# users/jwt_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").lower()
        password = request.data.get("password") or ""
        user = authenticate(username=email, password=password)
        if not user:
            return Response({"detail": "Identifiants invalides."}, status=status.HTTP_401_UNAUTHORIZED)

        # ✅ exiger email vérifié
        if not user.profile.is_email_verified:
            return Response({"detail": "Email non vérifié. Vérifiez votre boîte mail ou renvoyez un code."}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "email": user.email,
                "balance_vc": str(user.profile.balance_vc),
                "currency": user.profile.currency,
            },
        }, status=status.HTTP_200_OK)

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        u = request.user
        return Response({
            "email": u.email,
            "balance_vc": str(u.profile.balance_vc),
            "currency": u.profile.currency,
            "is_email_verified": u.profile.is_email_verified,
        })
