from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Contacto)
admin.site.register(Empresa)
admin.site.register(ContactoXEmpresa)
admin.site.register(Lista)
admin.site.register(Actividad)
admin.site.register(Telefono)
admin.site.register(Direccion)
admin.site.register(CuentaCorreo)
admin.site.register(CuentaRedSocial)
admin.site.register(ListaXContacto)
admin.site.register(ListaXEmpresa)