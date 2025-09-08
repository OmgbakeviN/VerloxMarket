from django.urls import path
from .views import CompanyListView, CompanyDetailView, CompanyBySymbolView, CompanyTicksView

urlpatterns = [
    path("", CompanyListView.as_view(), name="company-list"),
    path("<int:pk>", CompanyDetailView.as_view(), name="company-detail"),
    path("by-symbol/<str:symbol>/", CompanyBySymbolView.as_view(), name="company-by-symbol"),
    path("<int:pk>/ticks/", CompanyTicksView.as_view(), name="company-ticks"),
]
