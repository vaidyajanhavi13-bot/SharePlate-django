from django.conf import settings
from django.db import models


class Donation(models.Model):

    class QuantityUnit(models.TextChoices):
        KG = "KG", "kg"
        PLATE = "PLATE", "plates"
        PIECE = "PIECE", "pieces"
        PACKET = "PACKET", "packets"
        BOX = "BOX", "boxes"

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        CLAIMED = "CLAIMED", "Claimed"
        PICKED_UP = "PICKED_UP", "Picked Up"
        EXPIRED = "EXPIRED", "Expired"

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="donations",
    )
    food_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="donations/",
        blank=True,
        null=True,
    )

    quantity = models.PositiveIntegerField()

    quantity_unit = models.CharField(
        max_length=10,
        choices=QuantityUnit.choices,
        default=QuantityUnit.KG,
    )

    pickup_address = models.CharField(max_length=255)
    pickup_deadline = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.food_name