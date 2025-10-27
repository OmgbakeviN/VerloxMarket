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

def send_verification_pin_email(email: str, pin: str):
    subject = "VerloxMarket — Vérification de votre email"
    msg = (
        "Bonjour,\n\n"
        f"Votre code de vérification est : {pin}\n"
        "Il est valable 10 minutes.\n\n"
        "Si vous n'êtes pas à l'origine de cette demande, ignorez cet email."
    )
    send_mail(subject, msg, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)