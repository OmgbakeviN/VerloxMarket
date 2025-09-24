from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from django.db import transaction

from trading.models import Trade
from companies.price_engine import ensure_company_registered, get_ticks
from trading.utils import compute_outcome_and_pnl

class Command(BaseCommand):
    help = "Clôture les trades expirés: fixe close_price, calcule statut & pnl, met à jour le solde utilisateur."

    def handle(self, *args, **options):
        now = timezone.now()
        # On récupère tous les trades expirés encore ouverts
        expired_open_trades = Trade.objects.select_related("user__profile", "company") \
            .filter(status="OPEN", expires_at__lte=now).order_by("expires_at")

        closed_count = 0
        for trade in expired_open_trades:
            # 1) récupère le dernier prix courant depuis le moteur
            ensure_company_registered(trade.company_id, trade.company.volatility)
            ticks = get_ticks(trade.company_id, window=1)
            if not ticks:
                # Si pas de ticks (cas très rare), on skip pour ne pas casser la boucle
                continue
            close_price = Decimal(str(ticks[-1]["price"]))

            # 2) calcule statut et pnl
            status, pnl = compute_outcome_and_pnl(
                trade.direction,
                trade.open_price,
                close_price,
                trade.stake,
                trade.payout_percent_snapshot,
            )

            # 3) transaction atomique: MAJ trade + MAJ solde
            with transaction.atomic():
                trade.close_price = close_price
                trade.status = status
                trade.pnl = pnl
                trade.save(update_fields=["close_price", "status", "pnl"])

                # MAJ solde utilisateur
                profile = trade.user.profile
                profile.balance = (profile.balance + pnl).quantize(Decimal("0.01"))
                profile.save(update_fields=["balance"])

            closed_count += 1

        self.stdout.write(self.style.SUCCESS(f"Clôtures effectuées : {closed_count} trades"))
