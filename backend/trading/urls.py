from django.urls import path
from .views import TradeCreateListView

urlpatterns = [
    path("trades/", TradeCreateListView.as_view(), name="trades"),
]
