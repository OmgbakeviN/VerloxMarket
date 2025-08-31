from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    """
    Inscription: on choisit d'utiliser l'email comme username pour simplifier.
    """
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value

    def create(self, validated_data):
        email = validated_data["email"].lower()
        password = validated_data["password"]
        # On fixe username = email pour éviter les confusions
        user = User.objects.create_user(username=email, email=email, password=password)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class MeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    balance = serializers.DecimalField(max_digits=14, decimal_places=2)
    currency = serializers.CharField()
