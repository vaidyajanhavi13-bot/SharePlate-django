from django.conf import settings
from django.db import models


class PickupRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        COMPLETED = "COMPLETED", "Completed"

    class DeliveryStatus(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available for Volunteer"
        ASSIGNED = "ASSIGNED", "Volunteer Assigned"
        COLLECTED = "COLLECTED", "Food Collected"
        DELIVERED = "DELIVERED", "Delivered"
        CONFIRMED = "CONFIRMED", "Receipt Confirmed"

    donation = models.ForeignKey(
        "donations.Donation",
        on_delete=models.CASCADE,
        related_name="pickup_requests",
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pickup_requests",
    )
    volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="volunteer_deliveries",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        blank=True,
        default="",
    )
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["donation", "requester"],
                name="unique_donation_requester",
            )
        ]

    def __str__(self):
        return f"{self.requester.username} - {self.donation.food_name}"