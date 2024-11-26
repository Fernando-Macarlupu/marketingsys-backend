from django.db import models
from usuarios.models import CuentaUsuario
# Create your models here.
# Create your models here.
class Log(models.Model):
    tipo_choices = [
        ('0', 'Actividad'),
        ('1', 'Error'),
    ]
    id = models.BigAutoField(primary_key=True)
    tipo = models.CharField(max_length=20, choices=tipo_choices, null=True, blank=True)
    codigo = models.CharField(max_length=100, null=True, blank=True)
    fuente = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    propietario = models.ForeignKey(CuentaUsuario, on_delete=models.SET_NULL, null=True, blank=True)
    fechaHora = models.DateTimeField(blank=True,null =True)