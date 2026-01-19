from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.billing.models import Folio, FolioCharge, Payment, ChargeCode
from .serializers import (
    FolioSerializer, ChargeCodeSerializer,
    AddChargeSerializer, AddPaymentSerializer
)


class FolioDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FolioSerializer
    queryset = Folio.objects.all()


class ChargeCodeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChargeCodeSerializer
    
    def get_queryset(self):
        qs = ChargeCode.objects.filter(is_active=True)
        
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        
        return qs.order_by('category', 'name')


class AddChargeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            folio = Folio.objects.get(pk=pk)
        except Folio.DoesNotExist:
            return Response({'error': 'Folio not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AddChargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            charge_code = ChargeCode.objects.get(pk=data['charge_code_id'])
        except ChargeCode.DoesNotExist:
            return Response({'error': 'Charge code not found'}, status=status.HTTP_404_NOT_FOUND)
        
        charge = FolioCharge.objects.create(
            folio=folio,
            charge_code=charge_code,
            description=data.get('description', charge_code.name),
            quantity=data.get('quantity', 1),
            unit_price=data['unit_price'],
            posted_by=request.user
        )
        
        # Recalculate folio totals
        folio.recalculate_totals()
        
        return Response(FolioSerializer(folio).data)


class AddPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            folio = Folio.objects.get(pk=pk)
        except Folio.DoesNotExist:
            return Response({'error': 'Folio not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AddPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        payment = Payment.objects.create(
            folio=folio,
            payment_method=data['payment_method'],
            amount=data['amount'],
            reference_number=data.get('reference_number', ''),
            card_last_four=data.get('card_last_four', ''),
            received_by=request.user
        )
        
        # Recalculate folio totals
        folio.recalculate_totals()
        
        return Response(FolioSerializer(folio).data)


class CloseFolioView(APIView):
    """Close a folio (only when balance is zero)."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        from django.utils import timezone
        
        folio = get_object_or_404(Folio, pk=pk)
        
        # Check if folio balance is zero
        if folio.balance > 0:
            return Response(
                {'error': 'Cannot close folio with outstanding balance'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Close the folio
        folio.status = 'CLOSED'
        folio.closed_at = timezone.now()
        folio.closed_by = request.user
        folio.save()
        
        return Response(FolioSerializer(folio).data)


class FolioExportView(APIView):
    """Export folio as PDF."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        from django.http import HttpResponse
        
        folio = get_object_or_404(Folio, pk=pk)
        
        # TODO: Implement actual PDF generation (e.g., using reportlab)
        # For now, return JSON representation
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="folio_{folio.folio_number}.json"'
        
        import json
        data = FolioSerializer(folio).data
        response.write(json.dumps(data, indent=2))
        
        return response


class InvoiceDetailView(generics.RetrieveAPIView):
    """Get invoice detail."""
    permission_classes = [IsAuthenticated]
    queryset = None
    
    def get(self, request, pk):
        from apps.billing.models import Invoice
        from .serializers import InvoiceSerializer
        
        try:
            invoice = Invoice.objects.get(pk=pk)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(InvoiceSerializer(invoice).data)


class InvoicePayView(APIView):
    """Process invoice payment."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        from apps.billing.models import Invoice
        
        try:
            invoice = Invoice.objects.get(pk=pk)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method', 'CASH')
        
        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create payment record
        payment = Payment.objects.create(
            folio=invoice.folio if hasattr(invoice, 'folio') else None,
            payment_method=payment_method,
            amount=amount,
            reference_number=request.data.get('reference_number', ''),
            processed_by=request.user,
            status='COMPLETED'
        )
        
        # Update invoice
        invoice.paid_amount = (invoice.paid_amount or 0) + float(amount)
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = 'PAID'
        else:
            invoice.status = 'PARTIAL'
        invoice.save()
        
        from .serializers import InvoiceSerializer
        return Response(InvoiceSerializer(invoice).data)


class PaymentDetailView(generics.RetrieveAPIView):
    """Get payment detail."""
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.all()
    
    def get(self, request, pk):
        from .serializers import PaymentSerializer
        
        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(PaymentSerializer(payment).data)


class InvoiceListView(generics.ListCreateAPIView):
    """List all invoices and create new ones."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from apps.billing.models import Invoice
        from .serializers import InvoiceSerializer
        
        invoices = Invoice.objects.all().order_by('-created_at')
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            invoices = invoices.filter(status=status_filter)
        
        return Response(InvoiceSerializer(invoices, many=True).data)
    
    def post(self, request):
        from apps.billing.models import Invoice
        from .serializers import InvoiceSerializer
        
        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            invoice = serializer.save()
            return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentListView(generics.ListAPIView):
    """List all payments."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from .serializers import PaymentSerializer
        
        payments = Payment.objects.all().order_by('-payment_date')
        
        # Apply filters
        folio_id = request.query_params.get('folio')
        if folio_id:
            payments = payments.filter(folio_id=folio_id)
        
        return Response(PaymentSerializer(payments, many=True).data)
