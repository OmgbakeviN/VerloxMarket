from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db import transaction

from .serializers import (
    RateSerializer, WalletMeSerializer,
    DepositCreateSerializer, DepositSerializer
)
from .models import WalletSettings, Deposit
from .services import credit_vc

class WalletRateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        rate = WalletSettings.get_rate()
        return Response(RateSerializer({"rate_xaf_per_vc": rate}).data)

class WalletMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        rate = WalletSettings.get_rate()
        data = {
            "balance_vc": user.profile.balance_vc,
            "rate_xaf_per_vc": rate,
        }
        return Response(WalletMeSerializer(data).data)

class DepositCreateView(APIView):
    """
    POST /api/wallet/deposits
    Body: { provider, phone, amount_xaf }
    Effet:
      - valide (provider, phone, min/max)
      - calcule coins_vc = floor(amount_xaf / rate) à 2 décimales
      - crée Deposit(status=SUCCESS en V1)
      - crédite immédiatement user.profile.balance_vc (transactionnel)
      - envoie un email de confirmation
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = DepositCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        provider = ser.validated_data["provider"]
        phone = ser.validated_data["phone"]
        amount_xaf = ser.validated_data["amount_xaf"]

        # Transaction: crédit + enregistrement du dépôt + email
        with transaction.atomic():
            dep = credit_vc(
                request.user,
                provider=provider,
                phone=phone,
                amount_xaf=amount_xaf,
            )

        return Response(DepositSerializer(dep).data, status=status.HTTP_201_CREATED)
