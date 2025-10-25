from django.urls import path
from .views import WalletRateView, WalletMeView, DepositCreateView, DepositListView

urlpatterns = [
    path("rate/", WalletRateView.as_view(), name="wallet-rate"),
    path("me/", WalletMeView.as_view(), name="wallet-me"),
    path("deposits", DepositCreateView.as_view(), name="wallet-deposits-create"),
    path("deposits/list", DepositListView.as_view(), name="wallet-deposits-list"),
]
