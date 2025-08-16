from django.urls import path
from . import views

app_name = 'work'

urlpatterns = [
    path('', views.worklog_list, name='worklog_list'),
    path('create/', views.worklog_create, name='worklog_create'),
    path('<int:pk>/', views.worklog_detail, name='worklog_detail'),
    path('<int:pk>/edit/', views.worklog_update, name='worklog_update'),
    path('<int:pk>/delete/', views.worklog_delete, name='worklog_delete'),
]
