from django.db import migrations, models


def hash_existing_passwords(apps, schema_editor):
    Usuario = apps.get_model("usuarios", "Usuario")
    from django.contrib.auth.hashers import is_password_usable, make_password

    for usuario in Usuario.objects.exclude(contrasena__isnull=True).exclude(contrasena=""):
        if not is_password_usable(usuario.contrasena):
            usuario.contrasena = make_password(usuario.contrasena)
            usuario.save(update_fields=["contrasena"])


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usuario",
            name="contrasena",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.RunPython(hash_existing_passwords, migrations.RunPython.noop),
    ]
