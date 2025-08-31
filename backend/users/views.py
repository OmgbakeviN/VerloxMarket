from django.shortcuts import render
from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, MeSerializer
from .utils import send_login_email

# Create your views here.

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Crée un user avec email+password.
        Retourne access/refresh + info profil.
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Générer les tokens JWT pour l'auto-login après inscription
        refresh = RefreshToken.for_user(user)
        data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "email": user.email,
                "balance": str(user.profile.balance),
                "currency": user.profile.currency,
            },
        }
        return Response(data, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Authentifie via email + password (username=email).
        Envoie un email de login si OK.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        password = serializer.validated_data["password"]

        # Récupère le user par email puis utilise authenticate(username=..., password=...)
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"detail": "Identifiants invalides."}, status=status.HTTP_400_BAD_REQUEST)

        user_auth = authenticate(request, username=user.username, password=password)
        if not user_auth:
            return Response({"detail": "Identifiants invalides."}, status=status.HTTP_400_BAD_REQUEST)

        # Tokens JWT
        refresh = RefreshToken.for_user(user_auth)
        data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "email": user_auth.email,
                "balance": str(user_auth.profile.balance),
                "currency": user_auth.profile.currency,
            },
        }

        # Envoi d'email de login (asynchrone plus tard; ici simple)
        send_login_email(user_auth)

        return Response(data, status=status.HTTP_200_OK)

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Retourne les infos principales (email, balance) du user courant.
        """
        user = request.user
        payload = {
            "email": user.email,
            "balance": user.profile.balance,
            "currency": user.profile.currency,
        }
        return Response(MeSerializer(payload).data, status=status.HTTP_200_OK)