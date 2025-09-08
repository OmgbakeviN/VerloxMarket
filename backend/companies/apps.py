from django.apps import AppConfig
import os

class CompaniesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "companies"

    def ready(self):
        """
        Démarre le price engine une seule fois (évite double-run en autoreload).
        """
        from .price_engine import start_engine
        # En dev, Django autoreload lance 2 process; on protège:
        if os.environ.get("RUN_MAIN") == "true" or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            start_engine()
        # En production WSGI (PythonAnywhere), RUN_MAIN n'est pas présent:
        if not os.environ.get("RUN_MAIN") and not os.environ.get("WERKZEUG_RUN_MAIN"):
            start_engine()
