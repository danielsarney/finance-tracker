from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.subscription_list, name='subscription_list'),
    path('create/', views.subscription_create, name='subscription_create'),
    path('<int:pk>/', views.subscription_detail, name='subscription_detail'),
    path('<int:pk>/edit/', views.subscription_update, name='subscription_update'),
    path('<int:pk>/delete/', views.subscription_delete, name='subscription_delete'),
]
