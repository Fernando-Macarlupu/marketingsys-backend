# Generated by Django 3.1.3 on 2024-11-01 12:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CuentaUsuario',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(blank=True, max_length=100, null=True)),
                ('expiracionCuenta', models.DateTimeField(blank=True, null=True)),
                ('diasExpiracioncuenta', models.IntegerField(blank=True, null=True)),
                ('fechaCreacion', models.DateTimeField(auto_now_add=True)),
                ('fechaModificacion', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('modulo', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('nombreCompleto', models.CharField(blank=True, max_length=50, null=True)),
                ('fechaCreacion', models.DateTimeField(auto_now_add=True)),
                ('fechaModificacion', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PoliticaContrasena',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('nombreUsuario', models.CharField(blank=True, max_length=50, null=True)),
                ('contrasena', models.CharField(blank=True, max_length=50, null=True)),
                ('foto', models.TextField(blank=True, null=True)),
                ('rol', models.CharField(blank=True, max_length=50, null=True)),
                ('esAdministrador', models.BooleanField(default=True)),
                ('fechaCreacion', models.DateTimeField(auto_now_add=True)),
                ('fechaModificacion', models.DateTimeField(auto_now=True)),
                ('cuentaUsuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='usuarios.cuentausuario')),
                ('persona', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='usuarios.persona')),
            ],
        ),
        migrations.CreateModel(
            name='UsuarioXPoliticaContrasena',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.BooleanField(default=True)),
                ('politicaContrasena', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='usuarios.politicacontrasena')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='usuarios.usuario')),
            ],
        ),
        migrations.CreateModel(
            name='UsuarioXNotificacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.BooleanField(default=False)),
                ('notificacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='usuarios.notificacion')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='usuarios.usuario')),
            ],
        ),
        migrations.AddField(
            model_name='usuario',
            name='usuario_x_notificacion',
            field=models.ManyToManyField(through='usuarios.UsuarioXNotificacion', to='usuarios.Notificacion'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='usuario_x_politicaContrasena',
            field=models.ManyToManyField(through='usuarios.UsuarioXPoliticaContrasena', to='usuarios.PoliticaContrasena'),
        ),
    ]
