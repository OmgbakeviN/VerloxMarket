from decimal import Decimal
from .constants import DRAW_ON_EQUAL

def compute_outcome_and_pnl(direction: str, open_price: Decimal, close_price: Decimal, stake: Decimal, payout_percent: int):
    """
    Calcule le statut final et le PnL d'un trade fixed-time.
    - direction: "UP" ou "DOWN"
    - égalité: config via DRAW_ON_EQUAL (False par défaut => LOST)
    """
    status = "LOST"
    pnl = Decimal("0.00")

    if close_price == open_price:
        if DRAW_ON_EQUAL:
            status = "OPEN"  # on peut considérer un statut "DRAW" si tu veux l'ajouter plus tard
            pnl = Decimal("0.00")
            status = "LOST"  # par simplicité V1 on garde LOST si DRAW_ON_EQUAL=False
        else:
            status = "LOST"
            pnl = -stake
        return status, pnl

    if direction == "UP":
        if close_price > open_price:
            status = "WON"
            pnl = (stake * Decimal(payout_percent) / Decimal(100)).quantize(Decimal("0.01"))
        else:
            status = "LOST"
            pnl = -stake
    else:  # direction == "DOWN"
        if close_price < open_price:
            status = "WON"
            pnl = (stake * Decimal(payout_percent) / Decimal(100)).quantize(Decimal("0.01"))
        else:
            status = "LOST"
            pnl = -stake

    return status, pnl
