from django.core.mail import send_mail
from django.conf import settings

def send_login_email(user):
    """
    Envoie un email après connexion réussie. En dev, ça s'affiche en console.
    """
    subject = "Nouvelle connexion à votre compte VerloxMarket"
    message = (
        f"Bonjour,\n\n"
        f"Vous venez de vous connecter sur VerloxMarket avec l'adresse {user.email}.\n"
        f"Si ce n'était pas vous, changez votre mot de passe immédiatement.\n\n"
        f"- L'équipe Verlox"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
