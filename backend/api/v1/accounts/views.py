from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.accounts.models import StaffProfile, ActivityLog
from apps.accounts.mfa_utils import MFAManager, EmailMFA, SMSMFA
from .serializers import (
    StaffProfileSerializer,
    StaffProfileCreateSerializer,
    ActivityLogSerializer,
    ActivityLogCreateSerializer,
    MFASetupSerializer,
    MFASetupResponseSerializer,
    MFAVerifySerializer,
    MFAEnableSerializer,
    MFALoginSerializer,
    UserMFAStatusSerializer,
)
from api.permissions import IsAdminOrManager

User = get_user_model()


# ===========================
# MFA Views
# ===========================

class MFASetupView(APIView):
    """
    Initiate MFA setup for current user.
    
    POST /api/v1/accounts/mfa/setup/
    Body: {"method": "TOTP|EMAIL|SMS"}
    
    Returns:
    - TOTP: secret, qr_code, backup_codes
    - EMAIL/SMS: backup_codes only (code sent to user)
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=MFASetupSerializer,
        responses={
            200: MFASetupResponseSerializer,
            400: "Invalid method or user already has MFA enabled"
        },
        operation_description="Initiate MFA setup. Returns secret and QR code for TOTP, or sends code for EMAIL/SMS."
    )
    def post(self, request):
        serializer = MFASetupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        method = serializer.validated_data['method']
        user = request.user
        
        if user.mfa_enabled:
            return Response(
                {'error': 'MFA already enabled. Disable first to change method.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate backup codes
        backup_codes = MFAManager.generate_backup_codes()
        
        response_data = {
            'method': method,
            'backup_codes': backup_codes
        }
        
        if method == 'TOTP':
            # Generate TOTP secret and QR code
            secret, uri = MFAManager.get_totp_uri(user)
            qr_code = MFAManager.generate_qr_code(uri)
            
            # Store secret temporarily (not enabled yet)
            user.mfa_secret = secret
            user.mfa_method = method
            user.backup_codes = backup_codes
            user.save(update_fields=['mfa_secret', 'mfa_method', 'backup_codes'])
            
            response_data['secret'] = secret
            response_data['qr_code'] = qr_code
            
        elif method == 'EMAIL':
            # Send email code
            if EmailMFA.send_code(user):
                user.mfa_method = method
                user.backup_codes = backup_codes
                user.save(update_fields=['mfa_method', 'backup_codes'])
                response_data['message'] = 'Verification code sent to your email'
            else:
                return Response(
                    {'error': 'Failed to send email code'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        elif method == 'SMS':
            # Send SMS code
            if not user.phone:
                return Response(
                    {'error': 'Phone number required for SMS authentication'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if SMSMFA.send_code(user):
                user.mfa_method = method
                user.backup_codes = backup_codes
                user.save(update_fields=['mfa_method', 'backup_codes'])
                response_data['message'] = 'Verification code sent to your phone'
            else:
                return Response(
                    {'error': 'Failed to send SMS code'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(response_data, status=status.HTTP_200_OK)


class MFAEnableView(APIView):
    """
    Enable MFA after verifying the setup code.
    
    POST /api/v1/accounts/mfa/enable/
    Body: {"code": "123456", "method": "TOTP|EMAIL|SMS"}
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=MFAEnableSerializer,
        responses={
            200: "MFA enabled successfully",
            400: "Invalid code or MFA already enabled"
        }
    )
    def post(self, request):
        serializer = MFAEnableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        code = serializer.validated_data['code']
        method = serializer.validated_data['method']
        
        if user.mfa_enabled:
            return Response(
                {'error': 'MFA already enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify code based on method
        valid = False
        if method == 'TOTP' and user.mfa_secret:
            valid = MFAManager.verify_totp_code(user.mfa_secret, code)
        elif method == 'EMAIL':
            valid = EmailMFA.verify_code(user, code)
        elif method == 'SMS':
            valid = SMSMFA.verify_code(user, code)
        
        if not valid:
            return Response(
                {'error': 'Invalid verification code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Enable MFA
        user.mfa_enabled = True
        user.save(update_fields=['mfa_enabled'])
        
        return Response({
            'message': 'MFA enabled successfully',
            'method': method
        }, status=status.HTTP_200_OK)


class MFADisableView(APIView):
    """
    Disable MFA for current user.
    
    POST /api/v1/accounts/mfa/disable/
    Body: {"code": "123456"}
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=MFAVerifySerializer,
        responses={
            200: "MFA disabled successfully",
            400: "Invalid code or MFA not enabled"
        }
    )
    def post(self, request):
        serializer = MFAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        code = serializer.validated_data['code']
        
        if not user.mfa_enabled:
            return Response(
                {'error': 'MFA not enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify code
        valid = False
        if user.mfa_method == 'TOTP':
            valid = MFAManager.verify_totp_code(user.mfa_secret, code)
        elif user.mfa_method == 'EMAIL':
            # Send new code first
            EmailMFA.send_code(user)
            valid = EmailMFA.verify_code(user, code)
        elif user.mfa_method == 'SMS':
            # Send new code first
            SMSMFA.send_code(user)
            valid = SMSMFA.verify_code(user, code)
        
        # Also check backup codes
        if not valid:
            valid = MFAManager.verify_backup_code(user, code)
        
        if not valid:
            return Response(
                {'error': 'Invalid verification code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Disable MFA
        user.mfa_enabled = False
        user.mfa_secret = ''
        user.backup_codes = []
        user.save(update_fields=['mfa_enabled', 'mfa_secret', 'backup_codes'])
        
        return Response({
            'message': 'MFA disabled successfully'
        }, status=status.HTTP_200_OK)


class MFAVerifyView(APIView):
    """
    Verify MFA code during login.
    
    POST /api/v1/accounts/mfa/verify/
    Body: {"code": "123456"}
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=MFAVerifySerializer,
        responses={
            200: "Code verified successfully",
            400: "Invalid code"
        }
    )
    def post(self, request):
        serializer = MFAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        code = serializer.validated_data['code']
        
        if not user.mfa_enabled:
            return Response(
                {'error': 'MFA not enabled for this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify code based on method
        valid = False
        if user.mfa_method == 'TOTP':
            valid = MFAManager.verify_totp_code(user.mfa_secret, code)
        elif user.mfa_method == 'EMAIL':
            valid = EmailMFA.verify_code(user, code)
        elif user.mfa_method == 'SMS':
            valid = SMSMFA.verify_code(user, code)
        
        # Check backup codes if regular code failed
        if not valid and len(code) == 8:
            valid = MFAManager.verify_backup_code(user, code)
            if valid:
                return Response({
                    'message': 'Backup code verified successfully',
                    'warning': f'You have {len(user.backup_codes)} backup codes remaining'
                }, status=status.HTTP_200_OK)
        
        if not valid:
            return Response(
                {'error': 'Invalid verification code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': 'Code verified successfully'
        }, status=status.HTTP_200_OK)


class MFAStatusView(APIView):
    """
    Get MFA status for current user.
    
    GET /api/v1/accounts/mfa/status/
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        responses={
            200: UserMFAStatusSerializer
        }
    )
    def get(self, request):
        serializer = UserMFAStatusSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MFAResendCodeView(APIView):
    """
    Resend MFA code (for EMAIL/SMS methods).
    
    POST /api/v1/accounts/mfa/resend/
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        responses={
            200: "Code resent successfully",
            400: "Invalid MFA method"
        }
    )
    def post(self, request):
        user = request.user
        
        if not user.mfa_enabled:
            return Response(
                {'error': 'MFA not enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.mfa_method == 'EMAIL':
            if EmailMFA.send_code(user):
                return Response({
                    'message': 'Verification code sent to your email'
                }, status=status.HTTP_200_OK)
        elif user.mfa_method == 'SMS':
            if SMSMFA.send_code(user):
                return Response({
                    'message': 'Verification code sent to your phone'
                }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Code resend not available for TOTP method'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {'error': 'Failed to send code'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ===========================
# Staff Profile Views
# ===========================

class StaffProfileListCreateView(generics.ListCreateAPIView):
    """List all staff profiles or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user__role', 'user__department', 'user__assigned_property']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'employee_id', 'job_title']
    ordering_fields = ['hire_date', 'user__first_name', 'employee_id']
    ordering = ['-hire_date']
    
    def get_queryset(self):
        qs = StaffProfile.objects.select_related(
            'user',
            'user__department',
            'user__assigned_property'
        )
        if self.request.user.is_superuser:
            return qs
        return qs.filter(user__assigned_property=self.request.user.assigned_property)
    
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
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = StaffProfileSerializer
    
    def get_queryset(self):
        department_id = self.kwargs.get('department_id')
        qs = StaffProfile.objects.select_related(
            'user', 'user__department', 'user__assigned_property'
        ).filter(user__department_id=department_id)
        if not self.request.user.is_superuser:
            qs = qs.filter(user__assigned_property=self.request.user.assigned_property)
        return qs


class StaffProfileByRoleView(generics.ListAPIView):
    """Get staff profiles by role."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = StaffProfileSerializer
    
    def get_queryset(self):
        role = self.kwargs.get('role')
        qs = StaffProfile.objects.select_related(
            'user', 'user__department', 'user__assigned_property'
        ).filter(user__role=role)
        if not self.request.user.is_superuser:
            qs = qs.filter(user__assigned_property=self.request.user.assigned_property)
        return qs


class ActivityLogListCreateView(generics.ListCreateAPIView):
    """List all activity logs or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'action', 'model_name']
    search_fields = ['description', 'model_name', 'object_id']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        qs = ActivityLog.objects.select_related('user')
        if not self.request.user.is_superuser:
            qs = qs.filter(user__assigned_property=self.request.user.assigned_property)

        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            qs = qs.filter(timestamp__gte=start_date)
        if end_date:
            qs = qs.filter(timestamp__lte=end_date)
        return qs
    
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
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = ActivityLogSerializer
    
    def get_queryset(self):
        qs = ActivityLog.objects.select_related('user')
        if self.request.user.is_superuser:
            return qs
        return qs.filter(user__assigned_property=self.request.user.assigned_property)


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
