from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

admin.site.register(Persona)
admin.site.register(Usuario)
admin.site.register(CuentaUsuario)
admin.site.register(PoliticaContrasena)
admin.site.register(Notificacion)
admin.site.register(UsuarioXPoliticaContrasena)
admin.site.register(UsuarioXNotificacion)

class CustomUserAdmin(UserAdmin):
    def save_model(self, request, obj, form, change):
        # Hashear el password antes de guardarlo
        obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


# admin.site.register(User)
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)

# Register your models here.
