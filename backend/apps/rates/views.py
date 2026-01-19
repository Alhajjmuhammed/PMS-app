from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Season, RatePlan, RoomRate, DateRate, Package, Discount, YieldRule


class RateDashboardView(LoginRequiredMixin, View):
    template_name = 'rates/dashboard.html'
    
    def get(self, request):
        rate_plans = RatePlan.objects.filter(is_active=True)
        if request.user.property:
            rate_plans = rate_plans.filter(property=request.user.property)
        
        context = {
            'rate_plans': rate_plans[:10],
            'active_packages': Package.objects.filter(is_active=True).count(),
            'active_discounts': Discount.objects.filter(is_active=True).count(),
        }
        return render(request, self.template_name, context)


class RatePlanListView(LoginRequiredMixin, ListView):
    model = RatePlan
    template_name = 'rates/plan_list.html'
    context_object_name = 'plans'


class RatePlanDetailView(LoginRequiredMixin, DetailView):
    model = RatePlan
    template_name = 'rates/plan_detail.html'
    context_object_name = 'plan'


class RatePlanEditView(LoginRequiredMixin, View):
    template_name = 'rates/plan_edit.html'
    
    def get(self, request, pk):
        plan = get_object_or_404(RatePlan, pk=pk)
        room_rates = plan.room_rates.all()
        
        context = {
            'plan': plan,
            'room_rates': room_rates,
        }
        return render(request, self.template_name, context)


class SeasonListView(LoginRequiredMixin, ListView):
    model = Season
    template_name = 'rates/season_list.html'
    context_object_name = 'seasons'


class PackageListView(LoginRequiredMixin, ListView):
    model = Package
    template_name = 'rates/package_list.html'
    context_object_name = 'packages'


class DiscountListView(LoginRequiredMixin, ListView):
    model = Discount
    template_name = 'rates/discount_list.html'
    context_object_name = 'discounts'


class RateCalendarView(LoginRequiredMixin, View):
    template_name = 'rates/calendar.html'
    
    def get(self, request):
        from apps.rooms.models import RoomType
        
        room_types = RoomType.objects.filter(is_active=True)
        if request.user.property:
            room_types = room_types.filter(property=request.user.property)
        
        context = {
            'room_types': room_types,
        }
        return render(request, self.template_name, context)


class YieldRuleListView(LoginRequiredMixin, ListView):
    model = YieldRule
    template_name = 'rates/yield_rules.html'
    context_object_name = 'rules'
