from django.db import models

# Create your models here.

class Company(models.Model):
    """
    Entreprise tradable (simulation V1).
    """
    VOL_CHOICES = [
        ("LOW", "Low"),
        ("MID", "Mid"),
        ("HIGH", "High"),
    ]

    name = models.CharField(max_length=120)
    symbol = models.CharField(max_length=12, unique=True)  # ex: VLXM
    payout_percent = models.PositiveIntegerField(default=80)  # % de payout pour le fixed time
    volatility = models.CharField(max_length=8, choices=VOL_CHOICES, default="MID")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["symbol"]

    def __str__(self):
        return f"{self.symbol} - {self.name}"