from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Plan)
admin.site.register(Estrategia)
admin.site.register(Campana)
admin.site.register(CampanaXContacto)
admin.site.register(Recurso)
admin.site.register(Oportunidad)
admin.site.register(Indicador)
admin.site.register(IndicadorAsignado)
admin.site.register(Variable)
admin.site.register(VariableXIndicador)
admin.site.register(Columna)
admin.site.register(Fila)