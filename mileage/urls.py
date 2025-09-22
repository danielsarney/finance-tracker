from django.urls import path
from . import views

app_name = 'mileage'

urlpatterns = [
    path('', views.MileageLogListView.as_view(), name='mileage_list'),
    path('create/', views.MileageLogCreateView.as_view(), name='mileage_create'),
    path('<int:pk>/', views.MileageLogDetailView.as_view(), name='mileage_detail'),
    path('<int:pk>/edit/', views.MileageLogUpdateView.as_view(), name='mileage_edit'),
    path('<int:pk>/delete/', views.MileageLogDeleteView.as_view(), name='mileage_delete'),
    path('summary/', views.mileage_summary, name='mileage_summary'),
    path('api/calculate/', views.calculate_mileage_claim, name='calculate_claim'),
]
