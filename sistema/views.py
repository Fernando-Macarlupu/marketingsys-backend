from django.shortcuts import render
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import datetime
from sistema.models import *
from sistema.serializers import *

# Create your views here.

class FiltrarLogs(APIView):
    def post(self, request,id=0):
        tipo = request.data["tipo"]
        fechaIni = request.data["fechaIni"]
        fechaFin = request.data["fechaFin"]
        idPropietario = int(request.data["propietario"])
        query = Q()
        query.add(Q(propietario__id=idPropietario), Q.AND)

        if(tipo != "" and tipo in ['0','1']):
            query.add(Q(tipo=tipo), Q.AND)
        if(fechaIni != ""):
            fecha  = datetime.datetime.strptime(fechaIni, '%d-%m-%Y').date()
            query.add(Q(fechaHora__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
        if(fechaFin != ""):
            fecha  = datetime.datetime.strptime(fechaFin, '%d-%m-%Y').date()
            query.add(Q(fechaHora__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
        
        logs = Log.objects.filter(query).values('id', 'tipo', 'codigo', 'fuente','descripcion', 'fechaHora')
        listaLogs = list(logs)
        for log in listaLogs:
            fechapub = log['fechaHora'].replace(tzinfo=None)
            log["fechaHora"] = datetime.datetime.strftime(fechapub, '%d-%m-%Y') + " " + str(fechapub.hour) + ":" + str(fechapub.minute) + ":" + str(fechapub.second)
        #poner el formato para mostrar contactos
        return Response(listaLogs, status = status.HTTP_200_OK)
