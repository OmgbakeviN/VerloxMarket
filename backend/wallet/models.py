from django.db import models
from django.conf import settings
from decimal import Decimal

PROVIDERS = [
    ("ORANGE", "Orange Money"),
    ("MTN", "MTN MoMo"),
]

class WalletSettings(models.Model):
    """
    Paramétrage simple du wallet.
    - rate_xaf_per_vc : combien de XAF pour 1 VC (démo: 100)
    - deposit_min_xaf / deposit_max_xaf : limites
    """
    rate_xaf_per_vc = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("100.00"))
    deposit_min_xaf = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("100.00"))
    deposit_max_xaf = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("10000000.00"))

    def __str__(self):
        return f"WalletSettings(rate={self.rate_xaf_per_vc} XAF/VC)"

    @classmethod
    def get_rate(cls) -> Decimal:
        obj = cls.objects.first()
        return obj.rate_xaf_per_vc if obj else Decimal("100.00")

class Deposit(models.Model):
    """
    Dépôt simulé : crédite le wallet en VC.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="deposits")
    provider = models.CharField(max_length=12, choices=PROVIDERS)
    phone = models.CharField(max_length=32)
    amount_xaf = models.DecimalField(max_digits=14, decimal_places=2)
    rate_xaf_per_vc = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot du taux
    coins_vc = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=16, default="SUCCESS")  # V1: succès direct
    reference = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Deposit({self.reference}, {self.coins_vc} VC)"
