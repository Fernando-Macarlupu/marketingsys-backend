from django.db import models
from usuarios.models import Persona, CuentaUsuario, Usuario

# Create your models here.

class Empresa(models.Model):
    tipo_choices = [
        ('0', 'Cliente potencial'),
        ('1', 'Socio'),
        ('2', 'Revendedor'),
        ('3', 'Proveedor'),
    ]
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50, null=True, blank=True)
    sector = models.CharField(max_length=50, null=True, blank=True)
    pais = models.CharField(max_length=50, null=True, blank=True)
    ciudad = models.CharField(max_length=50, null=True, blank=True)
    cantEmpleados = models.IntegerField(null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=tipo_choices, null=True, blank=True)
    propietario = models.ForeignKey(CuentaUsuario, on_delete=models.SET_NULL, null=True, blank=True)
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaModificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

class Contacto(models.Model):
    estado_choices = [
        ('0', 'Suscriptor'),
        ('1', 'Lead'),
        ('2', 'Oportunidad'),
        ('3', 'Cliente'),
    ]
    id = models.BigAutoField(primary_key=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True)
    calificado = models.BooleanField(default=False)
    estado = models.CharField(max_length=20, choices=estado_choices,null=True, blank=True)
    propietario = models.ForeignKey(CuentaUsuario, on_delete=models.SET_NULL, null=True, blank=True)
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaModificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.persona.nombreCompleto + "-" + self.estado


class ContactoXEmpresa(models.Model):
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.contacto.persona.nombreCompleto + "-" + self.empresa.nombre

class Lista(models.Model):
    objeto_choices = [
        ('0', 'Contacto'),
        ('1', 'Empresa'),
    ]
    tipo_choices = [
        ('0', 'Estática'),
        ('1', 'Activa'),
    ]
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50, null=True, blank=True)
    descripcion = models.CharField(max_length=100, null=True, blank=True)
    objeto = models.CharField(max_length=20, choices=objeto_choices, null=True, blank=True)  
    tipo = models.CharField(max_length=20, choices=tipo_choices, null=True, blank=True)
    tamano = models.IntegerField(null=True, blank=True)
    lista_x_contacto = models.ManyToManyField(Contacto, through='ListaXContacto')
    lista_x_empresa = models.ManyToManyField(Empresa, through='ListaXEmpresa')
    propietario = models.ForeignKey(CuentaUsuario, on_delete=models.SET_NULL, null=True, blank=True)
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaModificacion = models.DateTimeField(auto_now=True)

class Actividad(models.Model):
    tipo_choices = [
        ('0', 'Nota'),
        ('1', 'Correo'),
        ('2', 'Llamada'),
        ('3', 'Tarea'),
        ('4', 'Reunion'),
        ('5', 'Mensaje'),
    ]
    id = models.BigAutoField(primary_key=True)
    tipo = models.CharField(max_length=20, choices=tipo_choices, null=True, blank=True)
    titulo = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    fechaHora = models.DateTimeField(blank=True, null=True)
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaModificacion = models.DateTimeField(auto_now=True)

class Telefono(models.Model):
    id = models.BigAutoField(primary_key=True)
    numero = models.CharField(max_length=20, null=True, blank=True)
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    principal = models.BooleanField(default=False)

    def __str__(self):
        return self.numero

class Direccion(models.Model):
    id = models.BigAutoField(primary_key=True)
    pais = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=100, null=True, blank=True)
    ciudad = models.CharField(max_length=100, null=True, blank=True)
    direccion = models.CharField(max_length=100, null=True, blank=True)
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    principal = models.BooleanField(default=False)

    def __str__(self):
        return self.direccion

class CuentaCorreo(models.Model):
    servicio_choices = [
        ('0', 'Google'),
        ('1', 'Microsoft'),
    ]
    id = models.BigAutoField(primary_key=True)
    servicio = models.CharField(max_length=20, choices=servicio_choices, null=True, blank=True)
    direccion = models.CharField(max_length=50, null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.servicio + "-" + self.direccion

class CuentaRedSocial(models.Model):
    redes_choices = [
        ('0', 'Facebook'),
        ('1', 'Linkedin'),
        ('2', 'Twitter'),
        ('3', 'Instagram'),
    ]
    id = models.BigAutoField(primary_key=True)
    redSocial = models.CharField(max_length=20, choices=redes_choices, null=True, blank=True)
    nombreUsuario = models.CharField(max_length=50, null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.redSocial + "-" + self.nombreUsuario


# class ContactoXTelefono(models.Model):
#     contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, null=True, blank=True)
#     telefono = models.ForeignKey(Telefono, on_delete=models.CASCADE, null=True, blank=True)
#     principal = models.BooleanField(default=False)

# class ContactoXDireccion(models.Model):
#     contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, null=True, blank=True)
#     direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE, null=True, blank=True)
#     principal = models.BooleanField(default=False)

# class ContactoXCuentaCorreo(models.Model):
#     contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, null=True, blank=True)
#     cuentaCorreo = models.ForeignKey(CuentaCorreo, on_delete=models.CASCADE, null=True, blank=True)

# class ContactoXCuentaRedSocial(models.Model):
#     contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, null=True, blank=True)
#     cuentaRedSocial = models.ForeignKey(CuentaRedSocial, on_delete=models.CASCADE, null=True, blank=True)

class ListaXContacto(models.Model):
    lista = models.ForeignKey(Lista, on_delete=models.CASCADE, null=True, blank=True)
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, null=True, blank=True)

class ListaXEmpresa(models.Model):
    lista = models.ForeignKey(Lista, on_delete=models.CASCADE, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)

# class EmpresaXTelefono(models.Model):
#     empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
#     telefono = models.ForeignKey(Telefono, on_delete=models.CASCADE, null=True, blank=True)
#     principal = models.BooleanField(default=False)

# class EmpresaXCuentaCorreo(models.Model):
#     empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
#     cuentaCorreo = models.ForeignKey(CuentaCorreo, on_delete=models.CASCADE, null=True, blank=True)

# class EmpresaXCuentaRedSocial(models.Model):
#     empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
#     cuentaRedSocial = models.ForeignKey(CuentaRedSocial, on_delete=models.CASCADE, null=True, blank=True)