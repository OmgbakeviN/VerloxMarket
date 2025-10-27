from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import EmailPin
from rest_framework import serializers
from .utils import send_verification_pin_email

User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email déjà utilisé.")
        return value

    def create(self, validated_data):
        email = validated_data["email"].lower()
        user = User.objects.create_user(
            username=email, email=email, password=validated_data["password"]
        )
        # Génère un PIN
        pin = EmailPin.gen_code()
        EmailPin.objects.create(
            user=user,
            code=pin,
            purpose="SIGNUP",
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        send_verification_pin_email(email, pin)
        return user

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)

    def validate(self, attrs):
        from .models import UserProfile
        email = attrs["email"].lower()
        code = attrs["code"]
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Utilisateur introuvable."})

        pin_qs = EmailPin.objects.filter(user=user, purpose="SIGNUP", is_used=False).order_by("-created_at")
        if not pin_qs.exists():
            raise serializers.ValidationError({"code": "Aucun code actif. Veuillez renvoyer un code."})
        pin = pin_qs.first()

        if pin.is_expired():
            raise serializers.ValidationError({"code": "Code expiré. Veuillez renvoyer un code."})

        # petite limite d’essais
        if pin.attempts >= 5:
            raise serializers.ValidationError({"code": "Trop d'essais. Renvoyez un code."})

        if pin.code != code:
            pin.attempts += 1
            pin.save(update_fields=["attempts"])
            raise serializers.ValidationError({"code": "Code invalide."})

        attrs["user"] = user
        attrs["pin"] = pin
        return attrs

    def save(self, **kwargs):
        from .models import UserProfile
        user = self.validated_data["user"]
        pin = self.validated_data["pin"]
        # Marque utilisé + vérifie le profil
        pin.is_used = True
        pin.save(update_fields=["is_used"])
        profile = user.profile
        profile.is_email_verified = True
        profile.save(update_fields=["is_email_verified"])
        return user

class ResendPinSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta
        email = validated_data["email"].lower()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Utilisateur introuvable."})

        # petit anti-spam: 1 code max / 60s
        latest = EmailPin.objects.filter(user=user, purpose="SIGNUP").order_by("-created_at").first()
        if latest and (timezone.now() - latest.created_at) < timedelta(seconds=60):
            raise serializers.ValidationError({"email": "Veuillez patienter avant de renvoyer un code."})

        pin = EmailPin.gen_code()
        EmailPin.objects.create(
            user=user,
            code=pin,
            purpose="SIGNUP",
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        send_verification_pin_email(email, pin)
        return use

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class MeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    balance = serializers.DecimalField(max_digits=14, decimal_places=2)
    currency = serializers.CharField()
