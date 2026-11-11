
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from donations.models import Donation
from .models import PickupRequest


@login_required
def request_pickup(request, donation_id):
    if request.method != "POST":
        return redirect("home")

    if request.user.role != "CHARITY":
        messages.error(request, "Only charity accounts can request food.")
        return redirect("home")

    if not request.user.is_verified:
        messages.error(
            request,
            "Your charity account must be verified before requesting food."
        )
        return redirect("home")

    try:
        with transaction.atomic():
            donation = get_object_or_404(
                Donation.objects.select_for_update(),
                id=donation_id,
            )

            if donation.donor_id == request.user.id:
                messages.error(request, "You cannot request your own donation.")
                return redirect("home")

            if donation.status != Donation.Status.AVAILABLE:
                messages.error(request, "This donation is no longer available.")
                return redirect("home")

            if donation.pickup_deadline <= timezone.now():
                messages.error(request, "The pickup deadline has passed.")
                return redirect("home")

            PickupRequest.objects.create(
                donation=donation,
                requester=request.user,
            )

            donation.status = Donation.Status.CLAIMED
            donation.save(update_fields=["status"])

    except IntegrityError:
        messages.error(request, "You have already requested this donation.")
        return redirect("home")

    messages.success(request, "Pickup request submitted successfully.")
    return redirect("home")


@login_required
def my_pickup_requests(request):
    if request.user.role != "CHARITY":
        messages.error(request, "Only charity accounts can view pickup requests.")
        return redirect("home")

    pickup_requests = (
        PickupRequest.objects
        .filter(requester=request.user)
        .select_related("donation", "volunteer")
        .order_by("-requested_at")
    )

    return render(
        request,
        "requests_app/my_pickup_requests.html",
        {"pickup_requests": pickup_requests},
    )


@login_required
def manage_pickup_requests(request):
    if request.user.role != "DONOR":
        messages.error(request, "Only food donors can manage pickup requests.")
        return redirect("home")

    pickup_requests = (
        PickupRequest.objects
        .filter(donation__donor=request.user)
        .select_related("donation", "requester", "volunteer")
        .order_by("-requested_at")
    )

    return render(
        request,
        "requests_app/manage_pickup_requests.html",
        {"pickup_requests": pickup_requests},
    )


@login_required
def decide_pickup_request(request, request_id):
    if request.method != "POST":
        return redirect("manage_pickup_requests")

    if request.user.role != "DONOR":
        messages.error(request, "Only food donors can manage requests.")
        return redirect("home")

    action = request.POST.get("action")

    if action not in ["approve", "reject"]:
        messages.error(request, "Invalid action.")
        return redirect("manage_pickup_requests")

    with transaction.atomic():
        pickup_request = get_object_or_404(
            PickupRequest.objects.select_for_update().select_related("donation"),
            id=request_id,
            donation__donor=request.user,
        )

        donation = Donation.objects.select_for_update().get(
            id=pickup_request.donation_id
        )

        if pickup_request.status != PickupRequest.Status.PENDING:
            messages.error(request, "This request has already been processed.")
            return redirect("manage_pickup_requests")

        
        if action == "approve":
            print("Donation deadline:", donation.pickup_deadline)
            print("Current time:", timezone.now())
            print("Is expired:", donation.pickup_deadline <= timezone.now()) 

            if donation.pickup_deadline <= timezone.now():
                donation.status = Donation.Status.EXPIRED
                donation.save(update_fields=["status"])
                messages.error(
                    request,
                    "This donation has expired. The request cannot be approved."
                )
                return redirect("manage_pickup_requests")

            if donation.status != Donation.Status.CLAIMED:
                messages.error(request, "This donation is no longer claimable.")
                return redirect("manage_pickup_requests")

            pickup_request.status = PickupRequest.Status.APPROVED
            pickup_request.delivery_status = (
                PickupRequest.DeliveryStatus.AVAILABLE
            )
            pickup_request.save(
                update_fields=["status", "delivery_status"]
            )
            messages.success(
                request,
                "Request approved. It is now available for volunteers."
            )

        else:
            pickup_request.status = PickupRequest.Status.REJECTED
            pickup_request.save(update_fields=["status"])

            if donation.pickup_deadline <= timezone.now():
               donation.status = Donation.Status.EXPIRED
            else:
               donation.status = Donation.Status.AVAILABLE

            donation.save(update_fields=["status"])
            messages.success(request, "Pickup request rejected.")

    return redirect("manage_pickup_requests")


@login_required
def volunteer_dashboard(request):
    if request.user.role != "VOLUNTEER":
        messages.error(request, "Only volunteers can access this dashboard.")
        return redirect("home")

    available_tasks = (
        PickupRequest.objects
        .filter(
            status=PickupRequest.Status.APPROVED,
            delivery_status=PickupRequest.DeliveryStatus.AVAILABLE,
            donation__pickup_deadline__gt=timezone.now(),
        )
        .select_related("donation", "requester", "donation__donor")
        .order_by("donation__pickup_deadline")
    )

    my_tasks = (
        PickupRequest.objects
        .filter(volunteer=request.user)
        .select_related("donation", "requester", "donation__donor")
        .order_by("-requested_at")
    )

    return render(
        request,
        "requests_app/volunteer_dashboard.html",
        {
            "available_tasks": available_tasks,
            "my_tasks": my_tasks,
        },
    )


@login_required
def accept_delivery(request, request_id):
    if request.method != "POST":
        return redirect("volunteer_dashboard")

    if request.user.role != "VOLUNTEER":
        messages.error(request, "Only volunteers can accept delivery tasks.")
        return redirect("home")

    with transaction.atomic():
        pickup_request = get_object_or_404(
            PickupRequest.objects.select_for_update().select_related("donation"),
            id=request_id,
        )

        if pickup_request.donation.pickup_deadline <= timezone.now():
            messages.error(request, "This donation has expired.")
            return redirect("volunteer_dashboard")

        if pickup_request.status != PickupRequest.Status.APPROVED:
            messages.error(request, "This request is not approved.")
            return redirect("volunteer_dashboard")

        if pickup_request.delivery_status != PickupRequest.DeliveryStatus.AVAILABLE:
            messages.error(request, "This delivery task is no longer available.")
            return redirect("volunteer_dashboard")

        pickup_request.volunteer = request.user
        pickup_request.delivery_status = PickupRequest.DeliveryStatus.ASSIGNED
        pickup_request.save(update_fields=["volunteer", "delivery_status"])

    messages.success(request, "You have accepted this delivery task.")
    return redirect("volunteer_dashboard")


@login_required
def update_delivery_status(request, request_id):
    if request.method != "POST":
        return redirect("volunteer_dashboard")

    if request.user.role != "VOLUNTEER":
        messages.error(request, "Only volunteers can update delivery status.")
        return redirect("home")

    action = request.POST.get("action")

    with transaction.atomic():
        pickup_request = get_object_or_404(
            PickupRequest.objects.select_for_update(),
            id=request_id,
            volunteer=request.user,
        )

        if action == "collected":
            if pickup_request.delivery_status != PickupRequest.DeliveryStatus.ASSIGNED:
                messages.error(request, "This task cannot be marked as collected.")
                return redirect("volunteer_dashboard")

            pickup_request.delivery_status = PickupRequest.DeliveryStatus.COLLECTED

        elif action == "delivered":
            if pickup_request.delivery_status != PickupRequest.DeliveryStatus.COLLECTED:
                messages.error(request, "Collect the food before marking it delivered.")
                return redirect("volunteer_dashboard")

            pickup_request.delivery_status = PickupRequest.DeliveryStatus.DELIVERED

        else:
            messages.error(request, "Invalid delivery action.")
            return redirect("volunteer_dashboard")

        pickup_request.save(update_fields=["delivery_status"])

    messages.success(request, "Delivery status updated successfully.")
    return redirect("volunteer_dashboard")


@login_required
def confirm_delivery(request, request_id):
    if request.method != "POST":
        return redirect("my_pickup_requests")

    if request.user.role != "CHARITY":
        messages.error(request, "Only charities can confirm food receipt.")
        return redirect("home")

    with transaction.atomic():
        pickup_request = get_object_or_404(
            PickupRequest.objects.select_for_update().select_related("donation"),
            id=request_id,
            requester=request.user,
        )

        if pickup_request.delivery_status != PickupRequest.DeliveryStatus.DELIVERED:
            messages.error(request, "This delivery has not been marked as delivered.")
            return redirect("my_pickup_requests")

        donation = Donation.objects.select_for_update().get(
            id=pickup_request.donation_id
        )

        pickup_request.delivery_status = PickupRequest.DeliveryStatus.CONFIRMED
        pickup_request.status = PickupRequest.Status.COMPLETED
        pickup_request.save(update_fields=["delivery_status", "status"])

        donation.status = Donation.Status.PICKED_UP
        donation.save(update_fields=["status"])

    messages.success(request, "Food receipt confirmed. Thank you!")
    return redirect("my_pickup_requests")


@login_required
def complete_pickup(request, request_id):
    messages.info(
        request,
        "Delivery completion is now handled by the volunteer and confirmed by the charity."
    )
    return redirect("manage_pickup_requests")
