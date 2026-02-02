"""
Views for Maintenance Module
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import date, timedelta

from apps.maintenance.models import MaintenanceRequest, Asset, MaintenanceLog
from apps.accounts.models import User
from apps.rooms.models import Room
from .maintenance_serializers import (
    MaintenanceRequestSerializer,
    AssetSerializer,
    MaintenanceLogSerializer,
    MaintenanceDashboardSerializer,
    MaintenanceRequestAssignSerializer
)
from api.permissions import IsAdminOrManager


# ===== Maintenance Requests =====

class MaintenanceRequestListCreateView(generics.ListCreateAPIView):
    """List all maintenance requests or create new request."""
    permission_classes = [IsAuthenticated]
    serializer_class = MaintenanceRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'request_type', 'assigned_to', 'room']
    search_fields = ['request_number', 'title', 'description', 'location']
    ordering_fields = ['created_at', 'priority', 'status', 'completed_at']
    ordering = ['-priority', 'created_at']
    
    def get_queryset(self):
        queryset = MaintenanceRequest.objects.filter(
            property=self.request.user.property
        ).select_related(
            'room', 'assigned_to', 'reported_by', 'property'
        ).prefetch_related('logs')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        # Generate request number
        last_request = MaintenanceRequest.objects.filter(
            property=self.request.user.property
        ).order_by('-id').first()
        
        if last_request:
            last_num = int(last_request.request_number.split('-')[-1])
            request_number = f"MR-{last_num + 1:06d}"
        else:
            request_number = "MR-000001"
        
        serializer.save(
            property=self.request.user.property,
            reported_by=self.request.user,
            request_number=request_number
        )


class MaintenanceRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a maintenance request."""
    permission_classes = [IsAuthenticated]
    serializer_class = MaintenanceRequestSerializer
    
    def get_queryset(self):
        return MaintenanceRequest.objects.filter(
            property=self.request.user.property
        ).select_related(
            'room', 'assigned_to', 'reported_by', 'property'
        ).prefetch_related('logs')


class PendingMaintenanceView(generics.ListAPIView):
    """List pending maintenance requests."""
    permission_classes = [IsAuthenticated]
    serializer_class = MaintenanceRequestSerializer
    
    def get_queryset(self):
        return MaintenanceRequest.objects.filter(
            property=self.request.user.property,
            status='PENDING'
        ).select_related('room', 'reported_by').order_by('-priority', 'created_at')


class MyMaintenanceTasksView(generics.ListAPIView):
    """List maintenance tasks assigned to current user."""
    permission_classes = [IsAuthenticated]
    serializer_class = MaintenanceRequestSerializer
    
    def get_queryset(self):
        return MaintenanceRequest.objects.filter(
            assigned_to=self.request.user,
            status__in=['ASSIGNED', 'IN_PROGRESS']
        ).select_related('room').order_by('-priority', 'created_at')


class EmergencyMaintenanceView(generics.ListAPIView):
    """List emergency maintenance requests."""
    permission_classes = [IsAuthenticated]
    serializer_class = MaintenanceRequestSerializer
    
    def get_queryset(self):
        return MaintenanceRequest.objects.filter(
            property=self.request.user.property,
            priority='EMERGENCY',
            status__in=['PENDING', 'ASSIGNED', 'IN_PROGRESS']
        ).select_related('room', 'assigned_to').order_by('created_at')


class AssignMaintenanceView(APIView):
    """Assign maintenance request to a technician."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        try:
            maintenance_request = MaintenanceRequest.objects.get(
                pk=pk,
                property=request.user.property
            )
            
            assigned_to_id = request.data.get('assigned_to')
            if not assigned_to_id:
                return Response(
                    {'error': 'assigned_to is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                assigned_to = User.objects.get(
                    id=assigned_to_id,
                    property=request.user.property
                )
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            maintenance_request.assigned_to = assigned_to
            maintenance_request.assigned_at = timezone.now()
            maintenance_request.status = 'ASSIGNED'
            maintenance_request.save()
            
            # Create log entry
            MaintenanceLog.objects.create(
                request=maintenance_request,
                action=f"Assigned to {assigned_to.get_full_name()}",
                user=request.user
            )
            
            serializer = MaintenanceRequestSerializer(maintenance_request)
            return Response(serializer.data)
            
        except MaintenanceRequest.DoesNotExist:
            return Response(
                {'error': 'Maintenance request not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class BulkAssignMaintenanceView(APIView):
    """Bulk assign multiple maintenance requests."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request):
        serializer = MaintenanceRequestAssignSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        assigned_to = User.objects.get(id=data['assigned_to'])
        
        requests = MaintenanceRequest.objects.filter(
            id__in=data['requests'],
            property=request.user.property
        )
        
        updated_count = 0
        for req in requests:
            req.assigned_to = assigned_to
            req.assigned_at = timezone.now()
            req.status = 'ASSIGNED'
            req.save()
            
            MaintenanceLog.objects.create(
                request=req,
                action=f"Bulk assigned to {assigned_to.get_full_name()}",
                user=request.user
            )
            updated_count += 1
        
        return Response({
            'message': f'Assigned {updated_count} requests to {assigned_to.get_full_name()}',
            'count': updated_count
        })


class StartMaintenanceView(APIView):
    """Start working on maintenance request."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            maintenance_request = MaintenanceRequest.objects.get(
                pk=pk,
                property=request.user.property
            )
            
            if maintenance_request.status not in ['PENDING', 'ASSIGNED']:
                return Response(
                    {'error': 'Request cannot be started'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            maintenance_request.status = 'IN_PROGRESS'
            maintenance_request.started_at = timezone.now()
            if not maintenance_request.assigned_to:
                maintenance_request.assigned_to = request.user
                maintenance_request.assigned_at = timezone.now()
            maintenance_request.save()
            
            MaintenanceLog.objects.create(
                request=maintenance_request,
                action="Work started",
                user=request.user
            )
            
            serializer = MaintenanceRequestSerializer(maintenance_request)
            return Response(serializer.data)
            
        except MaintenanceRequest.DoesNotExist:
            return Response(
                {'error': 'Maintenance request not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CompleteMaintenanceView(APIView):
    """Complete maintenance request."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            maintenance_request = MaintenanceRequest.objects.get(
                pk=pk,
                property=request.user.property
            )
            
            if maintenance_request.status == 'COMPLETED':
                return Response(
                    {'error': 'Request already completed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            resolution_notes = request.data.get('resolution_notes')
            if not resolution_notes:
                return Response(
                    {'error': 'resolution_notes is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            maintenance_request.status = 'COMPLETED'
            maintenance_request.completed_at = timezone.now()
            maintenance_request.resolution_notes = resolution_notes
            
            # Optional cost details
            parts_cost = request.data.get('parts_cost')
            labor_hours = request.data.get('labor_hours')
            
            if parts_cost is not None:
                maintenance_request.parts_cost = parts_cost
            if labor_hours is not None:
                maintenance_request.labor_hours = labor_hours
            
            maintenance_request.save()
            
            # Update room status if needed
            if maintenance_request.room and maintenance_request.room.status == 'OUT_OF_ORDER':
                maintenance_request.room.status = 'DIRTY'
                maintenance_request.room.save()
            
            MaintenanceLog.objects.create(
                request=maintenance_request,
                action="Work completed",
                notes=resolution_notes,
                user=request.user
            )
            
            serializer = MaintenanceRequestSerializer(maintenance_request)
            return Response(serializer.data)
            
        except MaintenanceRequest.DoesNotExist:
            return Response(
                {'error': 'Maintenance request not found'},
                status=status.HTTP_404_NOT_FOUND
            )


# ===== Assets =====

class AssetListCreateView(generics.ListCreateAPIView):
    """List all assets or create new asset."""
    permission_classes = [IsAuthenticated]
    serializer_class = AssetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'room', 'is_active']
    search_fields = ['name', 'code', 'brand', 'model', 'serial_number']
    ordering_fields = ['name', 'purchase_date', 'current_value']
    ordering = ['name']
    
    def get_queryset(self):
        return Asset.objects.filter(
            property=self.request.user.property
        ).select_related('room', 'property')
    
    def perform_create(self, serializer):
        serializer.save(property=self.request.user.property)


class AssetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an asset."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = AssetSerializer
    
    def get_queryset(self):
        return Asset.objects.filter(
            property=self.request.user.property
        ).select_related('room', 'property')


class AssetsByRoomView(generics.ListAPIView):
    """Get assets for a specific room."""
    permission_classes = [IsAuthenticated]
    serializer_class = AssetSerializer
    
    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        return Asset.objects.filter(
            room_id=room_id,
            property=self.request.user.property
        )


class AssetsDueMaintenanceView(generics.ListAPIView):
    """List assets due for maintenance."""
    permission_classes = [IsAuthenticated]
    serializer_class = AssetSerializer
    
    def get_queryset(self):
        today = date.today()
        return Asset.objects.filter(
            property=self.request.user.property,
            is_active=True,
            next_maintenance__lte=today
        ).order_by('next_maintenance')


# ===== Maintenance Logs =====

class MaintenanceLogListView(generics.ListAPIView):
    """List maintenance logs for a request."""
    permission_classes = [IsAuthenticated]
    serializer_class = MaintenanceLogSerializer
    
    def get_queryset(self):
        request_id = self.kwargs.get('request_id')
        return MaintenanceLog.objects.filter(
            request_id=request_id,
            request__property=self.request.user.property
        ).select_related('user', 'request').order_by('-timestamp')


class MaintenanceLogCreateView(generics.CreateAPIView):
    """Create a new maintenance log entry."""
    permission_classes = [IsAuthenticated]
    serializer_class = MaintenanceLogSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ===== Dashboard & Stats =====

class MaintenanceDashboardView(APIView):
    """Get maintenance dashboard statistics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db import models
        today = date.today()
        property_obj = request.user.property
        
        # Request statistics
        request_stats = MaintenanceRequest.objects.filter(
            property=property_obj
        ).aggregate(
            pending=Count('id', filter=Q(status='PENDING')),
            assigned=Count('id', filter=Q(status='ASSIGNED')),
            in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
            completed_today=Count('id', filter=Q(status='COMPLETED', completed_at__date=today)),
            emergency=Count('id', filter=Q(
                priority='EMERGENCY',
                status__in=['PENDING', 'ASSIGNED', 'IN_PROGRESS']
            ))
        )
        
        # Count overdue requests (emergency > 1h, high > 24h)
        one_hour_ago = timezone.now() - timedelta(hours=1)
        one_day_ago = timezone.now() - timedelta(days=1)
        
        overdue_emergency = MaintenanceRequest.objects.filter(
            property=property_obj,
            priority='EMERGENCY',
            status__in=['PENDING', 'ASSIGNED'],
            created_at__lt=one_hour_ago
        ).count()
        
        overdue_high = MaintenanceRequest.objects.filter(
            property=property_obj,
            priority='HIGH',
            status__in=['PENDING', 'ASSIGNED'],
            created_at__lt=one_day_ago
        ).count()
        
        overdue_requests = overdue_emergency + overdue_high
        
        # Asset statistics
        asset_stats = Asset.objects.filter(
            property=property_obj,
            is_active=True
        ).aggregate(
            total=Count('id'),
            due_maintenance=Count('id', filter=Q(next_maintenance__lte=today)),
            under_warranty=Count('id', filter=Q(warranty_expiry__gte=today))
        )
        
        # Average resolution time
        completed_requests = MaintenanceRequest.objects.filter(
            property=property_obj,
            status='COMPLETED',
            started_at__isnull=False,
            completed_at__isnull=False
        )
        
        avg_resolution = 0
        if completed_requests.exists():
            total_seconds = sum([
                (req.completed_at - req.started_at).total_seconds()
                for req in completed_requests[:100]  # Limit for performance
            ])
            avg_resolution = round(total_seconds / completed_requests.count() / 3600, 2)
        
        data = {
            'pending_requests': request_stats['pending'] or 0,
            'assigned_requests': request_stats['assigned'] or 0,
            'in_progress_requests': request_stats['in_progress'] or 0,
            'completed_today': request_stats['completed_today'] or 0,
            'emergency_requests': request_stats['emergency'] or 0,
            'overdue_requests': overdue_requests,
            'total_assets': asset_stats['total'] or 0,
            'assets_due_maintenance': asset_stats['due_maintenance'] or 0,
            'assets_under_warranty': asset_stats['under_warranty'] or 0,
            'avg_resolution_hours': avg_resolution
        }
        
        serializer = MaintenanceDashboardSerializer(data)
        return Response(serializer.data)
