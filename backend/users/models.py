from django.db import models
from django.conf import settings
from decimal import Decimal

# Create your models here.
class UserProfile(models.Model):
    """
    Profil lié au User natif, avec solde et devise.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=100000.00)  # solde de départ
    currency = models.CharField(max_length=8, default="XAF")
    balance_vc = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00")) 
     
    def __str__(self):
        return f"Profile({self.user.username})"