from django.urls import path
from . import views

urlpatterns = [
    # Charity
    path(
        "donations/<int:donation_id>/request/",
        views.request_pickup,
        name="request_pickup",
    ),
    path("my-requests/", views.my_pickup_requests, name="my_pickup_requests"),
    path(
        "my-requests/<int:request_id>/confirm/",
        views.confirm_delivery,
        name="confirm_delivery",
    ),

    # Donor
    path("donor-requests/", views.manage_pickup_requests, name="manage_pickup_requests"),
    path(
        "donor-requests/<int:request_id>/decide/",
        views.decide_pickup_request,
        name="decide_pickup_request",
    ),
    path(
        "donor-requests/<int:request_id>/complete/",
        views.complete_pickup,
        name="complete_pickup",
    ),

    # Volunteer
    path("volunteer-dashboard/", views.volunteer_dashboard, name="volunteer_dashboard"),
    path(
        "volunteer-tasks/<int:request_id>/accept/",
        views.accept_delivery,
        name="accept_delivery",
    ),
    path(
        "volunteer-tasks/<int:request_id>/update/",
        views.update_delivery_status,
        name="update_delivery_status",
    ),
]