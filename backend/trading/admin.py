from django.contrib import admin
from .models import Trade
# Register your models here.

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "direction", "stake", "payout_percent_snapshot", "open_price", "close_price", "opened_at", "expires_at", "status", "pnl")
