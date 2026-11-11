from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import DonationForm
from .models import Donation


def home(request):
    donations = Donation.objects.filter(
        status=Donation.Status.AVAILABLE,
        pickup_deadline__gt=timezone.now(),
    ).order_by("pickup_deadline")

    return render(
        request,
        "donations/home.html",
        {"donations": donations},
    )


@login_required
def create_donation(request):
    if request.user.role != "DONOR":
        messages.error(request, "Only food donors can list donations.")
        return redirect("home")

    if request.method == "POST":
        form = DonationForm(request.POST, request.FILES)

        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user

            if donation.pickup_deadline <= timezone.now():
                form.add_error(
                    "pickup_deadline",
                    "Please choose a future pickup deadline.",
                )
            else:
                donation.save()
                messages.success(request, "Your food donation was listed!")
                return redirect("home")
    else:
        form = DonationForm()

    return render(
        request,
        "donations/create_donation.html",
        {"form": form},
    )


@login_required
def donor_dashboard(request):
    if request.user.role != "DONOR":
        messages.error(request, "Only food donors can access this dashboard.")
        return redirect("home")

    Donation.objects.filter(
        donor=request.user,
        status=Donation.Status.AVAILABLE,
        pickup_deadline__lte=timezone.now(),
    ).update(status=Donation.Status.EXPIRED)

    my_donations = Donation.objects.filter(
        donor=request.user
    ).order_by("-created_at")

    return render(
        request,
        "donations/donor_dashboard.html",
        {"my_donations": my_donations},
    )