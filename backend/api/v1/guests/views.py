from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404
from apps.guests.models import Guest, GuestDocument, Company
from api.permissions import IsFrontDeskOrAbove
from .serializers import (
    GuestSerializer, GuestCreateSerializer, GuestDocumentSerializer,
    CompanySerializer, CompanyListSerializer
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
