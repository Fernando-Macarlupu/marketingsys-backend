from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from sistema.models import *
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'