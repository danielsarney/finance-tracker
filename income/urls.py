from django.urls import path
from . import views

app_name = "income"

urlpatterns = [
    path("", views.income_list, name="income_list"),
    path("create/", views.income_create, name="income_create"),
    path("<int:pk>/", views.income_detail, name="income_detail"),
    path("<int:pk>/edit/", views.income_update, name="income_update"),
    path("<int:pk>/delete/", views.income_delete, name="income_delete"),
]
