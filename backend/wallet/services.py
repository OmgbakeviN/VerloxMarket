from decimal import Decimal
from django.db import transaction
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings

from users.models import UserProfile
from .models import Deposit, WalletSettings

def gen_reference(prefix="DEP"):
    return f"{prefix}-{get_random_string(6).upper()}"

@transaction.atomic
def credit_vc(user, provider: str, phone: str, amount_xaf: Decimal, *, reason="DEPOSIT", meta=None):
    """
    Crédite le wallet en VC de l'utilisateur.
    - Calcule coins_vc = amount_xaf / rate
    - Crée un Deposit (status=SUCCESS en V1)
    - Incrémente profile.balance_vc (select_for_update)
    - Envoie un email de confirmation
    """
    rate = WalletSettings.get_rate()
    coins = (Decimal(amount_xaf) / rate).quantize(Decimal("0.01"))
    ref = gen_reference()

    # 1) Créer le dépôt (snapshot du taux)
    dep = Deposit.objects.create(
        user=user,
        provider=provider,
        phone=phone,
        amount_xaf=amount_xaf,
        rate_xaf_per_vc=rate,
        coins_vc=coins,
        status="SUCCESS",
        reference=ref,
    )

    # 2) Incrémenter le solde VC
    profile = UserProfile.objects.select_for_update().get(user=user)
    profile.balance_vc = (profile.balance_vc + coins).quantize(Decimal("0.01"))
    profile.save(update_fields=["balance_vc"])

    # 3) Email (console en dev)
    subject = "VerloxMarket — Dépôt confirmé"
    msg = (
        f"Bonjour,\n\n"
        f"Votre dépôt est confirmé.\n"
        f"Référence: {dep.reference}\n"
        f"Opérateur: {provider}\n"
        f"Numéro: {phone}\n"
        f"Montant: {amount_xaf} XAF\n"
        f"Crédit: {coins} VC (taux {rate} XAF/VC)\n\n"
        f"Merci d'utiliser VerloxMarket."
    )
    send_mail(subject, msg, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)

    return dep
