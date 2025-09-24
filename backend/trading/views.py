from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from .serializers import TradeCreateSerializer, TradeSerializer
from .models import Trade

# Create your views here.

class TradeCreateListView(APIView):
    """
    POST /api/trading/trades/   -> créer un trade (auth requis)
    GET  /api/trading/trades?status=OPEN|CLOSED  -> lister mes trades
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TradeCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        trade = serializer.save()
        return Response(TradeSerializer(trade).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        status_filter = request.GET.get("status")
        qs = Trade.objects.filter(user=request.user)
        if status_filter == "OPEN":
            qs = qs.filter(status="OPEN")
        elif status_filter == "CLOSED":
            qs = qs.filter(~Q(status="OPEN"))
        data = TradeSerializer(qs.order_by("-opened_at")[:100], many=True).data
        return Response(data, status=status.HTTP_200_OK)