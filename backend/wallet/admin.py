from django.contrib import admin
from .models import WalletSettings, Deposit

@admin.register(WalletSettings)
class WalletSettingsAdmin(admin.ModelAdmin):
    list_display = ("rate_xaf_per_vc", "deposit_min_xaf", "deposit_max_xaf")

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ("reference", "user", "provider", "phone", "amount_xaf", "coins_vc", "status", "created_at")
    list_filter = ("provider", "status", "created_at")
    search_fields = ("reference", "user__email", "phone")
