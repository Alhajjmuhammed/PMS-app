from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from apps.billing.models import Folio, FolioCharge, Payment, ChargeCode
from apps.billing.services import (
    BillingService, InvoiceService, PDFService,
    BillingServiceError, FolioClosedError, InsufficientBalanceError
)
from api.permissions import IsAccountantOrAbove, CanViewBilling
from .serializers import (
    FolioSerializer, FolioListSerializer, FolioCreateSerializer,
    ChargeCodeSerializer, ChargeCodeCreateSerializer,
    AddChargeSerializer, AddPaymentSerializer
)


class FolioListCreateView(generics.ListCreateAPIView):
    """List all folios or create a new folio."""
    permission_classes = [IsAuthenticated, CanViewBilling]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'folio_type', 'guest']
    search_fields = ['folio_number', 'guest__first_name', 'guest__last_name']
    ordering_fields = ['open_date', 'folio_number', 'total_charges', 'balance']
    ordering = ['-open_date']
    
    def get_queryset(self):
        qs = Folio.objects.select_related('guest', 'reservation', 'company')
        prop = self.request.user.assigned_property
        if prop:
            qs = qs.filter(
                Q(reservation__hotel=prop) |
                Q(reservation__isnull=True, guest__home_property=prop)
            )
        return qs
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FolioCreateSerializer
        return FolioListSerializer
    
    def perform_create(self, serializer):
        prop = self.request.user.assigned_property
        if prop:
            from rest_framework.exceptions import ValidationError
            guest = serializer.validated_data.get('guest')
            if guest and guest.home_property_id and guest.home_property_id != prop.id:
                raise ValidationError({'guest': 'Guest does not belong to your property.'})
            reservation = serializer.validated_data.get('reservation')
            if reservation and reservation.hotel_id != prop.id:
                raise ValidationError({'reservation': 'Reservation does not belong to your property.'})
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Return full folio data (including id and folio_number) after creation
        full = FolioSerializer(serializer.instance, context={'request': request})
        return Response(full.data, status=status.HTTP_201_CREATED)


class FolioDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a folio."""
    permission_classes = [IsAuthenticated, CanViewBilling]
    serializer_class = FolioSerializer
    
    def get_queryset(self):
        qs = Folio.objects.select_related('guest', 'reservation', 'company') \
                          .prefetch_related('charges', 'payments')
        prop = self.request.user.assigned_property
        if prop:
            qs = qs.filter(
                Q(reservation__hotel=prop) |
                Q(reservation__isnull=True, guest__home_property=prop)
            )
        return qs


class ChargeCodeListCreateView(generics.ListCreateAPIView):
    """
    List all charge codes or create a new one.
    
    NOTE: Intentionally GLOBAL - ChargeCode is master data (Room Charge, Food,
    Minibar, Laundry, etc.) shared across all properties. These are standard
    billing categories used system-wide.
    """
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['code', 'name']
    
    def get_queryset(self):
        # Intentionally global - master billing codes
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
    """
    Retrieve, update or delete a charge code.
    
    NOTE: Intentionally GLOBAL - ChargeCode is master data shared system-wide.
    """
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    serializer_class = ChargeCodeCreateSerializer
    queryset = ChargeCode.objects.all()


class FolioChargesView(generics.ListAPIView):
    """List all charges for a specific folio."""
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
    def get_serializer_class(self):
        from .serializers import FolioChargeSerializer
        return FolioChargeSerializer
    
    def get_queryset(self):
        folio_id = self.kwargs.get('pk')
        qs = FolioCharge.objects.filter(folio_id=folio_id).select_related('charge_code', 'folio')
        prop = self.request.user.assigned_property
        if prop:
            qs = qs.filter(
                Q(folio__reservation__hotel=prop) |
                Q(folio__reservation__isnull=True, folio__guest__home_property=prop)
            )
        return qs.order_by('-charge_date')


class AddChargeView(APIView):
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
    def post(self, request, pk):
        prop = request.user.assigned_property
        try:
            folio_qs = Folio.objects.all()
            if prop:
                folio_qs = folio_qs.filter(
                    Q(reservation__hotel=prop) |
                    Q(reservation__isnull=True, guest__home_property=prop)
                )
            folio = folio_qs.get(pk=pk)
        except Folio.DoesNotExist:
            return Response({'error': 'Folio not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AddChargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            charge_code = ChargeCode.objects.get(pk=data['charge_code_id'])
        except ChargeCode.DoesNotExist:
            return Response({'error': 'Charge code not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Use service layer
        try:
            BillingService.add_charge_to_folio(
                folio=folio,
                charge_code=charge_code,
                unit_price=data['unit_price'],
                quantity=data.get('quantity', 1),
                description=data.get('description'),
                posted_by=request.user
            )
        except FolioClosedError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(FolioSerializer(folio).data)


class AddPaymentView(APIView):
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
    def post(self, request, pk):
        prop = request.user.assigned_property
        try:
            folio_qs = Folio.objects.all()
            if prop:
                folio_qs = folio_qs.filter(
                    Q(reservation__hotel=prop) |
                    Q(reservation__isnull=True, guest__home_property=prop)
                )
            folio = folio_qs.get(pk=pk)
        except Folio.DoesNotExist:
            return Response({'error': 'Folio not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AddPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Use service layer
        try:
            BillingService.add_payment_to_folio(
                folio=folio,
                amount=data['amount'],
                payment_method=data['payment_method'],
                reference_number=data.get('reference_number', ''),
                card_last_four=data.get('card_last_four', ''),
                received_by=request.user
            )
        except (FolioClosedError, ValueError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(FolioSerializer(folio).data)


class CloseFolioView(APIView):
    """Close a folio (only when balance is zero)."""
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
    def post(self, request, pk):
        prop = request.user.assigned_property
        if prop:
            folio_qs = Folio.objects.filter(
                Q(reservation__hotel=prop) |
                Q(reservation__isnull=True, guest__home_property=prop)
            )
        else:
            folio_qs = Folio.objects.all()
        folio = get_object_or_404(folio_qs, pk=pk)
        
        # Use service layer
        try:
            BillingService.close_folio(folio, closed_by=request.user)
        except (InsufficientBalanceError, FolioClosedError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(FolioSerializer(folio).data)


class FolioExportView(APIView):
    """Export folio as PDF."""
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
    def get(self, request, pk):
        from django.http import HttpResponse
        import json
        
        prop = request.user.assigned_property
        folio_qs = Folio.objects.select_related(
            'reservation__guest',
            'reservation__hotel'
        ).prefetch_related(
            'charges__charge_code',
            'payments'
        )
        if prop:
            folio_qs = folio_qs.filter(
                Q(reservation__hotel=prop) |
                Q(reservation__isnull=True, guest__home_property=prop)
            )
        folio = get_object_or_404(folio_qs, pk=pk)
        
        # Generate PDF using service layer
        try:
            from io import BytesIO
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
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
            reservation = folio.reservation
            if reservation and reservation.guest:
                guest_data = [
                    ['Guest:', f"{reservation.guest.first_name} {reservation.guest.last_name}"],
                    ['Email:', reservation.guest.email or 'N/A'],
                    ['Check-in:', reservation.check_in_date.strftime('%Y-%m-%d')],
                    ['Check-out:', reservation.check_out_date.strftime('%Y-%m-%d')],
                ]
            else:
                g = folio.guest
                guest_data = [
                    ['Guest:', f"{g.first_name} {g.last_name}"],
                    ['Email:', g.email or 'N/A'],
                    ['Folio:', folio.folio_number],
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
                    charge.charge_date.strftime('%Y-%m-%d'),
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
                ['Taxes:', f"${folio.total_taxes:.2f}"],
                ['Total:', f"${folio.total_charges + folio.total_taxes:.2f}"],
                ['Paid:', f"${folio.total_payments:.2f}"],
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
    
    def get_serializer_class(self):
        from .serializers import InvoiceSerializer
        return InvoiceSerializer
    
    def get_queryset(self):
        from apps.billing.models import Invoice
        # Return empty queryset for swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Invoice.objects.none()
        return Invoice.objects.all()
    
    def get(self, request, pk):
        from apps.billing.models import Invoice
        from .serializers import InvoiceSerializer
        prop = request.user.assigned_property
        invoice_qs = Invoice.objects.all()
        if prop:
            invoice_qs = invoice_qs.filter(folio__reservation__hotel=prop)
        try:
            invoice = invoice_qs.get(pk=pk)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(InvoiceSerializer(invoice).data)


class InvoicePayView(APIView):
    """Process invoice payment."""
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
    def post(self, request, pk):
        from apps.billing.models import Invoice
        from decimal import Decimal
        prop = request.user.assigned_property
        invoice_qs = Invoice.objects.all()
        if prop:
            invoice_qs = invoice_qs.filter(folio__reservation__hotel=prop)
        try:
            invoice = invoice_qs.get(pk=pk)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method', 'CASH')
        
        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use service layer
        try:
            payment, invoice = InvoiceService.process_invoice_payment(
                invoice=invoice,
                amount=Decimal(str(amount)),
                payment_method=payment_method,
                reference_number=request.data.get('reference_number', ''),
                received_by=request.user
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        from .serializers import InvoiceSerializer
        return Response(InvoiceSerializer(invoice).data)


class PaymentDetailView(generics.RetrieveAPIView):
    """Get payment detail."""
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
    def get_queryset(self):
        qs = Payment.objects.all()
        if self.request.user.assigned_property:
            qs = qs.filter(folio__reservation__hotel=self.request.user.assigned_property)
        return qs
    
    def get_serializer_class(self):
        from .serializers import PaymentSerializer
        return PaymentSerializer
    
    def get(self, request, pk):
        from .serializers import PaymentSerializer
        prop = request.user.assigned_property
        payment_qs = Payment.objects.all()
        if prop:
            payment_qs = payment_qs.filter(folio__reservation__hotel=prop)
        try:
            payment = payment_qs.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(PaymentSerializer(payment).data)


class InvoiceListView(generics.ListCreateAPIView):
    """List all invoices and create new ones."""
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
    def get_serializer_class(self):
        from .serializers import InvoiceSerializer
        return InvoiceSerializer
    
    def get(self, request):
        from apps.billing.models import Invoice
        from .serializers import InvoiceSerializer
        
        invoices = Invoice.objects.all().order_by('-created_at')
        if request.user.assigned_property:
            invoices = invoices.filter(folio__reservation__hotel=request.user.assigned_property)
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            invoices = invoices.filter(status=status_filter)
        
        return Response(InvoiceSerializer(invoices, many=True).data)
    
    def post(self, request):
        from apps.billing.models import Invoice, Folio
        from .serializers import InvoiceSerializer
        from django.db.models import Q
        
        prop = request.user.assigned_property
        folio_id = request.data.get('folio')
        if folio_id and prop:
            folio_qs = Folio.objects.filter(pk=folio_id).filter(
                Q(reservation__hotel=prop) | Q(guest__home_property=prop)
            )
            if not folio_qs.exists():
                return Response({'error': 'Folio not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            invoice = serializer.save()
            return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentListView(generics.ListAPIView):
    """List all payments."""
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    
    def get_serializer_class(self):
        from .serializers import PaymentSerializer
        return PaymentSerializer
    
    def get(self, request):
        from .serializers import PaymentSerializer
        
        payments = Payment.objects.all().order_by('-payment_date')
        
        # Filter by assigned property for multi-tenancy
        if request.user.assigned_property:
            payments = payments.filter(folio__reservation__hotel=request.user.assigned_property)
        
        # Apply additional filters
        folio_id = request.query_params.get('folio')
        if folio_id:
            payments = payments.filter(folio_id=folio_id)
        
        return Response(PaymentSerializer(payments, many=True).data)


class FolioChargeListView(generics.ListAPIView):
    """List all folio charges."""
    permission_classes = [IsAuthenticated, IsAccountantOrAbove]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['folio', 'charge_code', 'is_posted']
    search_fields = ['description', 'folio__folio_number']
    ordering_fields = ['charge_date', 'amount']
    ordering = ['-charge_date']
    
    def get_serializer_class(self):
        from .serializers import FolioChargeSerializer
        return FolioChargeSerializer
    
    def get_queryset(self):
        qs = FolioCharge.objects.select_related('folio', 'charge_code')
        if self.request.user.assigned_property:
            qs = qs.filter(folio__reservation__hotel=self.request.user.assigned_property)
        return qs
