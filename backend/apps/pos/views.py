from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Outlet, MenuCategory, MenuItem, POSOrder, POSOrderItem


class POSDashboardView(LoginRequiredMixin, View):
    template_name = 'pos/dashboard.html'
    
    def get(self, request):
        outlets = Outlet.objects.filter(is_active=True)
        if request.user.property:
            outlets = outlets.filter(property=request.user.property)
        
        open_orders = POSOrder.objects.filter(status=POSOrder.Status.OPEN).count()
        
        context = {
            'outlets': outlets,
            'open_orders': open_orders,
        }
        return render(request, self.template_name, context)


class OutletListView(LoginRequiredMixin, ListView):
    model = Outlet
    template_name = 'pos/outlet_list.html'
    context_object_name = 'outlets'


class OutletDetailView(LoginRequiredMixin, DetailView):
    model = Outlet
    template_name = 'pos/outlet_detail.html'
    context_object_name = 'outlet'


class OrderListView(LoginRequiredMixin, ListView):
    model = POSOrder
    template_name = 'pos/order_list.html'
    context_object_name = 'orders'
    paginate_by = 30


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = POSOrder
    template_name = 'pos/order_detail.html'
    context_object_name = 'order'


class OrderCreateView(LoginRequiredMixin, View):
    template_name = 'pos/order_create.html'
    
    def get(self, request):
        outlets = Outlet.objects.filter(is_active=True)
        if request.user.property:
            outlets = outlets.filter(property=request.user.property)
        
        context = {'outlets': outlets}
        return render(request, self.template_name, context)
    
    def post(self, request):
        outlet = get_object_or_404(Outlet, pk=request.POST.get('outlet'))
        
        order = POSOrder.objects.create(
            outlet=outlet,
            room_number=request.POST.get('room_number', ''),
            guest_name=request.POST.get('guest_name', ''),
            table_number=request.POST.get('table_number', ''),
            server=request.user
        )
        
        messages.success(request, f'Order {order.order_number} created.')
        return redirect('pos:order_detail', pk=order.pk)


class PostToRoomView(LoginRequiredMixin, View):
    def post(self, request, pk):
        from apps.billing.models import Folio, FolioCharge, ChargeCode
        from apps.frontdesk.models import CheckIn
        
        order = get_object_or_404(POSOrder, pk=pk)
        
        # Find the guest's folio
        check_in = CheckIn.objects.filter(
            room__room_number=order.room_number,
            check_out__isnull=True
        ).first()
        
        if check_in and check_in.reservation.folio:
            folio = check_in.reservation.folio
            charge_code = ChargeCode.objects.filter(category='FOOD').first()
            
            FolioCharge.objects.create(
                folio=folio,
                charge_code=charge_code,
                description=f"POS: {order.outlet.name} - {order.order_number}",
                quantity=1,
                unit_price=order.total,
                posted_by=request.user
            )
            
            order.is_posted_to_room = True
            order.posted_at = timezone.now()
            order.check_in = check_in
            order.status = POSOrder.Status.CLOSED
            order.save()
            
            messages.success(request, 'Order posted to room folio.')
        else:
            messages.error(request, 'Could not find guest folio.')
        
        return redirect('pos:order_detail', pk=pk)


class MenuView(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = 'pos/menu.html'
    context_object_name = 'items'
