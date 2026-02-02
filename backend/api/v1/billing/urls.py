from django.urls import path
from . import views
from . import cashier_shift_views

app_name = 'billing'

urlpatterns = [
    # Folio endpoints
    path('folios/', views.FolioListCreateView.as_view(), name='folio_list'),
    path('folios/<int:pk>/', views.FolioDetailView.as_view(), name='folio_detail'),
    path('folios/<int:pk>/charges/', views.AddChargeView.as_view(), name='add_charge'),
    path('folios/<int:pk>/payments/', views.AddPaymentView.as_view(), name='add_payment'),
    path('folios/<int:pk>/close/', views.CloseFolioView.as_view(), name='close_folio'),
    path('folios/<int:pk>/export/', views.FolioExportView.as_view(), name='export_folio'),
    
    # Charge Code endpoints
    path('charge-codes/', views.ChargeCodeListCreateView.as_view(), name='charge_codes'),
    path('charge-codes/<int:pk>/', views.ChargeCodeDetailView.as_view(), name='charge_code_detail'),
    
    # Invoice endpoints
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/pay/', views.InvoicePayView.as_view(), name='invoice_pay'),
    
    # Payment endpoints
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    
    # Cashier Shift endpoints
    path('cashier-shifts/', cashier_shift_views.CashierShiftListView.as_view(), name='shift_list'),
    path('cashier-shifts/<int:pk>/', cashier_shift_views.CashierShiftDetailView.as_view(), name='shift_detail'),
    path('cashier-shifts/open/', cashier_shift_views.OpenCashierShiftView.as_view(), name='shift_open'),
    path('cashier-shifts/<int:pk>/close/', cashier_shift_views.CloseCashierShiftView.as_view(), name='shift_close'),
    path('cashier-shifts/<int:pk>/reconcile/', cashier_shift_views.ReconcileCashierShiftView.as_view(), name='shift_reconcile'),
    path('cashier-shifts/<int:pk>/summary/', cashier_shift_views.CashierShiftSummaryView.as_view(), name='shift_summary'),
    path('cashier-shifts/current/', cashier_shift_views.CurrentShiftView.as_view(), name='shift_current'),
]

