from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from users.models import UserProfile
from companies.models import Company
from companies.price_engine import ensure_company_registered, get_ticks
from .models import Trade
from .constants import ALLOWED_DURATIONS, STAKE_MIN_VC, STAKE_MAX_VC

class TradeCreateSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    direction = serializers.ChoiceField(choices=["UP", "DOWN"])
    stake = serializers.DecimalField(max_digits=14, decimal_places=2)          # montant en VC
    duration_sec = serializers.IntegerField()

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        # Company active
        try:
            company = Company.objects.get(pk=attrs["company_id"], is_active=True)
        except Company.DoesNotExist:
            raise serializers.ValidationError({"company_id": "Company not found or inactive."})

        # Durée autorisée
        duration = int(attrs["duration_sec"])
        if duration not in ALLOWED_DURATIONS:
            raise serializers.ValidationError({"duration_sec": f"Duration must be one of {ALLOWED_DURATIONS}."})

        # Stake VC
        try:
            stake = Decimal(attrs["stake"])
        except (InvalidOperation, KeyError):
            raise serializers.ValidationError({"stake": "Invalid stake amount."})

        if stake < Decimal(STAKE_MIN_VC) or stake > Decimal(STAKE_MAX_VC):
            raise serializers.ValidationError({"stake": f"Stake must be between {STAKE_MIN_VC} and {STAKE_MAX_VC} VC."})

        # Solde VC suffisant (pré-check, re-check en transaction)
        if user.profile.balance_vc < stake:
            raise serializers.ValidationError({"stake": "Insufficient VC balance."})

        # Snapshot du prix courant (moteur)
        ensure_company_registered(company.id, company.volatility)
        ticks = get_ticks(company.id, window=1)
        if not ticks:
            raise serializers.ValidationError("No price available for this company.")
        open_price = Decimal(str(ticks[-1]["price"]))

        attrs["company"] = company
        attrs["open_price"] = open_price
        attrs["payout_percent_snapshot"] = company.payout_percent
        attrs["opened_at"] = timezone.now()
        attrs["expires_at"] = attrs["opened_at"] + timedelta(seconds=duration)
        attrs["stake"] = stake  # (VC)
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        stake = validated_data["stake"]

        # Débit VC + création atomique
        with transaction.atomic():
            profile = UserProfile.objects.select_for_update().get(user=user)

            # re-check solde VC
            if profile.balance_vc < stake:
                raise serializers.ValidationError({"stake": "Insufficient VC balance."})

            # 💳 débit immédiat de la mise en VC
            profile.balance_vc = (profile.balance_vc - stake).quantize(Decimal("0.01"))
            profile.save(update_fields=["balance_vc"])

            trade = Trade.objects.create(
                user=user,
                company=validated_data["company"],
                direction=validated_data["direction"],
                stake=stake,  # VC
                payout_percent_snapshot=validated_data["payout_percent_snapshot"],
                open_price=validated_data["open_price"],
                opened_at=validated_data["opened_at"],
                expires_at=validated_data["expires_at"],
                status="OPEN",
            )
        return trade


class TradeSerializer(serializers.ModelSerializer):
    company_symbol = serializers.CharField(source="company.symbol", read_only=True)
    class Meta:
        model = Trade
        fields = [
            "id", "company", "company_symbol", "direction", "stake",
            "payout_percent_snapshot", "open_price", "close_price",
            "opened_at", "expires_at", "status", "pnl"
        ]