from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db.models import Sum, Q

from apps.billing.models import CashierShift, Payment
from .cashier_shift_serializers import (
    CashierShiftSerializer,
    CashierShiftOpenSerializer,
    CashierShiftCloseSerializer,
    CashierShiftReconcileSerializer
)
from api.permissions import IsAdminOrManager


class CashierShiftListView(generics.ListAPIView):
    """List all cashier shifts."""
    permission_classes = [IsAuthenticated]
    serializer_class = CashierShiftSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'is_balanced']
    ordering_fields = ['shift_start', 'shift_end']
    ordering = ['-shift_start']
    
    def get_queryset(self):
        queryset = CashierShift.objects.select_related(
            'user',
            'property'
        ).filter(property=self.request.user.assigned_property)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(shift_start__gte=start_date)
        if end_date:
            queryset = queryset.filter(shift_start__lte=end_date)
        
        # Filter open/closed
        is_open = self.request.query_params.get('is_open')
        if is_open == 'true':
            queryset = queryset.filter(shift_end__isnull=True)
        elif is_open == 'false':
            queryset = queryset.filter(shift_end__isnull=False)
        
        return queryset


class CashierShiftDetailView(generics.RetrieveAPIView):
    """Retrieve a cashier shift."""
    permission_classes = [IsAuthenticated]
    serializer_class = CashierShiftSerializer
    
    def get_queryset(self):
        return CashierShift.objects.select_related(
            'user',
            'property'
        ).filter(property=self.request.user.assigned_property)


class OpenCashierShiftView(APIView):
    """Open a new cashier shift."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Check if user already has an open shift
        open_shift = CashierShift.objects.filter(
            user=request.user,
            shift_end__isnull=True
        ).first()
        
        if open_shift:
            return Response(
                {'error': 'You already have an open shift.', 'shift_id': open_shift.id},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CashierShiftOpenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        shift = serializer.save()
        
        return Response(
            CashierShiftSerializer(shift).data,
            status=status.HTTP_201_CREATED
        )


class CloseCashierShiftView(APIView):
    """Close a cashier shift."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            shift = CashierShift.objects.get(
                pk=pk,
                property=request.user.assigned_property
            )
        except CashierShift.DoesNotExist:
            return Response(
                {'error': 'Shift not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if shift.shift_end:
            return Response(
                {'error': 'Shift is already closed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if shift.user != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You can only close your own shift'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CashierShiftCloseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Close the shift
        shift.shift_end = timezone.now()
        shift.closing_balance = serializer.validated_data['closing_balance']
        
        # Calculate expected closing
        expected_closing = shift.opening_balance + shift.total_cash_received + shift.total_card_received
        shift.variance = shift.closing_balance - expected_closing
        shift.is_balanced = abs(shift.variance) < 1  # Within $1 tolerance
        
        if serializer.validated_data.get('notes'):
            shift.notes = serializer.validated_data['notes']
        
        shift.save()
        
        return Response(CashierShiftSerializer(shift).data)


class ReconcileCashierShiftView(APIView):
    """Reconcile cash and card transactions for a shift."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            shift = CashierShift.objects.get(
                pk=pk,
                property=request.user.assigned_property
            )
        except CashierShift.DoesNotExist:
            return Response(
                {'error': 'Shift not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CashierShiftReconcileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Calculate actual totals from payments
        cash_payments = Payment.objects.filter(
            payment_method='CASH',
            created_at__gte=shift.shift_start,
            created_at__lte=shift.shift_end if shift.shift_end else timezone.now(),
            folio__guest__property=request.user.assigned_property
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        card_payments = Payment.objects.filter(
            payment_method__in=['CREDIT_CARD', 'DEBIT_CARD'],
            created_at__gte=shift.shift_start,
            created_at__lte=shift.shift_end if shift.shift_end else timezone.now(),
            folio__guest__property=request.user.assigned_property
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        shift.total_cash_received = cash_payments
        shift.total_card_received = card_payments
        
        # Compare with actual counts
        actual_cash = serializer.validated_data['actual_cash']
        actual_card = serializer.validated_data['actual_card']
        
        cash_variance = actual_cash - cash_payments
        card_variance = actual_card - card_payments
        total_variance = cash_variance + card_variance
        
        if serializer.validated_data.get('notes'):
            shift.notes += f"\n\nReconciliation: {serializer.validated_data['notes']}"
        
        shift.save()
        
        return Response({
            'shift': CashierShiftSerializer(shift).data,
            'reconciliation': {
                'expected_cash': float(cash_payments),
                'actual_cash': float(actual_cash),
                'cash_variance': float(cash_variance),
                'expected_card': float(card_payments),
                'actual_card': float(actual_card),
                'card_variance': float(card_variance),
                'total_variance': float(total_variance)
            }
        })


class CurrentShiftView(APIView):
    """Get the current user's open shift."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        shift = CashierShift.objects.filter(
            user=request.user,
            shift_end__isnull=True
        ).select_related('property').first()
        
        if not shift:
            return Response(
                {'message': 'No open shift'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(CashierShiftSerializer(shift).data)


class CashierShiftSummaryView(APIView):
    """Get cashier shift summary for a specific shift."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            shift = CashierShift.objects.get(
                pk=pk,
                property=request.user.assigned_property
            )
        except CashierShift.DoesNotExist:
            return Response(
                {'error': 'Shift not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get payments during shift
        end_time = shift.shift_end if shift.shift_end else timezone.now()
        
        payments = Payment.objects.filter(
            created_at__gte=shift.shift_start,
            created_at__lte=end_time,
            folio__guest__property=request.user.assigned_property
        )
        
        total_payments = payments.count()
        total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        by_method = {}
        for method, label in Payment.PaymentMethod.choices:
            method_payments = payments.filter(payment_method=method)
            by_method[method] = {
                'label': label,
                'count': method_payments.count(),
                'amount': float(method_payments.aggregate(total=Sum('amount'))['total'] or 0)
            }
        
        return Response({
            'shift': CashierShiftSerializer(shift).data,
            'summary': {
                'total_payments': total_payments,
                'total_amount': float(total_amount),
                'by_method': by_method
            }
        })
