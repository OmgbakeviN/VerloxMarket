from django.db import models
from django.conf import settings
from django.utils import timezone
from companies.models import Company


# Create your models here.


class Trade(models.Model):
    """
    Trade Fixed-Time.
    """
    DIR_CHOICES = [("UP", "Up"), ("DOWN", "Down")]
    STATUS_CHOICES = [("OPEN", "Open"), ("WON", "Won"), ("LOST", "Lost")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trades")
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="trades")

    direction = models.CharField(max_length=4, choices=DIR_CHOICES)
    stake = models.DecimalField(max_digits=14, decimal_places=2)  # mise

    payout_percent_snapshot = models.PositiveIntegerField(default=80)  # snapshot de l'entreprise au moment d'ouvrir
    open_price = models.DecimalField(max_digits=16, decimal_places=6)
    close_price = models.DecimalField(max_digits=16, decimal_places=6, null=True, blank=True)

    opened_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default="OPEN")
    pnl = models.DecimalField(max_digits=14, decimal_places=2, default=0)  # résultat final

    class Meta:
        indexes = [
            models.Index(fields=["status", "expires_at"]),
            models.Index(fields=["user", "opened_at"]),
        ]

    def __str__(self):
        return f"Trade#{self.pk} {self.company.symbol} {self.direction} {self.status}"