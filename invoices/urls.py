from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('create/', views.invoice_create, name='invoice_create'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('<int:pk>/download/', views.invoice_download_pdf, name='invoice_download_pdf'),
    path('get-available-worklogs/<int:client_id>/', views.get_available_worklogs, name='get_available_worklogs'),
]
