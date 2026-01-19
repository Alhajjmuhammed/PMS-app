from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group, Permission
from .serializers import (
    LoginSerializer, UserSerializer, ChangePasswordSerializer,
    UserManagementSerializer, PermissionSerializer, RoleSerializer
)

User = get_user_model()


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        
        return Response(
            {'error': 'Invalid credentials'},
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
        
        return Response({'message': 'Password changed successfully'})


class UserListCreateView(generics.ListCreateAPIView):
    """List and create users (admin only)."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserManagementSerializer
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        
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
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserManagementSerializer
    queryset = User.objects.all()


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
    permission_classes = [IsAuthenticated, IsAdminUser]
    
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
    permission_classes = [IsAuthenticated, IsAdminUser]
    
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
