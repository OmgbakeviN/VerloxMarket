from decimal import Decimal, ROUND_DOWN
from rest_framework import serializers
from .models import Deposit, WalletSettings, PROVIDERS

PHONE_HELP = "Numéro au format local sans indicatif (ex: 6XXXXXXXX)."

def get_rate():
    return WalletSettings.get_rate()

class RateSerializer(serializers.Serializer):
    rate_xaf_per_vc = serializers.DecimalField(max_digits=10, decimal_places=2)

class WalletMeSerializer(serializers.Serializer):
    balance_vc = serializers.DecimalField(max_digits=14, decimal_places=2)
    rate_xaf_per_vc = serializers.DecimalField(max_digits=10, decimal_places=2)

class DepositCreateSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=[p[0] for p in PROVIDERS])
    phone = serializers.CharField(max_length=32, help_text=PHONE_HELP)
    amount_xaf = serializers.DecimalField(max_digits=14, decimal_places=2)

    def validate(self, attrs):
        # Provider
        provider = attrs["provider"]
        if provider not in dict(PROVIDERS):
            raise serializers.ValidationError({"provider": "Provider invalide."})

        # Phone (validation simple Cameroun: commence par 6 + 8 chiffres)
        phone = attrs["phone"].strip()
        if not (len(phone) == 9 and phone.isdigit() and phone.startswith("6")):
            raise serializers.ValidationError({"phone": f"Numéro invalide. {PHONE_HELP}"})

        # Amount min/max
        amount_xaf = attrs["amount_xaf"]
        ws = WalletSettings.objects.first()
        min_x = ws.deposit_min_xaf if ws else Decimal("100.00")
        max_x = ws.deposit_max_xaf if ws else Decimal("10000000.00")
        if amount_xaf < min_x or amount_xaf > max_x:
            raise serializers.ValidationError({"amount_xaf": f"Le dépôt doit être entre {min_x} et {max_x} XAF."})

        # Calcul prévisionnel des VC (arrondi à 2 décimales, type floor)
        rate = get_rate()
        coins = (amount_xaf / rate).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

        attrs["phone"] = phone
        attrs["rate_xaf_per_vc"] = rate
        attrs["coins_vc"] = coins
        return attrs

class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = [
            "id", "reference", "provider", "phone",
            "amount_xaf", "rate_xaf_per_vc", "coins_vc",
            "status", "created_at",
        ]
