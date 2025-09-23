from django.urls import path
from . import views

app_name = "twofa"

urlpatterns = [
    path("setup/", views.setup_twofa, name="setup"),
    path("verify/", views.verify_twofa, name="verify"),
    path("status/", views.twofa_status, name="status"),
    path("verify-ajax/", views.verify_twofa_ajax, name="verify_ajax"),
    path("logout/", views.logout_view, name="logout"),
]
