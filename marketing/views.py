from django.shortcuts import render
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import datetime
from marketing.models import *
from marketing.serializers import *
from relaciones.models import *
from relaciones.serializers import *

# Create your views here.

class FiltrarPlanes(APIView):
    def post(self, request,id=0):
        cadena = request.data["cadena"]
        estado = request.data["estado"]
        fechaHoy = request.data["fechaHoy"]
        fechaVigenciaIni = request.data["fechaVigenciaIni"]
        fechaVigenciaFin = request.data["fechaVigenciaFin"]
        idPropietario = int(request.data["propietario"])
        subquery1 = Q()
        subquery2 = Q()
        subquery3 = Q()

        subquery1.add(Q(propietario__id=idPropietario), Q.AND)

        if(cadena != ""):
            subquery1.add(Q(descripcion__contains=cadena), Q.AND)
        if(estado != "" and estado in ['0','1']):
            fecha  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
            subquery1.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            subquery1.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
        if(fechaVigenciaIni != ""):
            fecha  = datetime.datetime.strptime(fechaVigenciaIni, '%d-%m-%Y').date()
            subquery2.add(Q(inicioVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            subquery3.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
        if(fechaVigenciaFin != ""):
            fecha  = datetime.datetime.strptime(fechaVigenciaFin, '%d-%m-%Y').date()
            subquery2.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
            subquery3.add(Q(finVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
        
        planes = Plan.objects.filter(( (subquery2) | (subquery3)) & subquery1).values('id', 'descripcion', 'sponsor', 'presupuesto','estado', 'inicioVigencia', 'finVigencia')
        listaPlanes = list(planes)
        for plan in listaPlanes:
            fechaHoy  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
            fecha = datetime.datetime(fechaHoy.year,fechaHoy.month,fechaHoy.day, 0,0,0)
            inicioVigencia = plan['inicioVigencia'].replace(tzinfo=None)
            finVigencia = plan['finVigencia'].replace(tzinfo=None)
            if inicioVigencia <= fecha and finVigencia >= fecha:
                plan['estado'] = 'Vigente'
            else:
                plan['estado'] = 'No vigente'
            plan['inicioVigencia'] = datetime.datetime.strftime(plan['inicioVigencia'], '%d-%m-%Y')
            plan['finVigencia'] = datetime.datetime.strftime(plan['finVigencia'], '%d-%m-%Y')
        return Response(listaPlanes, status = status.HTTP_200_OK)

class RegistrarPlan(APIView):
    def post(self, request,id=0):
        if request.data["idPlan"] is not None and request.data["idPlan"]>0:
            idPlan = request.data["idPlan"]
            IndicadorAsignado.objects.filter(Q(plan__id = idPlan)).delete()
            indicadores = request.data["indicadores"]
            for indicador in indicadores:
                campos = {'indicador': indicador['id'],
                          'plan': idPlan
                        }
                indicador_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicador_serializer.is_valid():
                    indicador_serializer.save()
            plan = Plan.objects.filter(id=idPlan).first()
            estrategias = request.data["estrategias"]
            for estrategia in estrategias:
                if(estrategia['tipo']=='Programa'):
                    Estrategia.objects.filter(id=estrategia['id']).update(plan=plan)
                else:
                    Campana.objects.filter(id=estrategia['id']).update(plan=plan)
            campos_plan = {
                 'descripcion': request.data["descripcion"],
                 'sponsor': request.data["sponsor"],
                 'presupuesto': request.data["presupuesto"],
                 'inicioVigencia': request.data["inicioVigencia"],
                 'finVigencia': request.data["finVigencia"],
                 'estado': request.data["estado"],
                 'propietario': request.data["propietario"]
            }
            if(request.data["inicioVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["inicioVigencia"], '%d-%m-%Y').date()
                campos_plan['inicioVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)
            if(request.data["finVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["finVigencia"], '%d-%m-%Y').date()
                campos_plan['finVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)
            plan_serializer = PlanSerializer(plan, data=campos_plan)
            if plan_serializer.is_valid():
                plan_serializer.save()
        else:
            campos_plan = {
                 'descripcion': request.data["descripcion"],
                 'sponsor': request.data["sponsor"],
                 'presupuesto': request.data["presupuesto"],
                 'inicioVigencia': request.data["inicioVigencia"],
                 'finVigencia': request.data["finVigencia"],
                 'estado': request.data["estado"],
                 'propietario': request.data["propietario"]
            }
            if(request.data["inicioVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["inicioVigencia"], '%d-%m-%Y').date()
                campos_plan['inicioVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)
            if(request.data["finVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["finVigencia"], '%d-%m-%Y').date()
                campos_plan['finVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)
            plan_serializer = PlanSerializer(data=campos_plan)
            if plan_serializer.is_valid():
                idPlan = plan_serializer.save()
                idPlan = idPlan.id
            plan = Plan.objects.filter(id=idPlan).first()
            estrategias = request.data["estrategias"]
            for estrategia in estrategias:
                if(estrategia['tipo']=='Programa'):
                    Estrategia.objects.filter(id=estrategia['id']).update(plan=plan)
                else:
                    Campana.objects.filter(id=estrategia['id']).update(plan=plan)
            indicadores = request.data["indicadores"]
            for indicador in indicadores:
                campos = {'indicador': indicador['id'],
                          'plan': idPlan
                        }
                indicador_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicador_serializer.is_valid():
                    indicador_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'Plan registrado correctamente',
                        },)	

class FiltrarEstrategias(APIView):
    def post(self, request,id=0):
        cadena = request.data["cadena"]
        estado = request.data["estado"]
        fechaHoy = request.data["fechaHoy"]
        tipo = request.data["tipo"]
        fechaVigenciaIni = request.data["fechaVigenciaIni"]
        fechaVigenciaFin = request.data["fechaVigenciaFin"]
        idPropietario = int(request.data["propietario"])
        subquery1 = Q()
        subquery2 = Q()
        subquery3 = Q()

        subquery1.add(Q(propietario__id=idPropietario), Q.AND)

        if(cadena != ""):
            subquery1.add(Q(descripcion__contains=cadena), Q.AND)
        if(estado != "" and estado in ['0','1']):
            fecha  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
            subquery1.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            subquery1.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
        
        if(fechaVigenciaIni != ""):
            fecha  = datetime.datetime.strptime(fechaVigenciaIni, '%d-%m-%Y').date()
            subquery2.add(Q(inicioVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            subquery3.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
        if(fechaVigenciaFin != ""):
            fecha  = datetime.datetime.strptime(fechaVigenciaFin, '%d-%m-%Y').date()
            subquery2.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
            subquery3.add(Q(finVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
        
        listaEstrategias = []
        if (tipo ==""):
            programas = Estrategia.objects.filter(( (subquery2) | (subquery3)) & subquery1).values('id', 'descripcion', 'sponsor', 'presupuesto','estado', 'tipo','inicioVigencia', 'finVigencia')
            subquery1.add(Q(tipo='1'), Q.AND)
            campanas = Campana.objects.filter(( (subquery2) | (subquery3)) & subquery1).values('id', 'descripcion', 'sponsor', 'presupuesto','estado', 'tipo','inicioVigencia', 'finVigencia')
            listaEstrategias = list(programas) + list(campanas)
        elif (tipo == '0'):
            estrategias = Estrategia.objects.filter(( (subquery2) | (subquery3)) & subquery1).values('id', 'descripcion', 'sponsor', 'presupuesto','estado', 'tipo','inicioVigencia', 'finVigencia')
            listaEstrategias = list(estrategias)
        elif (tipo == '1'):
            subquery1.add(Q(tipo='1'), Q.AND)
            estrategias = Campana.objects.filter(( (subquery2) | (subquery3)) & subquery1).values('id', 'descripcion', 'sponsor', 'presupuesto','estado', 'tipo','inicioVigencia', 'finVigencia')
            listaEstrategias = list(estrategias)
        for estrategia in listaEstrategias:
            fechaHoy  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
            fecha = datetime.datetime(fechaHoy.year,fechaHoy.month,fechaHoy.day, 0,0,0)
            inicioVigencia = estrategia['inicioVigencia'].replace(tzinfo=None)
            finVigencia = estrategia['finVigencia'].replace(tzinfo=None)
            if inicioVigencia <= fecha and finVigencia >= fecha:
                estrategia['estado'] = 'Vigente'
            else:
                estrategia['estado'] = 'No vigente'
            if estrategia['tipo'] == '0':
                estrategia['tipo'] = 'Programa'
            elif estrategia['tipo'] == '1':
                estrategia['tipo'] = 'Campaña stand-alone'
            estrategia['inicioVigencia'] = datetime.datetime.strftime(estrategia['inicioVigencia'], '%d-%m-%Y')
            estrategia['finVigencia'] = datetime.datetime.strftime(estrategia['finVigencia'], '%d-%m-%Y')
        return Response(listaEstrategias, status = status.HTTP_200_OK)

class RegistrarEstrategia(APIView):
    def post(self, request,id=0):
        if request.data["idEstrategia"] is not None and request.data["idEstrategia"]>0:
            idEstrategia = request.data["idEstrategia"]
            IndicadorAsignado.objects.filter(Q(estrategia__id = idEstrategia)).delete()
            #ContactoXEstrategia.objects.filter(Q(estrategia__id = idEstrategia)).delete()
            indicadores = request.data["indicadores"]
            for indicador in indicadores:
                campos = {'indicador': indicador['id'],
                          'estrategia': idEstrategia
                        }
                indicador_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicador_serializer.is_valid():
                    indicador_serializer.save()
            contactos = request.data["contactos"]
            for contacto in contactos:
                campos = {'contacto': contacto['id'],
                          'estrategia': idEstrategia
                        }
                #contactoxestrategia_serializer = ContactoXEstrategiaSerializer(data = campos)
                #if contactoxestrategia_serializer.is_valid():
                #    contactoxestrategia_serializer.save()
            estrategia = Estrategia.objects.filter(id=idEstrategia).first()
            campos_estrategia = {
                 'descripcion': request.data["descripcion"],
                 'tipo': '0',
                 'sponsor': request.data["sponsor"],
                 'presupuesto': request.data["presupuesto"],
                 'inicioVigencia': request.data["inicioVigencia"],
                 'finVigencia': request.data["finVigencia"],
                 'estado': request.data["estado"],
                 'propietario': request.data["propietario"]
            }
            if(request.data["idPlan"] != "" and request.data["idPlan"]>0):
                campos_estrategia['plan'] = request.data["idPlan"]
            if(request.data["leads"] != "" and request.data["leads"]>0):
                campos_estrategia['leads'] = request.data["leads"]
            if(request.data["inicioVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["inicioVigencia"], '%d-%m-%Y').date()
                campos_estrategia['inicioVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)
            if(request.data["finVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["finVigencia"], '%d-%m-%Y').date()
                campos_estrategia['finVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)
            estrategia_serializer = EstrategiaSerializer(estrategia, data=campos_estrategia)
            if estrategia_serializer.is_valid():
                estrategia_serializer.save()
        else:
            campos_estrategia = {
                 'descripcion': request.data["descripcion"],
                 'tipo': '0',
                 'sponsor': request.data["sponsor"],
                 'presupuesto': request.data["presupuesto"],
                 'inicioVigencia': request.data["inicioVigencia"],
                 'finVigencia': request.data["finVigencia"],
                 'estado': request.data["estado"],
                 'propietario': request.data["propietario"]
            }
            if(request.data["idPlan"] != "" and request.data["idPlan"]>0):
                campos_estrategia['plan'] = request.data["idPlan"]
            if(request.data["leads"] != "" and request.data["leads"]>0):
                campos_estrategia['leads'] = request.data["leads"]
            if(request.data["inicioVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["inicioVigencia"], '%d-%m-%Y').date()
                campos_estrategia['inicioVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)
            if(request.data["finVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["finVigencia"], '%d-%m-%Y').date()
                campos_estrategia['finVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)
            estrategia_serializer = EstrategiaSerializer(data=campos_estrategia)
            if estrategia_serializer.is_valid():
                idEstrategia = estrategia_serializer.save()
                idEstrategia = idEstrategia.id
            contactos = request.data["contactos"]
            for contacto in contactos:
                campos = {'contacto': contacto['id'],
                          'estrategia': idEstrategia
                        }
                #contactoxestrategia_serializer = ContactoXEstrategiaSerializer(data = campos)
                #if contactoxestrategia_serializer.is_valid():
                #    contactoxestrategia_serializer.save()
            indicadores = request.data["indicadores"]
            for indicador in indicadores:
                campos = {'indicador': indicador['id'],
                          'estrategia': idEstrategia
                        }
                indicador_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicador_serializer.is_valid():
                    indicador_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'Estrategia registrada correctamente',
                        },)	

class FiltrarCampanas(APIView):
    def post(self, request,id=0):
        cadena = request.data["cadena"]
        estado = request.data["estado"]
        fechaHoy = request.data["fechaHoy"]
        tipo = request.data["tipo"]
        fechaVigenciaIni = request.data["fechaVigenciaIni"]
        fechaVigenciaFin = request.data["fechaVigenciaFin"]
        idPropietario = int(request.data["propietario"])
        subquery1 = Q()
        subquery2 = Q()
        subquery3 = Q()

        subquery1.add(Q(propietario__id=idPropietario), Q.AND)

        if(cadena != ""):
            subquery1.add(Q(descripcion__contains=cadena), Q.AND)
        if(estado != "" and estado in ['0','1']):
            fecha  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
            subquery1.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            subquery1.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
        if(tipo != "" and tipo in ['0','1']):
            subquery1.add(Q(tipo=tipo), Q.AND)
        if(fechaVigenciaIni != ""):
            fecha  = datetime.datetime.strptime(fechaVigenciaIni, '%d-%m-%Y').date()
            subquery2.add(Q(inicioVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            subquery3.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
        if(fechaVigenciaFin != ""):
            fecha  = datetime.datetime.strptime(fechaVigenciaFin, '%d-%m-%Y').date()
            subquery2.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
            subquery3.add(Q(finVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
        
        campanas = Campana.objects.filter(( (subquery2) | (subquery3)) & subquery1).values('id', 'descripcion', 'presupuesto','estado', 'tipo','inicioVigencia', 'finVigencia')
        listaCampanas = list(campanas)
        for campana in listaCampanas:
            fechaHoy  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
            fecha = datetime.datetime(fechaHoy.year,fechaHoy.month,fechaHoy.day, 0,0,0)
            inicioVigencia = campana['inicioVigencia'].replace(tzinfo=None)
            finVigencia = campana['finVigencia'].replace(tzinfo=None)
            if inicioVigencia <= fecha and finVigencia >= fecha:
                campana['estado'] = 'Vigente'
            else:
                campana['estado'] = 'No vigente'
            if campana['tipo'] == '0':
                campana['tipo'] = 'Campaña de programa'
            elif campana['tipo'] == '1':
                campana['tipo'] = 'Campaña stand-alone'
            campana['inicioVigencia'] = datetime.datetime.strftime(campana['inicioVigencia'], '%d-%m-%Y')
            campana['finVigencia'] = datetime.datetime.strftime(campana['finVigencia'], '%d-%m-%Y')
        return Response(listaCampanas, status = status.HTTP_200_OK)

class RegistrarCampana(APIView):
    def post(self, request,id=0):
        if request.data["idCampana"] is not None and request.data["idCampana"]>0:
            idCampana = request.data["idCampana"]
            IndicadorAsignado.objects.filter(Q(campana__id = idCampana)).delete()
            #ContactoXCampana.objects.filter(Q(campana__id = idCampana)).delete()
            indicadores = request.data["indicadores"]
            for indicador in indicadores:
                campos = {'indicador': indicador['id'],
                          'campana': idCampana
                        }
                indicador_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicador_serializer.is_valid():
                    indicador_serializer.save()
            contactos = request.data["contactos"]
            for contacto in contactos:
                campos = {'contacto': contacto['id'],
                          'campana': idCampana
                        }
                #contactoxcampana_serializer = ContactoXCampanaSerializer(data = campos)
                #if contactoxcampana_serializer.is_valid():
                #    contactoxcampana_serializer.save()
            campana = Campana.objects.filter(id=idCampana).first()
            campos_campana = {
                'tipo': request.data["tipo"],
                 'descripcion': request.data["descripcion"],
                 'sponsor': request.data["sponsor"],
                 'presupuesto': request.data["presupuesto"],
                 'inicioVigencia': request.data["inicioVigencia"],
                 'finVigencia': request.data["finVigencia"],
                 'estado': request.data["estado"],
                 'propietario': request.data["propietario"]
            }
            if(request.data["leads"] != "" and request.data["leads"]>0):
                campos_campana['leads'] = request.data["leads"]
            if(request.data['idPlan']> 0 and request.data['idPlan'] != ""): campos_campana['plan'] = request.data['idPlan']
            elif(request.data['idEstrategia']> 0 and request.data['idEstrategia'] != ""): campos_campana['estrategia'] = request.data['idEstrategia']
            
            if(request.data["inicioVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["inicioVigencia"], '%d-%m-%Y').date()
                campos_campana['inicioVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)
            if(request.data["finVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["finVigencia"], '%d-%m-%Y').date()
                campos_campana['finVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)
            campana_serializer = CampanaSerializer(campana, data=campos_campana)
            if campana_serializer.is_valid():
                campana_serializer.save()
        else:
            campos_campana = {
                'tipo': request.data["tipo"],
                 'descripcion': request.data["descripcion"],
                 'sponsor': request.data["sponsor"],
                 'presupuesto': request.data["presupuesto"],
                 'inicioVigencia': request.data["inicioVigencia"],
                 'finVigencia': request.data["finVigencia"],
                 'estado': request.data["estado"],
                 'propietario': request.data["propietario"]
            }
            if(request.data["leads"] != "" and request.data["leads"]>0):
                campos_campana['leads'] = request.data["leads"]
            if(request.data['idPlan']> 0 and request.data['idPlan'] != ""): campos_campana['plan'] = request.data['idPlan']
            elif(request.data['idEstrategia']> 0 and request.data['idEstrategia'] != ""): campos_campana['estrategia'] = request.data['idEstrategia']
            
            if(request.data["inicioVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["inicioVigencia"], '%d-%m-%Y').date()
                campos_campana['inicioVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)
            if(request.data["finVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["finVigencia"], '%d-%m-%Y').date()
                campos_campana['finVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)
            campana_serializer = CampanaSerializer(data=campos_campana)
            if campana_serializer.is_valid():
                idCampana = campana_serializer.save()
                idCampana = idCampana.id
            contactos = request.data["contactos"]
            for contacto in contactos:
                campos = {'contacto': contacto['id'],
                          'campana': idCampana
                        }
                #contactoxcampana_serializer = ContactoXCampanaSerializer(data = campos)
                #if contactoxcampana_serializer.is_valid():
                #    contactoxcampana_serializer.save()
            indicadores = request.data["indicadores"]
            for indicador in indicadores:
                campos = {'indicador': indicador['id'],
                          'campana': idCampana
                        }
                indicador_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicador_serializer.is_valid():
                    indicador_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'Campaña registrada correctamente',
                        },)	

class FiltrarRecursos(APIView):
    def post(self, request,id=0):
        cadena = request.data["cadena"]
        estado = request.data["estado"]
        fechaHoy = request.data["fechaHoy"]
        tipo = request.data["tipo"]
        fechaVigenciaIni = request.data["fechaVigenciaIni"]
        fechaVigenciaFin = request.data["fechaVigenciaFin"]
        idPropietario = int(request.data["propietario"])
        subquery1 = Q()
        subquery2 = Q()
        subquery3 = Q()

        subquery1.add(Q(propietario__id=idPropietario), Q.AND)

        if(cadena != ""):
            subquery1.add(Q(descripcion__contains=cadena), Q.AND)
        if(estado != "" and estado in ['0','1']):
            fecha  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
            subquery1.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            subquery1.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
        if(tipo != "" and tipo in ['0','1','2']):
            subquery1.add(Q(tipo=tipo), Q.AND)
        if(fechaVigenciaIni != ""):
            fecha  = datetime.datetime.strptime(fechaVigenciaIni, '%d-%m-%Y').date()
            subquery2.add(Q(inicioVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            subquery3.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
        if(fechaVigenciaFin != ""):
            fecha  = datetime.datetime.strptime(fechaVigenciaFin, '%d-%m-%Y').date()
            subquery2.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
            subquery3.add(Q(finVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
        
        recursos = Recurso.objects.filter(( (subquery2) | (subquery3)) & subquery1).values('id', 'descripcion', 'presupuesto','estado', 'tipo', 'inicioVigencia', 'finVigencia')
        listaRecursos = list(recursos)
        for recurso in listaRecursos:
            fechaHoy  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
            fecha = datetime.datetime(fechaHoy.year,fechaHoy.month,fechaHoy.day, 0,0,0)
            inicioVigencia = recurso['inicioVigencia'].replace(tzinfo=None)
            finVigencia = recurso['finVigencia'].replace(tzinfo=None)
            if inicioVigencia <= fecha and finVigencia >= fecha:
                recurso['estado'] = 'Vigente'
            else:
                recurso['estado'] = 'No vigente'
            if recurso['tipo'] == '0':
                recurso['tipo'] = 'Correo'
            elif recurso['tipo'] == '1':
                recurso['tipo'] = 'Publicación'
            elif recurso['tipo'] == '2':
                recurso['tipo'] = 'Página web'
            recurso['inicioVigencia'] = datetime.datetime.strftime(recurso['inicioVigencia'], '%d-%m-%Y')
            recurso['finVigencia'] = datetime.datetime.strftime(recurso['finVigencia'], '%d-%m-%Y')
        return Response(listaRecursos, status = status.HTTP_200_OK)

class RegistrarRecurso(APIView):
    def post(self, request,id=0):
        if request.data["idRecurso"] is not None and request.data["idRecurso"]>0:
            idRecurso = request.data["idRecurso"]
            IndicadorAsignado.objects.filter(Q(recurso__id = idRecurso)).delete()
            #ContactoXRecurso.objects.filter(Q(recurso__id = idRecurso)).delete()
            indicadores = request.data["indicadores"]
            for indicador in indicadores:
                campos = {'indicador': indicador['id'],
                          'recurso': idRecurso
                        }
                indicador_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicador_serializer.is_valid():
                    indicador_serializer.save()
            #contactos = request.data["contactos"]
            #for contacto in contactos:
            #    campos = {'contacto': contacto['id'],
            #              'estrategia': idRecurso
            #            }
                #contactoxestrategia_serializer = ContactoXEstrategiaSerializer(data = campos)
                #if contactoxestrategia_serializer.is_valid():
                #    contactoxestrategia_serializer.save()
            recurso = Recurso.objects.filter(id=idRecurso).first()
            campos_recurso = {
                 'descripcion': request.data["descripcion"],
                 'tipo': request.data["tipo"],
                 'presupuesto': request.data["presupuesto"],
                 'inicioVigencia': request.data["inicioVigencia"],
                 'finVigencia': request.data["finVigencia"],
                 'estado': request.data["estado"],
                 'propietario': request.data["propietario"]
                 #falta poner los datos dependiendo del tipo
            }
            if(request.data['idCampana']> 0 and request.data['idCampana'] != ""): campos_recurso['campana'] = request.data['idCampana']
            if(request.data["inicioVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["inicioVigencia"], '%d-%m-%Y').date()
                campos_recurso['inicioVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)
            if(request.data["finVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["finVigencia"], '%d-%m-%Y').date()
                campos_recurso['finVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)
            recurso_serializer = RecursoSerializer(recurso, data=campos_recurso)
            if recurso_serializer.is_valid():
                recurso_serializer.save()
        else:
            campos_recurso = {
                 'descripcion': request.data["descripcion"],
                 'tipo': request.data["tipo"],
                 'presupuesto': request.data["presupuesto"],
                 'inicioVigencia': request.data["inicioVigencia"],
                 'finVigencia': request.data["finVigencia"],
                 'estado': request.data["estado"],
                 'propietario': request.data["propietario"]
                 #falta poner los datos dependiendo del tipo
            }
            if(request.data['idCampana']> 0 and request.data['idCampana'] != ""): campos_recurso['campana'] = request.data['idCampana']
            if(request.data["inicioVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["inicioVigencia"], '%d-%m-%Y').date()
                campos_recurso['inicioVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)
            if(request.data["finVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["finVigencia"], '%d-%m-%Y').date()
                campos_recurso['finVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)
            recurso_serializer = RecursoSerializer(recurso, data=campos_recurso)
            if recurso_serializer.is_valid():
                idRecurso = recurso_serializer.save()
                idRecurso = idRecurso.id
            #contactos = request.data["contactos"]
            #for contacto in contactos:
            #    campos = {'contacto': contacto['id'],
            #              'estrategia': idRecurso
            #            }
                #contactoxestrategia_serializer = ContactoXEstrategiaSerializer(data = campos)
                #if contactoxestrategia_serializer.is_valid():
                #    contactoxestrategia_serializer.save()
            indicadores = request.data["indicadores"]
            for indicador in indicadores:
                campos = {'indicador': indicador['id'],
                          'recurso': idRecurso
                        }
                indicador_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicador_serializer.is_valid():
                    indicador_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'Recurso registrado correctamente',
                        },)	

class FiltrarPropiedades(APIView):
    def post(self, request,id=0):
        entidades = request.data["entidades"]
        query = Q()
        for entidad in entidades:
            query.add(Q(entidad=entidad), Q.OR)
        propiedades = Propiedad.objects.filter(query).values('id', 'entidad','propiedad','tipo')
        listaPropiedades = list(propiedades)
        return Response(listaPropiedades, status = status.HTTP_200_OK)

class FiltrarVariables(APIView):
    def post(self, request,id=0):
        cadena = request.data["cadena"]
        aspecto = request.data["cadena"]
        tipo = request.data["cadena"]
        query = Q()
        if (cadena != ""):
            query.add(Q(nombre__contains=cadena), Q.AND)
        if (aspecto != ""):
            query.add(Q(aspecto=aspecto), Q.AND)
        if (tipo != ""):
            query.add(Q(tipo=tipo), Q.AND)
        variables = Variable.objects.filter(query).values('id', 'nombre','aspecto','tipo','automatica')
        listaVariables = list(variables)
        for variable in listaVariables:
            if variable['automatica'] == True:
                variable['automatica'] = 'Sí'
            else:
                variable['automatica'] = 'No'
        return Response(listaVariables, status = status.HTTP_200_OK)

class RegistrarIndicador(APIView):
    def post(self, request,id=0):
        if request.data["idIndicador"] is not None and request.data["idIndicador"]>0:
            idIndicador = request.data["idIndicador"]
            VariableXIndicador.objects.filter(Q(indicador__id = idIndicador)).delete()
            IndicadorAsignado.objects.filter(Q(indicador__id = idIndicador)).delete()
            variables = request.data["variables"]
            for variable in variables:
                campos = {'variable': variable['id'],
                          'indicador': idIndicador
                        }
                variablexindicador_serializer = VariableXIndicadorSerializer(data = campos)
                if variablexindicador_serializer.is_valid():
                    variablexindicador_serializer.save()
            indicador = Indicador.objects.filter(id=idIndicador).first()
            campos_indicador = {
                'nombre': request.data['nombre'],
                 'descripcion': request.data["descripcion"],
                 'formula': request.data["formula"],
                 'aspecto': request.data["aspecto"],
                 'tipo': request.data["tipo"],
                 'automatica': request.data["automatica"],
                 'propietario': request.data["propietario"]
            }
            indicador_serializer = IndicadorSerializer(indicador, data=campos_indicador)
            if indicador_serializer.is_valid():
                indicador_serializer.save()
            #falta guardar las asignaciones
        else:
            campos_indicador = {
                'nombre': request.data['nombre'],
                 'descripcion': request.data["descripcion"],
                 'formula': request.data["formula"],
                 'aspecto': request.data["aspecto"],
                 'tipo': request.data["tipo"],
                 'automatica': request.data["automatica"],
                 'propietario': request.data["propietario"]
            }
            indicador_serializer = IndicadorSerializer(data=campos_indicador)
            if indicador_serializer.is_valid():
                idIndicador = indicador_serializer.save()
                idIndicador = idIndicador.id
            variables = request.data["variables"]
            for variable in variables:
                campos = {'variable': variable['id'],
                          'indicador': idIndicador
                        }
                variablexindicador_serializer = VariableXIndicadorSerializer(data = campos)
                if variablexindicador_serializer.is_valid():
                    variablexindicador_serializer.save()
            #falta guardar las asignaciones
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'Indicador registrado correctamente',
                        },)	

class FiltrarIndicadores(APIView):
    def post(self, request,id=0):
        cadena = request.data["cadena"]
        aspecto = request.data["aspecto"]
        tipo = request.data["tipo"]
        fechaCreacionIni = request.data["fechaCreacionIni"]
        fechaCreacionFin = request.data["fechaCreacionFin"]
        fechaModificacionIni = request.data["fechaModificacionIni"]
        fechaModificacionFin = request.data["fechaModificacionFin"]
        idPropietario = int(request.data["propietario"])
        query = Q()
        subquery1 = Q()
        subquery3 = Q()

        query.add(Q(propietario__id=idPropietario), Q.AND)

        if (cadena != ""):
            subquery1.add(Q(nombre__contains=cadena), Q.OR)
            subquery3.add(Q(descripcion__contains=cadena), Q.OR)
        if (aspecto != "" and aspecto in ['0','1','2','3']):
            query.add(Q(aspecto=aspecto), Q.AND)
        if (tipo != "" and tipo in ['0','1','2','3','4','5','6']):
            query.add(Q(tipo=tipo), Q.AND)
        if(fechaCreacionIni != ""):
            fecha  = datetime.datetime.strptime(fechaCreacionIni, '%d-%m-%Y').date()
            query.add(Q(fechaCreacion__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
        if(fechaCreacionFin != ""):
            fecha  = datetime.datetime.strptime(fechaCreacionFin, '%d-%m-%Y').date()
            query.add(Q(fechaCreacion__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
        if(fechaModificacionIni != ""):
            fecha  = datetime.datetime.strptime(fechaModificacionIni, '%d-%m-%Y').date()
            query.add(Q(fechaModificacion__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
        if(fechaModificacionFin != ""):
            fecha  = datetime.datetime.strptime(fechaModificacionFin, '%d-%m-%Y').date()
            query.add(Q(fechaModificacion__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
        
        indicadores = Indicador.objects.filter((subquery1 | subquery3) & query).values('id', 'nombre','fechaCreacion', 'fechaModificacion','aspecto','tipo')
        listaIndicadores = list(indicadores)
        for indicador in listaIndicadores:
            indicador['fechaCreacion'] = datetime.datetime.strftime(indicador['fechaCreacion'], '%d-%m-%Y')
            indicador['fechaModificacion'] = datetime.datetime.strftime(indicador['fechaModificacion'], '%d-%m-%Y')
        return Response(listaIndicadores, status = status.HTTP_200_OK)

class FiltrarOportunidades(APIView):
    def post(self, request,id=0):
        cadena = request.data["cadena"]
        estado = request.data["estado"]
        fechaHoy = request.data["fechaHoy"]
        etapa = request.data["etapa"]
        fechaVigenciaIni = request.data["fechaVigenciaIni"]
        fechaVigenciaFin = request.data["fechaVigenciaFin"]
        idPropietario = int(request.data["propietario"])
        subquery1 = Q()
        subquery2 = Q()
        subquery3 = Q()

        subquery1.add(Q(propietario__id=idPropietario), Q.AND)

        if(cadena != ""):
            subquery1.add(Q(descripcion__contains=cadena), Q.AND)
        if(estado != "" and estado in ['0','1']):
            fecha  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
            subquery1.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            subquery1.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
        if(etapa != "" and etapa in ['0','1','2','3','4','5']):
            subquery1.add(Q(etapa=etapa), Q.AND)
        if(fechaVigenciaIni != ""):
            fecha  = datetime.datetime.strptime(fechaVigenciaIni, '%d-%m-%Y').date()
            subquery2.add(Q(inicioVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            subquery3.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
        if(fechaVigenciaFin != ""):
            fecha  = datetime.datetime.strptime(fechaVigenciaFin, '%d-%m-%Y').date()
            subquery2.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
            subquery3.add(Q(finVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
        
        oportunidades = Oportunidad.objects.filter(( (subquery2) | (subquery3)) & subquery1).values('id', 'descripcion', 'estado', 'etapa', 'inicioVigencia', 'finVigencia')
        listaOportunidades = list(oportunidades)
        for oportunidad in listaOportunidades:
            fechaHoy  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
            fecha = datetime.datetime(fechaHoy.year,fechaHoy.month,fechaHoy.day, 0,0,0)
            inicioVigencia = oportunidad['inicioVigencia'].replace(tzinfo=None)
            finVigencia = oportunidad['finVigencia'].replace(tzinfo=None)
            if inicioVigencia <= fecha and finVigencia >= fecha:
                oportunidad['estado'] = 'Vigente'
            else:
                oportunidad['estado'] = 'No vigente'
            if oportunidad['etapa'] == '0':
                oportunidad['etapa'] = 'Calificación'
            elif oportunidad['etapa'] == '1':
                oportunidad['etapa'] = 'Necesidad de análisis'
            elif oportunidad['etapa'] == '2':
                oportunidad['etapa'] = 'Propuesta'
            elif oportunidad['etapa'] == '3':
                oportunidad['etapa'] = 'Negociación'
            elif oportunidad['etapa'] == '4':
                oportunidad['etapa'] = 'Perdida'
            elif oportunidad['etapa'] == '5':
                oportunidad['etapa'] = 'Ganada'
            oportunidad['inicioVigencia'] = datetime.datetime.strftime(oportunidad['inicioVigencia'], '%d-%m-%Y')
            oportunidad['finVigencia'] = datetime.datetime.strftime(oportunidad['finVigencia'], '%d-%m-%Y')
        return Response(listaOportunidades, status = status.HTTP_200_OK)
    
class RegistrarOportunidad(APIView):
    def post(self, request,id=0):
        if request.data["idOportunidad"] is not None and request.data["idOportunidad"]>0:
            idOportunidad = request.data["idOportunidad"]
            OportunidadXContacto.objects.filter(Q(oportunidad__id = idOportunidad)).delete()
            contactos = request.data["contactos"]
            for contacto in contactos:
                campos = {'contacto': contacto['id'],
                          'oportunidad': idOportunidad
                        }
                contactoxoportunidad_serializer = OportunidadXContactoSerializer(data = campos)
                if contactoxoportunidad_serializer.is_valid():
                    contactoxoportunidad_serializer.save()
            oportunidad = Oportunidad.objects.filter(id=idOportunidad).first()
            campos_oportunidad = {
                 'descripcion': request.data["descripcion"],
                 'tipo': request.data["tipo"],
                 'etapa': request.data["etapa"],
                 'importe': request.data["importe"],
                 'inicioVigencia': request.data["inicioVigencia"],
                 'finVigencia': request.data["finVigencia"],
                 'estado': request.data["estado"],
                 'propietario': request.data["propietario"],
                 'campanaStandAloneAsociada': request.data["idEstrategia"],
                 'campanaAsociada': request.data["idCampana"]
            }
            if(request.data["idEstrategia"] != ""):
                campos_oportunidad['campanaStandAloneAsociada'] = request.data["idEstrategia"]
            if(request.data["idCampana"] != ""):
                campos_oportunidad['campanaAsociada'] = request.data["idCampana"]
            if(request.data["inicioVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["inicioVigencia"], '%d-%m-%Y').date()
                campos_oportunidad['inicioVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)
            if(request.data["finVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["finVigencia"], '%d-%m-%Y').date()
                campos_oportunidad['finVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)
            oportunidad_serializer = OportunidadSerializer(oportunidad, data=campos_oportunidad)
            if oportunidad_serializer.is_valid():
                oportunidad_serializer.save()
        else:
            campos_oportunidad = {
                 'descripcion': request.data["descripcion"],
                 'tipo': request.data["tipo"],
                 'etapa': request.data["etapa"],
                 'importe': request.data["importe"],
                 'inicioVigencia': request.data["inicioVigencia"],
                 'finVigencia': request.data["finVigencia"],
                 'estado': request.data["estado"],
                 'propietario': request.data["propietario"],
                 'campanaStandAloneAsociada': request.data["idEstrategia"],
                 'campanaAsociada': request.data["idCampana"]
            }
            if(request.data["idEstrategia"] != ""):
                campos_oportunidad['campanaStandAloneAsociada'] = request.data["idEstrategia"]
            if(request.data["idCampana"] != ""):
                campos_oportunidad['campanaAsociada'] = request.data["idCampana"]
            if(request.data["inicioVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["inicioVigencia"], '%d-%m-%Y').date()
                campos_oportunidad['inicioVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)
            if(request.data["finVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["finVigencia"], '%d-%m-%Y').date()
                campos_oportunidad['finVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)
            oportunidad_serializer = OportunidadSerializer(data=campos_oportunidad)
            if oportunidad_serializer.is_valid():
                idOportunidad = oportunidad_serializer.save()
                idOportunidad = idOportunidad.id
            contactos = request.data["contactos"]
            for contacto in contactos:
                campos = {'contacto': contacto['id'],
                          'oportunidad': idOportunidad
                        }
                contactoxoportunidad_serializer = OportunidadXContactoSerializer(data = campos)
                if contactoxoportunidad_serializer.is_valid():
                    contactoxoportunidad_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'Oportunidad registrada correctamente',
                        },)	