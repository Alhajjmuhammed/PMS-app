"""
Billing Business Logic Services

This module contains the core business logic for billing operations.
Separating business logic from views improves testability and maintainability.
"""

from decimal import Decimal
from typing import Dict, Any, Optional
from django.utils import timezone
from django.db import transaction
from .models import Folio, FolioCharge, Payment, ChargeCode


class BillingServiceError(Exception):
    """Base exception for billing service errors."""
    pass


class FolioClosedError(BillingServiceError):
    """Raised when attempting to modify a closed folio."""
    pass


class InsufficientBalanceError(BillingServiceError):
    """Raised when folio has outstanding balance."""
    pass


class BillingService:
    """Service class for billing operations."""
    
    @staticmethod
    @transaction.atomic
    def add_charge_to_folio(
        folio: Folio,
        charge_code: ChargeCode,
        unit_price: Decimal,
        quantity: int = 1,
        description: Optional[str] = None,
        posted_by = None
    ) -> FolioCharge:
        """
        Add a charge to a folio.
        
        Args:
            folio: The folio to add the charge to
            charge_code: The charge code to use
            unit_price: Price per unit
            quantity: Number of units (default: 1)
            description: Optional description (defaults to charge_code name)
            posted_by: User posting the charge
            
        Returns:
            The created FolioCharge instance
            
        Raises:
            FolioClosedError: If the folio is closed
        """
        if folio.status == 'CLOSED':
            raise FolioClosedError(f"Cannot add charges to closed folio {folio.folio_number}")
        
        # Calculate amount
        amount = unit_price * quantity
        
        # Create the charge
        charge = FolioCharge.objects.create(
            folio=folio,
            charge_code=charge_code,
            description=description or charge_code.name,
            quantity=quantity,
            unit_price=unit_price,
            amount=amount,
            posted_by=posted_by
        )
        
        # Recalculate folio totals
        folio.recalculate_totals()
        
        return charge
    
    @staticmethod
    @transaction.atomic
    def add_payment_to_folio(
        folio: Folio,
        amount: Decimal,
        payment_method: str,
        reference_number: str = '',
        card_last_four: str = '',
        received_by = None
    ) -> Payment:
        """
        Add a payment to a folio.
        
        Args:
            folio: The folio to add payment to
            amount: Payment amount
            payment_method: Payment method (CASH, CREDIT_CARD, etc.)
            reference_number: Optional reference/transaction number
            card_last_four: Last 4 digits of card (if card payment)
            received_by: User receiving the payment
            
        Returns:
            The created Payment instance
            
        Raises:
            FolioClosedError: If the folio is closed
            ValueError: If amount is invalid
        """
        if folio.status == 'CLOSED':
            raise FolioClosedError(f"Cannot add payments to closed folio {folio.folio_number}")
        
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        
        # Create the payment
        payment = Payment.objects.create(
            folio=folio,
            payment_method=payment_method,
            amount=amount,
            reference=reference_number,
            card_last_four=card_last_four,
            received_by=received_by
        )
        
        # Recalculate folio totals
        folio.recalculate_totals()
        
        return payment
    
    @staticmethod
    @transaction.atomic
    def close_folio(folio: Folio, closed_by = None) -> Folio:
        """
        Close a folio.
        
        Args:
            folio: The folio to close
            closed_by: User closing the folio
            
        Returns:
            The updated Folio instance
            
        Raises:
            InsufficientBalanceError: If folio has outstanding balance
            FolioClosedError: If folio is already closed
        """
        if folio.status == 'CLOSED':
            raise FolioClosedError(f"Folio {folio.folio_number} is already closed")
        
        # Check if balance is zero
        if folio.balance != 0:
            raise InsufficientBalanceError(
                f"Cannot close folio {folio.folio_number} with outstanding balance ${folio.balance}"
            )
        
        # Close the folio
        folio.status = 'CLOSED'
        folio.closed_at = timezone.now()
        folio.closed_by = closed_by
        folio.save()
        
        return folio
    
    @staticmethod
    def calculate_folio_totals(folio: Folio) -> Dict[str, Decimal]:
        """
        Calculate folio totals without saving.
        
        Args:
            folio: The folio to calculate totals for
            
        Returns:
            Dictionary with total_charges, total_payments, total_taxes, and balance
        """
        charges = folio.charges.all()
        payments = folio.payments.all()
        
        total_charges = sum((charge.amount for charge in charges), Decimal('0'))
        total_payments = sum((payment.amount for payment in payments), Decimal('0'))
        total_taxes = Decimal('0')  # Implement tax calculation logic as needed
        balance = total_charges + total_taxes - total_payments
        
        return {
            'total_charges': total_charges,
            'total_payments': total_payments,
            'total_taxes': total_taxes,
            'balance': balance
        }
    
    @staticmethod
    def get_folio_summary(folio: Folio) -> Dict[str, Any]:
        """
        Get a complete summary of a folio.
        
        Args:
            folio: The folio to summarize
            
        Returns:
            Dictionary with folio details, charges, payments, and totals
        """
        charges = list(folio.charges.select_related('charge_code').all())
        payments = list(folio.payments.all())
        
        return {
            'folio_number': folio.folio_number,
            'status': folio.status,
            'guest': {
                'name': f"{folio.guest.first_name} {folio.guest.last_name}",
                'email': folio.guest.email
            } if folio.guest else None,
            'charges': [
                {
                    'date': charge.charge_date,
                    'description': charge.description,
                    'quantity': charge.quantity,
                    'unit_price': charge.unit_price,
                    'amount': charge.amount
                }
                for charge in charges
            ],
            'payments': [
                {
                    'date': payment.payment_date,
                    'method': payment.payment_method,
                    'amount': payment.amount,
                    'reference': payment.reference
                }
                for payment in payments
            ],
            'totals': {
                'charges': folio.total_charges,
                'payments': folio.total_payments,
                'taxes': folio.total_taxes,
                'balance': folio.balance
            }
        }


class InvoiceService:
    """Service class for invoice operations."""
    
    @staticmethod
    @transaction.atomic
    def process_invoice_payment(
        invoice,
        amount: Decimal,
        payment_method: str,
        reference_number: str = '',
        received_by = None
    ):
        """
        Process a payment for an invoice.
        
        Args:
            invoice: The invoice to pay
            amount: Payment amount
            payment_method: Payment method
            reference_number: Optional reference number
            received_by: User receiving payment
            
        Returns:
            Tuple of (Payment, updated Invoice)
            
        Raises:
            ValueError: If amount is invalid
        """
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        
        # Create payment record
        payment = Payment.objects.create(
            folio=invoice.folio,
            payment_method=payment_method,
            amount=amount,
            reference=reference_number,
            received_by=received_by
        )
        
        # Update invoice status
        invoice.folio.recalculate_totals()
        total_paid = invoice.folio.total_payments
        
        if total_paid >= invoice.total:
            invoice.status = 'PAID'
        elif total_paid > 0:
            invoice.status = 'PARTIAL'
        
        invoice.save()
        
        return payment, invoice


class PDFService:
    """Service class for PDF generation."""
    
    @staticmethod
    def generate_folio_pdf(folio: Folio) -> bytes:
        """
        Generate a PDF invoice for a folio.
        
        Args:
            folio: The folio to generate PDF for
            
        Returns:
            PDF content as bytes
            
        Raises:
            ImportError: If reportlab is not installed
        """
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
        
        return buffer.getvalue()


# Convenience functions for backward compatibility and simpler imports
def add_charge_to_folio(*args, **kwargs):
    """Convenience function - delegates to BillingService."""
    return BillingService.add_charge_to_folio(*args, **kwargs)


def add_payment_to_folio(*args, **kwargs):
    """Convenience function - delegates to BillingService."""
    return BillingService.add_payment_to_folio(*args, **kwargs)


def close_folio(*args, **kwargs):
    """Convenience function - delegates to BillingService."""
    return BillingService.close_folio(*args, **kwargs)


def generate_folio_pdf(*args, **kwargs):
    """Convenience function - delegates to PDFService."""
    return PDFService.generate_folio_pdf(*args, **kwargs)


def process_invoice_payment(*args, **kwargs):
    """Convenience function - delegates to InvoiceService."""
    return InvoiceService.process_invoice_payment(*args, **kwargs)
