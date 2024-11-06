from django.db import models
from usuarios.models import Persona, CuentaUsuario, Usuario
from relaciones.models import Lista, Contacto

# Create your models here.
class Plan(models.Model):
    estado_choices = [
        ('0', 'No vigente'),
        ('1', 'Vigente'),
    ]
    id = models.BigAutoField(primary_key=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    sponsor = models.CharField(max_length=50, null=True, blank=True)
    presupuesto = models.FloatField(null=True, blank=True)
    inicioVigencia = models.DateTimeField(blank=True,null =True)
    finVigencia = models.DateTimeField(blank=True,null =True)
    estado = models.CharField(max_length=20, choices=estado_choices, null=True, blank=True)
    propietario = models.ForeignKey(CuentaUsuario, on_delete=models.SET_NULL, null=True, blank=True)
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaModificacion = models.DateTimeField(auto_now=True)

class Estrategia(models.Model):
    tipo_choices = [
        ('0', 'Programa'),
        ('1', 'Campaña stand-alone'),
    ]
    estado_choices = [
        ('0', 'No vigente'),
        ('1', 'Vigente'),
    ]
    id = models.BigAutoField(primary_key=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=tipo_choices, null=True, blank=True)
    sponsor = models.CharField(max_length=50, null=True, blank=True)
    presupuesto = models.FloatField(null=True, blank=True)
    inicioVigencia = models.DateTimeField(blank=True,null =True)
    finVigencia = models.DateTimeField(blank=True,null =True)
    estado = models.CharField(max_length=20, choices=estado_choices, null=True, blank=True)
    leads = models.ForeignKey(Lista, on_delete=models.SET_NULL, null=True, blank=True)
    propietario = models.ForeignKey(CuentaUsuario, on_delete=models.SET_NULL, null=True, blank=True)
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaModificacion = models.DateTimeField(auto_now=True)

class Campana(models.Model):
    tipo_choices = [
        ('0', 'Campaña de programa'),
        ('1', 'Campaña stand-alone'),
    ]
    estado_choices = [
        ('0', 'No vigente'),
        ('1', 'Vigente'),
    ]
    id = models.BigAutoField(primary_key=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    estrategia = models.ForeignKey(Estrategia, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=tipo_choices, null=True, blank=True)
    sponsor = models.CharField(max_length=50, null=True, blank=True)
    presupuesto = models.FloatField(null=True, blank=True)
    inicioVigencia = models.DateTimeField(blank=True,null =True)
    finVigencia = models.DateTimeField(blank=True,null =True)
    estado = models.CharField(max_length=20, choices=estado_choices, null=True, blank=True)
    leads = models.ForeignKey(Lista, on_delete=models.SET_NULL, null=True, blank=True)
    propietario = models.ForeignKey(CuentaUsuario, on_delete=models.SET_NULL, null=True, blank=True)
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaModificacion = models.DateTimeField(auto_now=True)

class Recurso(models.Model):
    tipo_choices = [
        ('0', 'Correo'),
        ('1', 'Publicación'),
        ('2', 'Página web'),
    ]
    estado_choices = [
        ('0', 'No vigente'),
        ('1', 'Vigente'),
    ]
    redes_choices = [
        ('0', 'Facebook'),
        ('1', 'Linkedin'),
        ('2', 'Twitter'),
        ('3', 'Instagram'),
    ]
    audiencia_choices = [
        ('0', 'Público en general'),
        ('1', 'Seguidores'),
    ]
    id = models.BigAutoField(primary_key=True)
    campana = models.ForeignKey(Campana, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=tipo_choices, null=True, blank=True)
    presupuesto = models.FloatField(null=True, blank=True)
    inicioVigencia = models.DateTimeField(blank=True,null =True)
    finVigencia = models.DateTimeField(blank=True,null =True)
    estado = models.CharField(max_length=20, choices=estado_choices, null=True, blank=True)
    fechaPublicacion = models.DateTimeField(blank=True,null =True)

    asuntoCorreo = models.TextField(null=True, blank=True)
    remitenteCorreo = models.CharField(max_length=50, null=True, blank=True)

    servicioRedSocial = models.CharField(max_length=20, choices=redes_choices, null=True, blank=True)
    usuarioRedSocial = models.CharField(max_length=50, null=True, blank=True)
    audienciaRedSocial = models.CharField(max_length=20, choices=audiencia_choices, null=True, blank=True)

    titulo = models.TextField(null=True, blank=True)
    dominio = models.TextField(null=True, blank=True)
    complementoDominio = models.TextField(null=True, blank=True)

    contenido = models.TextField(null=True, blank=True)
    propietario = models.ForeignKey(CuentaUsuario, on_delete=models.SET_NULL, null=True, blank=True)
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaModificacion = models.DateTimeField(auto_now=True)

class Propiedad(models.Model):
    tipo_choices = [
        ('0', 'int'),
        ('1', 'string'),
        ('2', 'date'),
        ('3', 'bool'),
        ('4', 'double'),
    ]
    id = models.BigAutoField(primary_key=True)
    entidad = models.CharField(max_length=50, null=True, blank=True)
    propiedad = models.CharField(max_length=50, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=tipo_choices, null=True, blank=True)

class Filtro(models.Model):
    evaluacion_choices = [
        ('0', 'Igual'),
        ('1', 'Menor'),
        ('2', 'Mayor'),
        ('3', 'Menor o igual'),
        ('4', 'Mayor o igual'),
        ('5', 'Contiene'),
    ]
    id = models.BigAutoField(primary_key=True)
    lista = models.ForeignKey(Lista, on_delete=models.CASCADE, null=True, blank=True)
    propiedad = models.CharField(max_length=200, null=True, blank=True) #ver si se cambio por foreign key a propiedad
    #fidReporte
    evaluacion = models.CharField(max_length=20, choices=evaluacion_choices, null=True, blank=True)
    valorEvaluacion = models.CharField(max_length=200, null=True, blank=True)

class Variable(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=200, null=True, blank=True)
    abreviatura = models.CharField(max_length=10, null=True, blank=True)
    aspecto = models.CharField(max_length=50, null=True, blank=True)
    tipo = models.CharField(max_length=50, null=True, blank=True)
    automatica = models.BooleanField(default=False)

class Indicador(models.Model):
    aspecto_choices = [
        ('0', 'Plan'),
        ('1', 'Estrategia'),
        ('2', 'Campaña'),
        ('3', 'Recurso'),
    ]
    tipo_choices = [
        ('0', 'Programa'),
        ('1', 'Campaña stand-alone'),
        ('2', 'Campaña de programa'),
        ('3', 'Campaña stand-alone'),
        ('4', 'Correo'),
        ('5', 'Publicación'),
        ('6', 'Página web'),
    ]
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    formula = models.TextField(null=True, blank=True)
    aspecto = models.CharField(max_length=20, choices=aspecto_choices, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=tipo_choices, null=True, blank=True)
    automatica = models.BooleanField(default=False)
    propietario = models.ForeignKey(CuentaUsuario, on_delete=models.SET_NULL, null=True, blank=True)
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaModificacion = models.DateTimeField(auto_now=True)

class IndicadorAsignado(models.Model):
    id = models.BigAutoField(primary_key=True)
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, null=True, blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True)
    estrategia = models.ForeignKey(Estrategia, on_delete=models.CASCADE, null=True, blank=True)
    campana = models.ForeignKey(Campana, on_delete=models.CASCADE, null=True, blank=True)
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE, null=True, blank=True)
    calculoAutomatico = models.BooleanField(default=False)

class VariableXIndicador(models.Model):
    id = models.BigAutoField(primary_key=True)
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE, null=True, blank=True)
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, null=True, blank=True)

class Oportunidad(models.Model):
    tipo_choices = [
        ('0', 'Negocio existente'),
        ('1', 'Nuevo negocio'),
    ]
    etapa_choices = [
        ('0', 'Calificación'),
        ('1', 'Necesidad de análisis'),
        ('2', 'Propuesta'),
        ('3', 'Negociación'),
        ('4', 'Perdida'),
        ('5', 'Ganada'),
    ]
    estado_choices = [
        ('0', 'No vigente'),
        ('1', 'Vigente'),
    ]
    id = models.BigAutoField(primary_key=True)
    campanaAsociada = models.ForeignKey(Campana, on_delete=models.SET_NULL, null=True, blank=True)
    campanaStandAloneAsociada = models.ForeignKey(Estrategia, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=tipo_choices, null=True, blank=True)
    etapa = models.CharField(max_length=20, choices=etapa_choices, null=True, blank=True)
    importe = models.FloatField(null=True, blank=True)
    oportunidad_x_contacto = models.ManyToManyField(Contacto, through='OportunidadXContacto')
    inicioVigencia = models.DateTimeField(blank=True,null =True)
    finVigencia = models.DateTimeField(blank=True,null =True)
    estado = models.CharField(max_length=20, choices=estado_choices, null=True, blank=True)
    propietario = models.ForeignKey(CuentaUsuario, on_delete=models.SET_NULL, null=True, blank=True)
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaModificacion = models.DateTimeField(auto_now=True)

class OportunidadXContacto(models.Model):
    oportunidad = models.ForeignKey(Oportunidad, on_delete=models.CASCADE, null=True, blank=True)
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, null=True, blank=True)