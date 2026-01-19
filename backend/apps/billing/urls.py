from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.BillingDashboardView.as_view(), name='dashboard'),
    path('folios/', views.FolioListView.as_view(), name='folio_list'),
    path('folios/<int:pk>/', views.FolioDetailView.as_view(), name='folio_detail'),
    path('folios/<int:pk>/add-charge/', views.AddChargeView.as_view(), name='add_charge'),
    path('folios/<int:pk>/add-payment/', views.AddPaymentView.as_view(), name='add_payment'),
    path('folios/<int:pk>/invoice/', views.GenerateInvoiceView.as_view(), name='generate_invoice'),
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('cashier/', views.CashierView.as_view(), name='cashier'),
    path('cashier/shift/start/', views.StartShiftView.as_view(), name='start_shift'),
    path('cashier/shift/end/', views.EndShiftView.as_view(), name='end_shift'),
]
