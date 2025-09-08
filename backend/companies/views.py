from .models import Company
from .serializers import CompanySerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .price_engine import ensure_company_registered, get_ticks

# Create your views here.

# get pour les entreprises actives
class CompanyListView(generics.ListAPIView):
    """
    Liste uniquement les entreprises actives pour la V1.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.filter(is_active=True)

# get pour une entreprise specifique par id
class CompanyDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

#get pour les entreprises par symbol
class CompanyBySymbolView(generics.GenericAPIView):
    """
    Récupère une entreprise à partir de son 'symbol' (ex: VLXE).
    Utile pour la route frontend /company/:symbol
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = CompanySerializer

    def get(self, request, symbol):
        try:
            company = Company.objects.get(symbol__iexact=symbol, is_active=True)
        except Company.DoesNotExist:
            return Response({"detail": "Company not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(company).data)

# get pour les ticks d'une entreprise
class CompanyTicksView(APIView):
    """
    Renvoie les ticks d'une company par ID.
    GET /api/companies/<id>/ticks/?window=120
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk: int):
        # assure l’enregistrement dans le moteur (idempotent)
        company = get_object_or_404(Company, pk=pk, is_active=True)
        ensure_company_registered(company.id, company.volatility)

        try:
            window = int(request.GET.get("window", "120"))
        except ValueError:
            window = 120

        data = get_ticks(company.id, window=window)
        # data est une liste de {t, price} (t en ms UTC)
        return Response(data, status=status.HTTP_200_OK)