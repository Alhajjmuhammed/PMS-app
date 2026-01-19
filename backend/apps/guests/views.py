from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from .models import Guest, GuestPreference, GuestDocument, Company, LoyaltyTransaction
from .forms import GuestForm, GuestPreferenceForm, CompanyForm


class GuestListView(LoginRequiredMixin, ListView):
    model = Guest
    template_name = 'guests/guest_list.html'
    context_object_name = 'guests'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = Guest.objects.all()
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        guest_type = self.request.GET.get('type')
        if guest_type:
            queryset = queryset.filter(guest_type=guest_type)
        
        return queryset


class GuestDetailView(LoginRequiredMixin, DetailView):
    model = Guest
    template_name = 'guests/guest_detail.html'
    context_object_name = 'guest'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['preferences'] = self.object.preferences.all()
        context['documents'] = self.object.documents.all()
        context['reservations'] = self.object.reservations.all()[:10]
        context['loyalty_transactions'] = self.object.loyalty_transactions.all()[:10]
        return context


class GuestCreateView(LoginRequiredMixin, CreateView):
    model = Guest
    form_class = GuestForm
    template_name = 'guests/guest_form.html'
    success_url = reverse_lazy('guests:guest_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Guest profile created successfully.')
        return super().form_valid(form)


class GuestUpdateView(LoginRequiredMixin, UpdateView):
    model = Guest
    form_class = GuestForm
    template_name = 'guests/guest_form.html'
    
    def get_success_url(self):
        return reverse_lazy('guests:guest_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Guest profile updated successfully.')
        return super().form_valid(form)


class GuestSearchView(LoginRequiredMixin, View):
    """AJAX guest search."""
    
    def get(self, request):
        query = request.GET.get('q', '')
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        guests = Guest.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )[:10]
        
        results = [{
            'id': g.id,
            'name': g.full_name,
            'email': g.email,
            'phone': g.phone,
        } for g in guests]
        
        return JsonResponse({'results': results})


class GuestHistoryView(LoginRequiredMixin, View):
    """Guest stay history."""
    template_name = 'guests/guest_history.html'
    
    def get(self, request, pk):
        guest = get_object_or_404(Guest, pk=pk)
        reservations = guest.reservations.all().order_by('-check_in_date')
        
        context = {
            'guest': guest,
            'reservations': reservations,
        }
        return render(request, self.template_name, context)


class GuestPreferenceListView(LoginRequiredMixin, ListView):
    model = GuestPreference
    template_name = 'guests/preference_list.html'
    context_object_name = 'preferences'
    
    def get_queryset(self):
        self.guest = get_object_or_404(Guest, pk=self.kwargs['guest_pk'])
        return GuestPreference.objects.filter(guest=self.guest)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guest'] = self.guest
        return context


class GuestPreferenceCreateView(LoginRequiredMixin, CreateView):
    model = GuestPreference
    form_class = GuestPreferenceForm
    template_name = 'guests/preference_form.html'
    
    def form_valid(self, form):
        guest = get_object_or_404(Guest, pk=self.kwargs['guest_pk'])
        form.instance.guest = guest
        messages.success(self.request, 'Preference added.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('guests:preference_list', kwargs={'guest_pk': self.kwargs['guest_pk']})


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'guests/company_list.html'
    context_object_name = 'companies'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Company.objects.all()
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
        
        company_type = self.request.GET.get('type')
        if company_type:
            queryset = queryset.filter(company_type=company_type)
        
        return queryset


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'guests/company_detail.html'
    context_object_name = 'company'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guests'] = self.object.guests.all()[:20]
        context['reservations'] = self.object.reservations.all()[:10]
        return context


class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'guests/company_form.html'
    success_url = reverse_lazy('guests:company_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Company created successfully.')
        return super().form_valid(form)


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'guests/company_form.html'
    
    def get_success_url(self):
        return reverse_lazy('guests:company_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Company updated successfully.')
        return super().form_valid(form)


class LoyaltyDashboardView(LoginRequiredMixin, View):
    """Loyalty program dashboard."""
    template_name = 'guests/loyalty_dashboard.html'
    
    def get(self, request):
        from .models import LoyaltyProgram
        
        programs = LoyaltyProgram.objects.filter(is_active=True)
        top_members = Guest.objects.filter(
            loyalty_number__isnull=False
        ).order_by('-loyalty_points')[:20]
        
        context = {
            'programs': programs,
            'top_members': top_members,
        }
        return render(request, self.template_name, context)


class LoyaltyTransactionListView(LoginRequiredMixin, ListView):
    model = LoyaltyTransaction
    template_name = 'guests/loyalty_transactions.html'
    context_object_name = 'transactions'
    paginate_by = 50
    
    def get_queryset(self):
        self.guest = get_object_or_404(Guest, pk=self.kwargs['guest_pk'])
        return LoyaltyTransaction.objects.filter(guest=self.guest)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guest'] = self.guest
        return context
