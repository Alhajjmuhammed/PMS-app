from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.billing.models import Folio, FolioCharge, Payment, ChargeCode
from api.permissions import IsAccountantOrAbove
from .serializers import (
    FolioSerializer, FolioListSerializer, FolioCreateSerializer,
    ChargeCodeSerializer, ChargeCodeCreateSerializer,
    AddChargeSerializer, AddPaymentSerializer
)


class FolioListCreateView(generics.ListCreateAPIView):
    """List all folios or create a new folio."""
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'folio_type', 'guest']
    search_fields = ['folio_number', 'guest__first_name', 'guest__last_name']
    ordering_fields = ['open_date', 'folio_number', 'total_charges', 'balance']
    ordering = ['-open_date']
    
    def get_queryset(self):
        return Folio.objects.select_related('guest', 'reservation', 'company').all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FolioCreateSerializer
        return FolioListSerializer


class FolioDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a folio."""
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    serializer_class = FolioSerializer
    
    def get_queryset(self):
        return Folio.objects.select_related('guest', 'reservation', 'company') \
                           .prefetch_related('charges', 'payments')


class ChargeCodeListCreateView(generics.ListCreateAPIView):
    """List all charge codes or create a new one."""
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['code', 'name']
    
    def get_queryset(self):
        qs = ChargeCode.objects.all()
        
        # Filter active only by default
        show_all = self.request.query_params.get('show_all')
        if not show_all:
            qs = qs.filter(is_active=True)
        
        return qs.order_by('category', 'name')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChargeCodeCreateSerializer
        return ChargeCodeSerializer


class ChargeCodeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a charge code."""
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    serializer_class = ChargeCodeCreateSerializer
    queryset = ChargeCode.objects.all()


class AddChargeView(APIView):
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
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
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
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
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
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
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
    def get(self, request, pk):
        from django.http import HttpResponse
        from io import BytesIO
        
        folio = get_object_or_404(Folio.objects.select_related(
            'reservation__guest',
            'reservation__hotel'
        ).prefetch_related(
            'charges__charge_code',
            'payments'
        ), pk=pk)
        
        # Generate PDF
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            elements.append(Paragraph(f"Invoice - {folio.folio_number}", title_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # Guest Info
            guest_data = [
                ['Guest:', f"{folio.reservation.guest.first_name} {folio.reservation.guest.last_name}"],
                ['Email:', folio.reservation.guest.email or 'N/A'],
                ['Check-in:', folio.reservation.check_in_date.strftime('%Y-%m-%d')],
                ['Check-out:', folio.reservation.check_out_date.strftime('%Y-%m-%d')],
            ]
            guest_table = Table(guest_data, colWidths=[1.5*inch, 4*inch])
            guest_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(guest_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Charges Table
            charge_data = [['Date', 'Description', 'Quantity', 'Amount']]
            for charge in folio.charges.all():
                charge_data.append([
                    charge.date.strftime('%Y-%m-%d'),
                    charge.description,
                    str(charge.quantity),
                    f"${charge.amount:.2f}"
                ])
            
            charge_table = Table(charge_data, colWidths=[1*inch, 3*inch, 1*inch, 1.5*inch])
            charge_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(charge_table)
            elements.append(Spacer(1, 0.2*inch))
            
            # Totals
            totals_data = [
                ['Subtotal:', f"${folio.total_charges:.2f}"],
                ['Taxes:', f"${folio.total_tax:.2f}"],
                ['Total:', f"${folio.total_amount:.2f}"],
                ['Paid:', f"${folio.paid_amount:.2f}"],
                ['Balance:', f"${folio.balance:.2f}"]
            ]
            totals_table = Table(totals_data, colWidths=[4.5*inch, 1.5*inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
                ('TOPPADDING', (0, -1), (-1, -1), 10),
            ]))
            elements.append(totals_table)
            
            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="folio_{folio.folio_number}.pdf"'
            return response
            
        except ImportError:
            # Fallback if reportlab not installed
            response = HttpResponse(content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="folio_{folio.folio_number}.json"'
            import json
            data = FolioSerializer(folio).data
            response.write(json.dumps(data, indent=2))
            return response


class InvoiceDetailView(generics.RetrieveAPIView):
    """Get invoice detail."""
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    serializer_class = None
    
    def get_queryset(self):
        from apps.billing.models import Invoice
        # Return empty queryset for swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Invoice.objects.none()
        return Invoice.objects.all()
    
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
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
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
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
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
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
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
