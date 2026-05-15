from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from apps.maintenance.models import MaintenanceRequest, MaintenanceLog
from api.permissions import IsMaintenanceStaff
from .serializers import (
    MaintenanceRequestSerializer, MaintenanceRequestCreateSerializer,
    MaintenanceLogSerializer, RequestUpdateSerializer
)


class RequestListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMaintenanceStaff]
    serializer_class = MaintenanceRequestSerializer
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MaintenanceRequestCreateSerializer
        return MaintenanceRequestSerializer
    
    def get_queryset(self):
        qs = MaintenanceRequest.objects.select_related('room', 'assigned_to', 'reported_by')
        
        if self.request.user.assigned_property:
            qs = qs.filter(property=self.request.user.assigned_property)
        
        # MAINTENANCE role only sees their own tasks + unassigned pool
        from django.db.models import Q
        if self.request.user.role == 'MAINTENANCE':
            qs = qs.filter(
                Q(assigned_to=self.request.user) |
                Q(assigned_to__isnull=True, status='PENDING')
            )

        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        
        priority = self.request.query_params.get('priority')
        if priority:
            qs = qs.filter(priority=priority)
        
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(request_type=category)
        
        return qs.order_by('-priority', '-created_at')


class RequestDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsMaintenanceStaff]
    serializer_class = MaintenanceRequestSerializer
    
    def get_queryset(self):
        qs = MaintenanceRequest.objects.all()
        if self.request.user.assigned_property:
            qs = qs.filter(property=self.request.user.assigned_property)
        return qs
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return RequestUpdateSerializer
        return MaintenanceRequestSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        logs = MaintenanceLog.objects.filter(request=instance)
        
        return Response({
            'request': MaintenanceRequestSerializer(instance).data,
            'logs': MaintenanceLogSerializer(logs, many=True).data
        })


class RequestCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMaintenanceStaff]
    serializer_class = MaintenanceRequestCreateSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            property=self.request.user.assigned_property,
            reported_by=self.request.user
        )


class MyRequestsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMaintenanceStaff]
    serializer_class = MaintenanceRequestSerializer

    def get_queryset(self):
        qs = MaintenanceRequest.objects.filter(
            assigned_to=self.request.user,
            status__in=['PENDING', 'ASSIGNED', 'IN_PROGRESS']
        )
        if self.request.user.assigned_property:
            qs = qs.filter(property=self.request.user.assigned_property)
        return qs.order_by('-priority', '-created_at')


class AssignRequestView(APIView):
    permission_classes = [IsAuthenticated, IsMaintenanceStaff]
    
    def post(self, request, pk):
        prop = request.user.assigned_property
        try:
            req_qs = MaintenanceRequest.objects.all()
            if prop:
                req_qs = req_qs.filter(property=prop)
            maintenance_request = req_qs.get(pk=pk)
        except MaintenanceRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        assigned_to_id = request.data.get('assigned_to')
        if not assigned_to_id:
            return Response({'error': 'assigned_to is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user_qs = User.objects.filter(assigned_property=prop) if prop else User.objects.all()
            assigned_to = user_qs.get(pk=assigned_to_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        maintenance_request.assigned_to = assigned_to
        maintenance_request.status = 'ASSIGNED'
        
        with transaction.atomic():
            maintenance_request.save()
            MaintenanceLog.objects.create(
            request=maintenance_request,
            action='Assigned',
            notes=f'Assigned to {assigned_to.get_full_name()}',
            user=request.user
        )
        
        return Response(MaintenanceRequestSerializer(maintenance_request).data)


class StartRequestView(APIView):
    permission_classes = [IsAuthenticated, IsMaintenanceStaff]
    
    def post(self, request, pk):
        prop = request.user.assigned_property
        if not prop:
            return Response({'error': 'No property assigned'}, status=status.HTTP_403_FORBIDDEN)
        try:
            maintenance_request = MaintenanceRequest.objects.get(pk=pk, property=prop)
        except MaintenanceRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        maintenance_request.status = 'IN_PROGRESS'
        maintenance_request.started_at = timezone.now()
        
        with transaction.atomic():
            maintenance_request.save()
            MaintenanceLog.objects.create(
                request=maintenance_request,
                action='Started',
                notes='Work started',
                user=request.user
            )
            
            # Put room OOS if needed
            if maintenance_request.room and maintenance_request.priority in ['HIGH', 'EMERGENCY']:
                maintenance_request.room.status = 'OOS'
                maintenance_request.room.save()
        
        return Response(MaintenanceRequestSerializer(maintenance_request).data)


class CompleteRequestView(APIView):
    permission_classes = [IsAuthenticated, IsMaintenanceStaff]
    
    def post(self, request, pk):
        prop = request.user.assigned_property
        if not prop:
            return Response({'error': 'No property assigned'}, status=status.HTTP_403_FORBIDDEN)
        try:
            maintenance_request = MaintenanceRequest.objects.get(pk=pk, property=prop)
        except MaintenanceRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RequestUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        maintenance_request.status = 'COMPLETED'
        maintenance_request.completed_at = timezone.now()
        maintenance_request.resolution_notes = serializer.validated_data.get('notes', '')
        
        if 'actual_cost' in serializer.validated_data:
            maintenance_request.parts_cost = serializer.validated_data['actual_cost']
        
        with transaction.atomic():
            maintenance_request.save()
            MaintenanceLog.objects.create(
                request=maintenance_request,
                action='Completed',
                notes=maintenance_request.resolution_notes,
                user=request.user
            )
            
            # Return room to VD if it was OOS
            if maintenance_request.room and maintenance_request.room.status == 'OOS':
                maintenance_request.room.status = 'VD'
                maintenance_request.room.save()
        
        return Response(MaintenanceRequestSerializer(maintenance_request).data)


class RequestDetailViewAPI(generics.RetrieveAPIView):
    """Maintenance request detail view for /maintenance/{id}/ endpoint."""
    permission_classes = [IsAuthenticated, IsMaintenanceStaff]
    serializer_class = MaintenanceRequestSerializer
    
    def get_queryset(self):
        qs = MaintenanceRequest.objects.all()
        if self.request.user.assigned_property:
            qs = qs.filter(property=self.request.user.assigned_property)
        return qs


class ResolveRequestView(APIView):
    """Resolve/close maintenance request."""
    permission_classes = [IsAuthenticated, IsMaintenanceStaff]
    
    def post(self, request, pk):
        prop = request.user.assigned_property
        if not prop:
            return Response({'error': 'No property assigned'}, status=status.HTTP_403_FORBIDDEN)
        try:
            maintenance_request = MaintenanceRequest.objects.get(pk=pk, property=prop)
        except MaintenanceRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        notes = request.data.get('notes', '')
        
        maintenance_request.status = 'COMPLETED'
        maintenance_request.resolution_notes = notes
        maintenance_request.completed_at = timezone.now()
        
        with transaction.atomic():
            maintenance_request.save()
            MaintenanceLog.objects.create(
            request=maintenance_request,
            action='Resolved',
            notes=notes,
            user=request.user
        )
        
        return Response(MaintenanceRequestSerializer(maintenance_request).data)
