from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone
import secrets
# Create your models here.
class UserProfile(models.Model):
    """
    Profil lié au User natif, avec solde et devise.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=100000.00)  # solde de départ
    currency = models.CharField(max_length=8, default="XAF")
    balance_vc = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00")) 
    is_email_verified = models.BooleanField(default=False)
     
    def __str__(self):
        return f"Profile({self.user.username})"

class EmailPin(models.Model):
    #PIN email 6 chiffres pour signup / reset, etc.

    PURPOSES = (("SIGNUP", "SIGNUP"),)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_pins")
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=16, choices=PURPOSES, default="SIGNUP")
    expires_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() >= self.expires_at

    @staticmethod
    def gen_code():
        # 6 chiffres, pas de zéros “collants” (secrets pour l’entropie)
        return f"{secrets.randbelow(1000000):06d}"