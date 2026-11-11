from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import User


class SharePlateRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")


def register(request):
    if request.method == "POST":
        form = SharePlateRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account was created successfully.")
            return redirect("home")
    else:
        form = SharePlateRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})

@login_required
def profile(request):
    return render(request, "accounts/profile.html")