import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

from companies.models import Company
from trading.models import Trade
from trading.utils import compute_outcome_and_pnl

@pytest.mark.django_db
def test_compute_outcome_basic():
    stake = Decimal("1000")
    payout = 80

    # UP gagnant
    status, pnl = compute_outcome_and_pnl("UP", Decimal("100"), Decimal("101"), stake, payout)
    assert status == "WON"
    assert pnl == Decimal("800.00")

    # UP perdant
    status, pnl = compute_outcome_and_pnl("UP", Decimal("100"), Decimal("99"), stake, payout)
    assert status == "LOST"
    assert pnl == Decimal("-1000")

    # DOWN gagnant
    status, pnl = compute_outcome_and_pnl("DOWN", Decimal("100"), Decimal("99"), stake, payout)
    assert status == "WON"
    assert pnl == Decimal("800.00")

    # DOWN perdant
    status, pnl = compute_outcome_and_pnl("DOWN", Decimal("100"), Decimal("101"), stake, payout)
    assert status == "LOST"
    assert pnl == Decimal("-1000")

@pytest.mark.django_db
def test_close_expired_trade_command(monkeypatch):
    # Setup user + profile auto via signal
    user = User.objects.create_user(username="u@u.com", email="u@u.com", password="x")
    c = Company.objects.create(name="TestCo", symbol="TST", payout_percent=80, volatility="MID", is_active=True)

    # Trade expiré
    t = Trade.objects.create(
        user=user, company=c, direction="UP",
        stake=Decimal("1000.00"),
        payout_percent_snapshot=80,
        open_price=Decimal("100.000000"),
        opened_at=timezone.now() - timedelta(minutes=2),
        expires_at=timezone.now() - timedelta(seconds=10),
        status="OPEN"
    )

    # Mock les ticks pour forcer un close_price > open_price => WON
    def fake_get_ticks(company_id: int, window: int = 1):
        return [{"t": 0, "price": 101.0}]
    monkeypatch.setattr("trading.management.commands.close_expired_trades.get_ticks", fake_get_ticks)

    from django.core.management import call_command
    call_command("close_expired_trades")

    t.refresh_from_db()
    user.profile.refresh_from_db()

    assert t.status == "WON"
    assert t.close_price == Decimal("101")
    assert t.pnl == Decimal("800.00")
    # 100000.00 + 800.00
    assert user.profile.balance == Decimal("100800.00")
