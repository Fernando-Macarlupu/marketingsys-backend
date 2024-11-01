from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from usuarios.models import *
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

class PoliticaContrasenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliticaContrasena
        fields = '__all__'

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'

class CuentaUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaUsuario
        fields = '__all__'

class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class UsuarioXPoliticaContrasenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioXPoliticaContrasena
        fields = '__all__'

class UsuarioXNotificacionContrasenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioXNotificacion
        fields = '__all__'

# class DynamicFieldsModelSerializer(serializers.ModelSerializer):
#     """
#     A ModelSerializer that takes an additional `fields` argument that
#     controls which fields should be displayed.
#     """

#     def __init__(self, *args, **kwargs):
#         # Don't pass the 'fields' arg up to the superclass
#         fields = kwargs.pop('fields', None)

#         # Instantiate the superclass normally
#         super().__init__(*args, **kwargs)

#         if fields is not None:
#             # Drop any fields that are not specified in the `fields` argument.
#             allowed = set(fields)
#             existing = set(self.fields)
#             for field_name in existing - allowed:
#                 self.fields.pop(field_name)


# class UserSerializerRead(DynamicFieldsModelSerializer, serializers.ModelSerializer):
#     class Meta:
#         model = User
#         depth = 1
#         fields = ['id', 'created', 'modified', 'is_active', 'username', 'first_name', 'second_name', 'last_name', 'maiden_name', 'email', 'password', 'roles']


# class UserSerializerWrite(DynamicFieldsModelSerializer, serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'created', 'modified', 'is_active', 'username', 'first_name', 'second_name', 'last_name', 'maiden_name', 'email', 'password', 'roles']
