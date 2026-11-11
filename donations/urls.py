from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("donations/create/", views.create_donation, name="create_donation"),
    path("donor-dashboard/", views.donor_dashboard, name="donor_dashboard"),
]