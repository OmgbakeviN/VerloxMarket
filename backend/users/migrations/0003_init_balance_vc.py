from django.db import migrations
from decimal import Decimal, ROUND_DOWN

RATE_XAF_PER_VC = Decimal("100")  # 1 VC = 100 XAF (démo)

def init_balance_vc(apps, schema_editor):
    UserProfile = apps.get_model("users", "UserProfile")
    for p in UserProfile.objects.all():
        try:
            vc = (p.balance / RATE_XAF_PER_VC).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        except Exception:
            vc = Decimal("0.00")
        p.balance_vc = vc
        p.save(update_fields=["balance_vc"])

class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_userprofile_balance_vc"),  # <-- mets ici le VRAI nom juste avant
    ]

    operations = [
        migrations.RunPython(init_balance_vc, migrations.RunPython.noop),
    ]
