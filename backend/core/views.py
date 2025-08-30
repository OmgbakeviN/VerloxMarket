from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.timezone import now
# Create your views here.

@api_view(["GET"])
def health(request):
    """
    Endpoint de santé très simple pour valider:
    - le serveur tourne
    - le routage fonctionne
    - la timezone est correcte
    """
    return Response({
        "status": "ok",
        "service": "verlox-backend",
        "time": now().isoformat()
    })