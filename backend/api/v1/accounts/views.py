from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.accounts.models import StaffProfile, ActivityLog
from .serializers import (
    StaffProfileSerializer,
    StaffProfileCreateSerializer,
    ActivityLogSerializer,
    ActivityLogCreateSerializer
)
from api.permissions import IsAdminOrManager


class StaffProfileListCreateView(generics.ListCreateAPIView):
    """List all staff profiles or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user__role', 'user__department', 'user__assigned_property']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'employee_id', 'job_title']
    ordering_fields = ['hire_date', 'user__first_name', 'employee_id']
    ordering = ['-hire_date']
    
    def get_queryset(self):
        queryset = StaffProfile.objects.select_related(
            'user',
            'user__department',
            'user__assigned_property'
        ).filter(user__assigned_property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StaffProfileCreateSerializer
        return StaffProfileSerializer


class StaffProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a staff profile."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get_queryset(self):
        return StaffProfile.objects.select_related(
            'user',
            'user__department',
            'user__assigned_property'
        ).filter(user__assigned_property=self.request.user.assigned_property)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return StaffProfileCreateSerializer
        return StaffProfileSerializer


class StaffProfileByDepartmentView(generics.ListAPIView):
    """Get staff profiles by department."""
    permission_classes = [IsAuthenticated]
    serializer_class = StaffProfileSerializer
    
    def get_queryset(self):
        department_id = self.kwargs.get('department_id')
        return StaffProfile.objects.select_related(
            'user',
            'user__department',
            'user__assigned_property'
        ).filter(
            user__assigned_property=self.request.user.assigned_property,
            user__department_id=department_id
        )


class StaffProfileByRoleView(generics.ListAPIView):
    """Get staff profiles by role."""
    permission_classes = [IsAuthenticated]
    serializer_class = StaffProfileSerializer
    
    def get_queryset(self):
        role = self.kwargs.get('role')
        return StaffProfile.objects.select_related(
            'user',
            'user__department',
            'user__assigned_property'
        ).filter(
            user__assigned_property=self.request.user.assigned_property,
            user__role=role
        )


class ActivityLogListCreateView(generics.ListCreateAPIView):
    """List all activity logs or create a new one."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'action', 'model_name']
    search_fields = ['description', 'model_name', 'object_id']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        queryset = ActivityLog.objects.select_related('user').filter(
            user__assigned_property=self.request.user.assigned_property
        )
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ActivityLogCreateSerializer
        return ActivityLogSerializer
    
    def perform_create(self, serializer):
        # Auto-capture IP and user agent
        request = self.request
        serializer.save(
            user=request.user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ActivityLogDetailView(generics.RetrieveAPIView):
    """Retrieve a single activity log entry."""
    permission_classes = [IsAuthenticated]
    serializer_class = ActivityLogSerializer
    
    def get_queryset(self):
        return ActivityLog.objects.select_related('user').filter(
            user__assigned_property=self.request.user.assigned_property
        )


class ActivityLogByUserView(generics.ListAPIView):
    """Get activity logs for a specific user."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = ActivityLogSerializer
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return ActivityLog.objects.select_related('user').filter(
            user__assigned_property=self.request.user.assigned_property,
            user_id=user_id
        ).order_by('-timestamp')


class ActivityLogExportView(APIView):
    """Export activity logs to JSON."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get(self, request):
        queryset = ActivityLog.objects.select_related('user').filter(
            user__assigned_property=request.user.assigned_property
        )
        
        # Apply filters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        user_id = request.query_params.get('user')
        action = request.query_params.get('action')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action:
            queryset = queryset.filter(action=action)
        
        serializer = ActivityLogSerializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'logs': serializer.data
        })
