from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class PoliticaContrasena(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50, null=True, blank=True)

class Notificacion(models.Model):
    id = models.BigAutoField(primary_key=True)
    modulo = models.CharField(max_length=50, null=True, blank=True)

class CuentaUsuario(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    expiracionCuenta = models.DateTimeField(blank=True,null =True)
    diasExpiracioncuenta = models.IntegerField(blank=True,null =True)
    fechaCreacion = models.DateTimeField(blank=True,null =True)
    fechaModificacion = models.DateTimeField(blank=True,null =True)

class Persona(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombreCompleto = models.CharField(max_length=50, null=True, blank=True)
    fechaCreacion = models.DateTimeField(blank=True,null =True)
    fechaModificacion = models.DateTimeField(blank=True,null =True)

    def __str__(self):
        return self.nombreCompleto

class Usuario(models.Model):
    id = models.BigAutoField(primary_key=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, null=True, blank=True)
    nombreUsuario = models.CharField(max_length=50, null=True, blank=True)
    contrasena = models.CharField(max_length=50, null=True, blank=True)
    foto = models.TextField(null=True, blank=True) #url de la foto
    rol = models.CharField(max_length=50, null=True, blank=True)
    esAdministrador = models.BooleanField(default=True)
    cuentaUsuario = models.ForeignKey(CuentaUsuario, on_delete=models.SET_NULL, null=True, blank=True)
    usuario_x_politicaContrasena = models.ManyToManyField(PoliticaContrasena, through='UsuarioXPoliticaContrasena')
    usuario_x_notificacion = models.ManyToManyField(Notificacion, through='UsuarioXNotificacion')
    fechaCreacion = models.DateTimeField(blank=True,null =True)
    fechaModificacion = models.DateTimeField(blank=True,null =True)

# class UsuarioXCuentaCorreo(models.Model):
#     usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
#     cuentaCorreo = models.ForeignKey(CuentaCorreo, on_delete=models.CASCADE, null=True, blank=True)

# class UsuarioXCuentaRedSocial(models.Model):
#     usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
#     cuentaRedSocial = models.ForeignKey(CuentaRedSocial, on_delete=models.CASCADE, null=True, blank=True)

class UsuarioXPoliticaContrasena(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    politicaContrasena = models.ForeignKey(PoliticaContrasena, on_delete=models.CASCADE, null=True, blank=True)
    estado = models.BooleanField(default=True)

class UsuarioXNotificacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    notificacion = models.ForeignKey(Notificacion, on_delete=models.CASCADE, null=True, blank=True)
    estado = models.BooleanField(default=False)

# class User(AbstractUser, TimeStampedModel, SafeDeleteModel):
#     _safedelete_policy = SOFT_DELETE_CASCADE
#     email = models.EmailField(
#         verbose_name="email address",
#         max_length=255,
#         unique=True,
#     )
#     second_name = models.CharField(max_length=25)
#     maiden_name = models.CharField(max_length=25)
#     recovery_code = models.CharField(max_length=25, null=True, blank=True)
#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = ["username"]
#     # objects = CustomUserManager()

#     def __str__(self):
#         return self.first_name + " " + self.second_name

#     export_fields = [
#         'username',
#         'email',
#         'first_name',
#         'second_name',
#         'last_name',
#         'maiden_name'
#         'roles',
#         'is_active'
#     ]