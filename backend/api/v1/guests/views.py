from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from apps.guests.models import Guest, GuestDocument, Company, LoyaltyProgram, LoyaltyTier, LoyaltyTransaction
from api.permissions import IsFrontDeskOrAbove
from .serializers import (
    GuestSerializer, GuestCreateSerializer, GuestDocumentSerializer,
    CompanySerializer, CompanyListSerializer,
    LoyaltyProgramSerializer, LoyaltyProgramCreateSerializer,
    LoyaltyTierSerializer, LoyaltyTransactionSerializer,
    LoyaltyTransactionCreateSerializer
)


class GuestListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = GuestSerializer
    queryset = Guest.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['nationality', 'is_blacklisted']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'id_number']
    ordering_fields = ['created_at', 'last_name', 'total_stays', 'total_revenue']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GuestCreateSerializer
        return GuestSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Custom filters
        vip_only = self.request.query_params.get('vip_only')
        if vip_only == 'true':
            qs = qs.exclude(vip_status='')
        
        return qs


class GuestDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = GuestSerializer
    
    def get_queryset(self):
        return Guest.objects.prefetch_related(
            'reservations',
            'documents',
            'preferences'
        )


class GuestCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = GuestCreateSerializer


class GuestSearchView(APIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        
        if len(query) < 2:
            return Response({'results': []})
        
        guests = Guest.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )[:20]
        
        return Response({
            'results': GuestSerializer(guests, many=True).data
        })


class GuestDocumentListView(generics.ListCreateAPIView):
    """List and upload guest documents."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = GuestDocumentSerializer
    
    def get_queryset(self):
        guest_id = self.kwargs.get('guest_id')
        return GuestDocument.objects.filter(guest_id=guest_id)
    
    def perform_create(self, serializer):
        guest_id = self.kwargs.get('guest_id')
        guest = get_object_or_404(Guest, pk=guest_id)
        serializer.save(guest=guest, uploaded_by=self.request.user)


class GuestDocumentDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a specific guest document."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = GuestDocumentSerializer
    queryset = GuestDocument.objects.all()
    lookup_url_kwarg = 'document_id'


class CompanyListCreateView(generics.ListCreateAPIView):
    """List all companies or create a new company."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    queryset = Company.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company_type', 'is_active']
    search_fields = ['name', 'code', 'contact_person', 'email']
    ordering_fields = ['name', 'created_at', 'credit_limit']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CompanyListSerializer
        return CompanySerializer


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a company."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    lookup_url_kwarg = 'pk'


# ============= Loyalty Program Views =============

class LoyaltyProgramListCreateView(generics.ListCreateAPIView):
    """List all loyalty programs or create a new one."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property', 'is_active']
    search_fields = ['name']
    ordering = ['-id']
    
    def get_queryset(self):
        queryset = LoyaltyProgram.objects.select_related('property').prefetch_related('tiers')
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LoyaltyProgramCreateSerializer
        return LoyaltyProgramSerializer


class LoyaltyProgramDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a loyalty program."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get_queryset(self):
        queryset = LoyaltyProgram.objects.select_related('property').prefetch_related('tiers')
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return LoyaltyProgramCreateSerializer
        return LoyaltyProgramSerializer


class LoyaltyTierListCreateView(generics.ListCreateAPIView):
    """List all loyalty tiers or create a new one."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = LoyaltyTierSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['program']
    ordering = ['min_points']
    
    def get_queryset(self):
        queryset = LoyaltyTier.objects.select_related('program')
        if self.request.user.assigned_property:
            queryset = queryset.filter(program__property=self.request.user.assigned_property)
        return queryset


class LoyaltyTierDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a loyalty tier."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = LoyaltyTierSerializer
    
    def get_queryset(self):
        queryset = LoyaltyTier.objects.select_related('program')
        if self.request.user.assigned_property:
            queryset = queryset.filter(program__property=self.request.user.assigned_property)
        return queryset


class LoyaltyTransactionListCreateView(generics.ListCreateAPIView):
    """List all loyalty transactions or create a new one."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['guest', 'transaction_type']
    search_fields = ['guest__first_name', 'guest__last_name', 'description', 'reference']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return LoyaltyTransaction.objects.select_related('guest')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LoyaltyTransactionCreateSerializer
        return LoyaltyTransactionSerializer


class LoyaltyTransactionDetailView(generics.RetrieveAPIView):
    """Retrieve a loyalty transaction."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = LoyaltyTransactionSerializer
    queryset = LoyaltyTransaction.objects.select_related('guest')


class GuestLoyaltyBalanceView(APIView):
    """Get guest's loyalty points balance."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get(self, request, guest_id):
        guest = get_object_or_404(Guest, pk=guest_id)
        
        # Get last transaction for current balance
        last_transaction = LoyaltyTransaction.objects.filter(
            guest=guest
        ).order_by('-created_at').first()
        
        balance = last_transaction.balance_after if last_transaction else 0
        
        # Get total earned and redeemed
        stats = LoyaltyTransaction.objects.filter(guest=guest).aggregate(
            total_earned=Sum('points', filter=Q(transaction_type='EARN')),
            total_redeemed=Sum('points', filter=Q(transaction_type='REDEEM'))
        )
        
        # Determine tier
        tier = None
        if balance > 0:
            tier_obj = LoyaltyTier.objects.filter(
                min_points__lte=balance
            ).order_by('-min_points').first()
            
            if tier_obj:
                tier = {
                    'name': tier_obj.name,
                    'min_points': tier_obj.min_points,
                    'discount_percentage': float(tier_obj.discount_percentage),
                    'benefits': tier_obj.benefits
                }
        
        return Response({
            'guest_id': guest.id,
            'guest_name': guest.full_name,
            'current_balance': balance,
            'total_earned': stats['total_earned'] or 0,
            'total_redeemed': abs(stats['total_redeemed'] or 0),
            'current_tier': tier,
            'recent_transactions': LoyaltyTransactionSerializer(
                LoyaltyTransaction.objects.filter(guest=guest)[:10],
                many=True
            ).data
        })
