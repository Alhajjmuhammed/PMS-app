from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group, Permission
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit
import secrets

from apps.accounts.mfa_utils import MFAManager
from api.permissions import CanManageUsers, IsAdminOrManager
from .serializers import (
    LoginSerializer, MFAVerifySerializer, UserSerializer, ChangePasswordSerializer,
    UserManagementSerializer, PermissionSerializer, RoleSerializer
)

User = get_user_model()


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=False), name='dispatch')
class LoginView(APIView):
    """
    User login endpoint with MFA enforcement.
    
    Returns:
        - If MFA is not enabled: Returns auth token immediately
        - If MFA is enabled: Returns mfa_required=True and temporary mfa_token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Check if rate limited
        if getattr(request, 'limited', False):
            return Response(
                {'error': 'Too many login attempts. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if user:
            # Reject login if the user's assigned property is deactivated
            if (
                user.assigned_property is not None
                and not user.assigned_property.is_active
            ):
                return Response(
                    {'error': 'Your property is inactive. Please contact the administrator.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if MFA is enabled for this user
            if user.mfa_enabled:
                # Generate temporary MFA session token
                mfa_token = secrets.token_urlsafe(32)
                
                # Store user ID in cache for 5 minutes
                cache_key = f"mfa_session:{mfa_token}"
                cache.set(cache_key, user.id, timeout=300)  # 5 minutes
                
                # Send MFA code based on user's MFA method
                if user.mfa_method == 'TOTP':
                    # TOTP doesn't need to send anything, user has app
                    mfa_message = "Enter the 6-digit code from your authenticator app"
                elif user.mfa_method == 'EMAIL':
                    # Send email with code
                    code = MFAManager.generate_email_code(user.email)
                    MFAManager.send_email_code(user.email, code)
                    mfa_message = f"A 6-digit code has been sent to {user.email}"
                elif user.mfa_method == 'SMS':
                    # Send SMS with code
                    code = MFAManager.generate_sms_code(user.phone)
                    MFAManager.send_sms_code(user.phone, code)
                    mfa_message = f"A 6-digit code has been sent to {user.phone}"
                else:
                    mfa_message = "MFA is enabled. Please enter your verification code."
                
                return Response({
                    'mfa_required': True,
                    'mfa_token': mfa_token,
                    'mfa_method': user.mfa_method,
                    'message': mfa_message
                }, status=status.HTTP_200_OK)
            
            # No MFA - proceed with normal login
            token, created = Token.objects.get_or_create(user=user)
            # Always update token.created to reset expiration on login (sliding window)
            token.created = timezone.now()
            token.save(update_fields=['created'])
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=False), name='dispatch')
class MFAVerifyView(APIView):
    """
    Verify MFA code and complete login.
    
    Requires:
        - mfa_token: Temporary session token from login response
        - mfa_code: 6-digit verification code
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Check if rate limited
        if getattr(request, 'limited', False):
            return Response(
                {'error': 'Too many verification attempts. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        serializer = MFAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        mfa_token = serializer.validated_data['mfa_token']
        mfa_code = serializer.validated_data['mfa_code']
        
        # Get user ID from cache
        cache_key = f"mfa_session:{mfa_token}"
        user_id = cache.get(cache_key)
        
        if not user_id:
            return Response(
                {'error': 'Invalid or expired MFA session. Please log in again.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify the MFA code based on method
        is_valid = False
        
        if user.mfa_method == 'TOTP':
            is_valid = MFAManager.verify_totp_code(user.mfa_secret, mfa_code)
        elif user.mfa_method == 'EMAIL':
            is_valid = MFAManager.verify_email_code(user.email, mfa_code)
        elif user.mfa_method == 'SMS':
            is_valid = MFAManager.verify_sms_code(user.phone, mfa_code)
        
        # Also check backup codes
        if not is_valid and user.mfa_backup_codes:
            is_valid = MFAManager.verify_backup_code(user, mfa_code)
            if is_valid:
                # Backup code was used - save the updated list
                user.save(update_fields=['mfa_backup_codes'])
        
        if is_valid:
            # Delete the MFA session from cache
            cache.delete(cache_key)
            
            # Create auth token
            token, created = Token.objects.get_or_create(user=user)
            token.created = timezone.now()
            token.save(update_fields=['created'])
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        
        return Response(
            {'error': 'Invalid verification code'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not request.user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        # Invalidate the current auth token so the client must log in again
        try:
            request.user.auth_token.delete()
        except Token.DoesNotExist:
            pass

        return Response({'message': 'Password changed successfully. Please log in again.'})


class UserListCreateView(generics.ListCreateAPIView):
    """List and create users (admin only)."""
    permission_classes = [IsAuthenticated, CanManageUsers]
    serializer_class = UserManagementSerializer

    def perform_create(self, serializer):
        # Non-superadmins can only create users in their own property.
        if not self.request.user.is_superuser and self.request.user.assigned_property:
            serializer.save(assigned_property=self.request.user.assigned_property)
        else:
            serializer.save()

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')

        # Superadmin sees everyone; others see only their property
        if not self.request.user.is_superuser and self.request.user.assigned_property:
            queryset = queryset.filter(assigned_property=self.request.user.assigned_property)

        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a user (admin only)."""
    permission_classes = [IsAuthenticated, CanManageUsers]
    serializer_class = UserManagementSerializer

    def perform_update(self, serializer):
        # Non-superadmins cannot move a user to a different property.
        if not self.request.user.is_superuser and self.request.user.assigned_property:
            serializer.save(assigned_property=self.request.user.assigned_property)
        else:
            serializer.save()

    def get_queryset(self):
        qs = User.objects.all()
        if not self.request.user.is_superuser and self.request.user.assigned_property:
            qs = qs.filter(assigned_property=self.request.user.assigned_property)
        return qs


class PermissionListView(APIView):
    """List all available permissions."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get all permissions
        permissions = Permission.objects.select_related('content_type').all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)


class RoleListCreateView(APIView):
    """List and create roles (groups)."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get(self, request):
        groups = Group.objects.prefetch_related('permissions').all()
        data = []
        for group in groups:
            data.append({
                'id': group.id,
                'name': group.name,
                'description': '',  # Groups don't have description by default
                'permissions': [{
                    'id': p.id,
                    'name': p.name,
                    'codename': p.codename
                } for p in group.permissions.all()]
            })
        return Response(data)
    
    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create group
        group = Group.objects.create(name=serializer.validated_data['name'])
        
        # Add permissions
        permission_ids = serializer.validated_data.get('permissions', [])
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            group.permissions.set(permissions)
        
        return Response({
            'id': group.id,
            'name': group.name,
            'description': '',
            'permissions': [{
                'id': p.id,
                'name': p.name,
                'codename': p.codename
            } for p in group.permissions.all()]
        }, status=status.HTTP_201_CREATED)


class RoleDetailView(APIView):
    """Retrieve, update, or delete a role (group)."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get(self, request, pk):
        try:
            group = Group.objects.prefetch_related('permissions').get(pk=pk)
            return Response({
                'id': group.id,
                'name': group.name,
                'description': '',
                'permissions': [{
                    'id': p.id,
                    'name': p.name,
                    'codename': p.codename
                } for p in group.permissions.all()]
            })
        except Group.DoesNotExist:
            return Response(
                {'error': 'Role not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def patch(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response(
                {'error': 'Role not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update group
        if 'name' in serializer.validated_data:
            group.name = serializer.validated_data['name']
            group.save()
        
        # Update permissions
        if 'permissions' in serializer.validated_data:
            permission_ids = serializer.validated_data['permissions']
            permissions = Permission.objects.filter(id__in=permission_ids)
            group.permissions.set(permissions)
        
        return Response({
            'id': group.id,
            'name': group.name,
            'description': '',
            'permissions': [{
                'id': p.id,
                'name': p.name,
                'codename': p.codename
            } for p in group.permissions.all()]
        })
    
    def delete(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
            group.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Group.DoesNotExist:
            return Response(
                {'error': 'Role not found'},
                status=status.HTTP_404_NOT_FOUND
            )
