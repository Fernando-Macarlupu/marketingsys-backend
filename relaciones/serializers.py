from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from relaciones.models import *
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed


class ActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = '__all__'
    
class TelefonoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telefono
        fields = '__all__'

class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = '__all__'

class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacto
        fields = '__all__'

class ContactoDetalleSerializer(serializers.ModelSerializer):
    persona_nombreCompleto = serializers.CharField(source='persona.nombreCompleto')
    propietario_nombre = serializers.CharField(source='propietario.nombre')
    class Meta:
        model = Contacto
        fields = ['id','persona','persona_nombreCompleto','calificado','estado', 'propietario','propietario_nombre' ,'fechaCreacion', 'fechaModificacion']

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'

class ContactoXEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactoXEmpresa
        fields = '__all__'

class ListaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lista
        fields = '__all__'

class CuentaCorreoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaCorreo
        fields = '__all__'

class CuentaRedSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaRedSocial
        fields = '__all__'

class ListaXContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaXContacto
        fields = '__all__'

class ListaXEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaXEmpresa
        fields = '__all__'