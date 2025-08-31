from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.timezone import now

@api_view(["GET"])
def health(_request):
    # Endpoint simple pour vérifier API/CORS/horloge
    return Response({"status": "ok", "service": "verlox-backend", "time": now().isoformat()})
