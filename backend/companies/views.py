from .models import Company
from .serializers import CompanySerializer
from rest_framework import generics, permissions

# Create your views here.

class CompanyListView(generics.ListAPIView):
    """
    Liste uniquement les entreprises actives pour la V1.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.filter(is_active=True)

class CompanyDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CompanySerializer
    queryset = Company.objects.all()