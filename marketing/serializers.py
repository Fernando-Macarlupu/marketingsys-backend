from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from marketing.models import *
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class EstrategiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estrategia
        fields = '__all__'

class CampanaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campana
        fields = '__all__'

class RecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recurso
        fields = '__all__'

class PropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propiedad
        fields = '__all__'

class FiltroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filtro
        fields = '__all__'

class VariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variable
        fields = '__all__'

class IndicadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicador
        fields = '__all__'

class IndicadorAsignadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorAsignado
        fields = '__all__'

class VariableXIndicadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariableXIndicador
        fields = '__all__'

class OportunidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Oportunidad
        fields = '__all__'

class OportunidadXContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OportunidadXContacto
        fields = '__all__'