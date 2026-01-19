from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Folio, FolioCharge, Payment, Invoice, CashierShift, ChargeCode
import uuid


class BillingDashboardView(LoginRequiredMixin, View):
    template_name = 'billing/dashboard.html'
    
    def get(self, request):
        today = timezone.now().date()
        
        open_folios = Folio.objects.filter(status=Folio.Status.OPEN).count()
        today_charges = FolioCharge.objects.filter(charge_date=today).aggregate(
            total=models.Sum('amount'))['total'] or 0
        today_payments = Payment.objects.filter(payment_date__date=today).aggregate(
            total=models.Sum('amount'))['total'] or 0
        
        context = {
            'open_folios': open_folios,
            'today_charges': today_charges,
            'today_payments': today_payments,
        }
        return render(request, self.template_name, context)


class FolioListView(LoginRequiredMixin, ListView):
    model = Folio
    template_name = 'billing/folio_list.html'
    context_object_name = 'folios'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Folio.objects.select_related('guest', 'reservation').all()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class FolioDetailView(LoginRequiredMixin, DetailView):
    model = Folio
    template_name = 'billing/folio_detail.html'
    context_object_name = 'folio'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['charges'] = self.object.charges.all()
        context['payments'] = self.object.payments.all()
        context['charge_codes'] = ChargeCode.objects.filter(is_active=True)
        return context


class AddChargeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        folio = get_object_or_404(Folio, pk=pk)
        charge_code = get_object_or_404(ChargeCode, pk=request.POST.get('charge_code'))
        
        FolioCharge.objects.create(
            folio=folio,
            charge_code=charge_code,
            description=request.POST.get('description', charge_code.name),
            quantity=request.POST.get('quantity', 1),
            unit_price=request.POST.get('unit_price', charge_code.default_amount),
            posted_by=request.user
        )
        
        messages.success(request, 'Charge added to folio.')
        return redirect('billing:folio_detail', pk=pk)


class AddPaymentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        folio = get_object_or_404(Folio, pk=pk)
        
        Payment.objects.create(
            folio=folio,
            payment_method=request.POST.get('payment_method'),
            amount=request.POST.get('amount'),
            reference=request.POST.get('reference', ''),
            received_by=request.user
        )
        
        messages.success(request, 'Payment recorded.')
        return redirect('billing:folio_detail', pk=pk)


class GenerateInvoiceView(LoginRequiredMixin, View):
    def post(self, request, pk):
        folio = get_object_or_404(Folio, pk=pk)
        
        invoice = Invoice.objects.create(
            invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
            folio=folio,
            bill_to_name=folio.guest.full_name,
            subtotal=folio.total_charges,
            tax_amount=folio.total_taxes,
            total=folio.balance,
            status=Invoice.Status.ISSUED
        )
        
        messages.success(request, f'Invoice {invoice.invoice_number} generated.')
        return redirect('billing:invoice_detail', pk=invoice.pk)


class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'billing/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 30


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'billing/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'billing/invoice_detail.html'
    context_object_name = 'invoice'


class CashierView(LoginRequiredMixin, View):
    template_name = 'billing/cashier.html'
    
    def get(self, request):
        current_shift = CashierShift.objects.filter(
            user=request.user,
            shift_end__isnull=True
        ).first()
        
        context = {'current_shift': current_shift}
        return render(request, self.template_name, context)


class StartShiftView(LoginRequiredMixin, View):
    def post(self, request):
        CashierShift.objects.create(
            user=request.user,
            property=request.user.property,
            shift_start=timezone.now(),
            opening_balance=request.POST.get('opening_balance', 0)
        )
        messages.success(request, 'Shift started.')
        return redirect('billing:cashier')


class EndShiftView(LoginRequiredMixin, View):
    def post(self, request):
        shift = CashierShift.objects.filter(
            user=request.user,
            shift_end__isnull=True
        ).first()
        
        if shift:
            shift.shift_end = timezone.now()
            shift.closing_balance = request.POST.get('closing_balance', 0)
            shift.save()
            messages.success(request, 'Shift ended.')
        
        return redirect('billing:cashier')
