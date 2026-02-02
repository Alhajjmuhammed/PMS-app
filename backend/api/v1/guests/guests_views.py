"""
Views for Guests Enhanced Module
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q, Count, Sum

from apps.guests.models import (
    GuestPreference, GuestDocument, Company,
    LoyaltyProgram, LoyaltyTier, LoyaltyTransaction, Guest
)
from .guests_serializers import (
    GuestPreferenceSerializer,
    GuestDocumentSerializer,
    CompanySerializer,
    LoyaltyProgramSerializer,
    LoyaltyTierSerializer,
    LoyaltyTransactionSerializer,
    GuestLoyaltySerializer
)
from api.permissions import IsAdminOrManager


# ===== Guest Preferences =====

class GuestPreferenceListCreateView(generics.ListCreateAPIView):
    """List all guest preferences or create new preference."""
    permission_classes = [IsAuthenticated]
    serializer_class = GuestPreferenceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['guest', 'category']
    search_fields = ['preference', 'notes']
    
    def get_queryset(self):
        return GuestPreference.objects.all().select_related('guest')


class GuestPreferenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a guest preference."""
    permission_classes = [IsAuthenticated]
    serializer_class = GuestPreferenceSerializer
    
    def get_queryset(self):
        return GuestPreference.objects.all().select_related('guest')


class GuestPreferencesByGuestView(generics.ListAPIView):
    """Get preferences for a specific guest."""
    permission_classes = [IsAuthenticated]
    serializer_class = GuestPreferenceSerializer
    
    def get_queryset(self):
        guest_id = self.kwargs.get('guest_id')
        return GuestPreference.objects.filter(guest_id=guest_id)


# ===== Guest Documents =====

class GuestDocumentListCreateView(generics.ListCreateAPIView):
    """List all guest documents or create new document."""
    permission_classes = [IsAuthenticated]
    serializer_class = GuestDocumentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['guest', 'document_type']
    search_fields = ['document_number', 'issuing_country']
    ordering_fields = ['issue_date', 'expiry_date']
    ordering = ['-issue_date']
    
    def get_queryset(self):
        return GuestDocument.objects.all().select_related('guest')


class GuestDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a guest document."""
    permission_classes = [IsAuthenticated]
    serializer_class = GuestDocumentSerializer
    
    def get_queryset(self):
        return GuestDocument.objects.all().select_related('guest')


class GuestDocumentsByGuestView(generics.ListAPIView):
    """Get documents for a specific guest."""
    permission_classes = [IsAuthenticated]
    serializer_class = GuestDocumentSerializer
    
    def get_queryset(self):
        guest_id = self.kwargs.get('guest_id')
        return GuestDocument.objects.filter(guest_id=guest_id).order_by('-issue_date')


# ===== Companies =====

class CompanyListCreateView(generics.ListCreateAPIView):
    """List all companies or create new company."""
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company_type', 'is_active']
    search_fields = ['name', 'code', 'contact_person', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        return Company.objects.all().prefetch_related('guests')


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a company."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = CompanySerializer
    
    def get_queryset(self):
        return Company.objects.all()


class ActiveCompaniesView(generics.ListAPIView):
    """List active companies."""
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']
    
    def get_queryset(self):
        return Company.objects.filter(is_active=True).order_by('name')


# ===== Loyalty Programs =====

class LoyaltyProgramListCreateView(generics.ListCreateAPIView):
    """List all loyalty programs or create new program."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = LoyaltyProgramSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_queryset(self):
        return LoyaltyProgram.objects.filter(
            property=self.request.user.property
        ).prefetch_related('tiers')
    
    def perform_create(self, serializer):
        serializer.save(property=self.request.user.property)


class LoyaltyProgramDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a loyalty program."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = LoyaltyProgramSerializer
    
    def get_queryset(self):
        return LoyaltyProgram.objects.filter(
            property=self.request.user.property
        )


class ActiveLoyaltyProgramsView(generics.ListAPIView):
    """List active loyalty programs."""
    permission_classes = [IsAuthenticated]
    serializer_class = LoyaltyProgramSerializer
    
    def get_queryset(self):
        return LoyaltyProgram.objects.filter(
            property=self.request.user.property,
            is_active=True
        )


# ===== Loyalty Tiers =====

class LoyaltyTierListCreateView(generics.ListCreateAPIView):
    """List all loyalty tiers or create new tier."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = LoyaltyTierSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['program']
    ordering = ['min_points']
    
    def get_queryset(self):
        return LoyaltyTier.objects.filter(
            program__property=self.request.user.property
        ).select_related('program')


class LoyaltyTierDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a loyalty tier."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = LoyaltyTierSerializer
    
    def get_queryset(self):
        return LoyaltyTier.objects.filter(
            program__property=self.request.user.property
        ).select_related('program')


class LoyaltyTiersByProgramView(generics.ListAPIView):
    """Get tiers for a specific program."""
    permission_classes = [IsAuthenticated]
    serializer_class = LoyaltyTierSerializer
    
    def get_queryset(self):
        program_id = self.kwargs.get('program_id')
        return LoyaltyTier.objects.filter(
            program_id=program_id,
            program__property=self.request.user.property
        ).order_by('min_points')


# ===== Loyalty Transactions =====

class LoyaltyTransactionListCreateView(generics.ListCreateAPIView):
    """List all loyalty transactions or create new transaction."""
    permission_classes = [IsAuthenticated]
    serializer_class = LoyaltyTransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['guest', 'transaction_type']
    search_fields = ['description', 'reference']
    ordering_fields = ['created_at', 'points']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return LoyaltyTransaction.objects.all().select_related('guest')


class LoyaltyTransactionDetailView(generics.RetrieveAPIView):
    """Retrieve a loyalty transaction."""
    permission_classes = [IsAuthenticated]
    serializer_class = LoyaltyTransactionSerializer
    
    def get_queryset(self):
        return LoyaltyTransaction.objects.all().select_related('guest')


class LoyaltyTransactionsByGuestView(generics.ListAPIView):
    """Get transactions for a specific guest."""
    permission_classes = [IsAuthenticated]
    serializer_class = LoyaltyTransactionSerializer
    
    def get_queryset(self):
        guest_id = self.kwargs.get('guest_id')
        return LoyaltyTransaction.objects.filter(
            guest_id=guest_id
        ).order_by('-created_at')


# ===== Loyalty Actions =====

class EarnLoyaltyPointsView(APIView):
    """Earn loyalty points for a guest."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, guest_id):
        try:
            guest = Guest.objects.get(id=guest_id)
            
            points = request.data.get('points')
            description = request.data.get('description', 'Points earned')
            reference = request.data.get('reference', '')
            
            if not points or points <= 0:
                return Response(
                    {'error': 'Points must be a positive number'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create transaction
            transaction = LoyaltyTransaction.objects.create(
                guest=guest,
                transaction_type='EARN',
                points=points,
                description=description,
                reference=reference,
                balance_after=guest.loyalty_points + points
            )
            
            # Update guest balance
            guest.loyalty_points += points
            guest.save()
            
            serializer = LoyaltyTransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Guest.DoesNotExist:
            return Response(
                {'error': 'Guest not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class RedeemLoyaltyPointsView(APIView):
    """Redeem loyalty points for a guest."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, guest_id):
        try:
            guest = Guest.objects.get(id=guest_id)
            
            points = request.data.get('points')
            description = request.data.get('description', 'Points redeemed')
            reference = request.data.get('reference', '')
            
            if not points or points <= 0:
                return Response(
                    {'error': 'Points must be a positive number'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if guest.loyalty_points < points:
                return Response(
                    {'error': 'Insufficient loyalty points'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create transaction (negative points)
            transaction = LoyaltyTransaction.objects.create(
                guest=guest,
                transaction_type='REDEEM',
                points=-points,
                description=description,
                reference=reference,
                balance_after=guest.loyalty_points - points
            )
            
            # Update guest balance
            guest.loyalty_points -= points
            guest.save()
            
            serializer = LoyaltyTransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Guest.DoesNotExist:
            return Response(
                {'error': 'Guest not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class GuestLoyaltyDashboardView(APIView):
    """Get loyalty dashboard for a guest."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, guest_id):
        try:
            guest = Guest.objects.get(id=guest_id)
            
            # Calculate totals
            transactions = LoyaltyTransaction.objects.filter(guest=guest)
            earned = transactions.filter(transaction_type='EARN').aggregate(
                total=Sum('points')
            )['total'] or 0
            redeemed = transactions.filter(transaction_type='REDEEM').aggregate(
                total=Sum('points')
            )['total'] or 0
            
            # Get recent transactions
            recent = transactions.order_by('-created_at')[:10]
            
            data = {
                'guest_id': guest.id,
                'guest_name': guest.full_name,
                'loyalty_number': guest.loyalty_number or '',
                'loyalty_tier': guest.loyalty_tier or '',
                'loyalty_points': guest.loyalty_points,
                'total_earned': earned,
                'total_redeemed': abs(redeemed),
                'recent_transactions': LoyaltyTransactionSerializer(recent, many=True).data
            }
            
            serializer = GuestLoyaltySerializer(data)
            return Response(serializer.data)
            
        except Guest.DoesNotExist:
            return Response(
                {'error': 'Guest not found'},
                status=status.HTTP_404_NOT_FOUND
            )
