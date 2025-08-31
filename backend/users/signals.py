from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_profile_on_user_creation(sender, instance, created, **kwargs):
    """
    Crée automatiquement un UserProfile au moment de la création de l'utilisateur.
    """
    if created:
        UserProfile.objects.create(user=instance)
