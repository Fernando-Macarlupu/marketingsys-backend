from django.shortcuts import render
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
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
        subquery4 = Q()
        subquery5 = Q()

        subquery1.add(Q(propietario__id=idPropietario), Q.AND)

        if(cadena != ""):
            subquery1.add(Q(descripcion__contains=cadena), Q.AND)
        if(estado != "" and estado in ['0','1']):
            fecha  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
            if estado == "1":
                subquery1.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                subquery1.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            elif estado == "0":
                subquery4.add(Q(inicioVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                subquery4.add(Q(finVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                subquery5.add(Q(inicioVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                subquery5.add(Q(finVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
        if(fechaVigenciaIni != ""):
            fecha  = datetime.datetime.strptime(fechaVigenciaIni, '%d-%m-%Y').date()
            subquery2.add(Q(inicioVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            subquery3.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
        if(fechaVigenciaFin != ""):
            fecha  = datetime.datetime.strptime(fechaVigenciaFin, '%d-%m-%Y').date()
            subquery2.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
            subquery3.add(Q(finVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
        
        planes = Plan.objects.filter(( (subquery2) | (subquery3)) & subquery1 & ( (subquery4) | (subquery5))).values('id', 'descripcion', 'sponsor', 'presupuesto','estado', 'inicioVigencia', 'finVigencia')
        listaPlanes = list(planes)
        fechaHoy  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
        for plan in listaPlanes:
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
                          'plan': idPlan,
                          'valor': indicador['valor']
                          #podria incluirse el calculoautomatico
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
                          'plan': idPlan,
                          'valor': indicador['valor']
                          #podria incluirse el calculoautomatico
                        }
                indicador_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicador_serializer.is_valid():
                    indicador_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'Plan registrado correctamente',
                        },)	

class BuscarDetallePlan(APIView):
    def get(self, request,id):
        if id != "" and id > 0:
            plan = Plan.objects.filter(id=id).values('id','descripcion', 'sponsor', 'presupuesto', 'inicioVigencia','finVigencia', 'estado','propietario__id').first()
            if plan is not None:
                campos_plan = {
                    "idPlan": plan['id'],
                    "descripcion": plan['descripcion'],
                    "sponsor": plan['sponsor'],
                    "presupuesto": plan['presupuesto'],
                    "estado": plan['estado'],
                    "propietario": plan['propietario__id'],
                    "indicadores": [],
                    "estrategias": [],
                    #leads:,
                    #"contactos": [],
                }
                campos_plan['inicioVigencia'] = datetime.datetime.strftime(plan['inicioVigencia'], '%m/%d/%Y')
                campos_plan['finVigencia'] = datetime.datetime.strftime(plan['finVigencia'], '%m/%d/%Y')
                
                indicadores = IndicadorAsignado.objects.filter(plan__id = plan['id']).values('indicador__id','indicador__nombre','indicador__tipo','indicador__calculoAutomatico','valor') #faltan values
                campos_plan['indicadores'] = list(indicadores)
                for indicador in campos_plan['indicadores']:
                    indicador['id'] = indicador['indicador__id']
                    indicador['nombre'] = indicador['indicador__nombre']
                    indicador['tipo'] = indicador['indicador__tipo']
                    indicador['calculoAutomatico'] = indicador['indicador__calculoAutomatico']
                    del indicador['indicador__id']
                    del indicador['indicador__nombre']
                    del indicador['indicador__tipo']
                    del indicador['indicador__calculoAutomatico']

                programas = Estrategia.objects.filter(plan__id = plan['id']).values('id', 'descripcion','estado', 'tipo','inicioVigencia', 'finVigencia')
                campanas = Campana.objects.filter(plan__id = plan['id']).values('id', 'descripcion','estado', 'tipo','inicioVigencia', 'finVigencia')
                campos_plan['estrategias'] = list(programas) + list(campanas)
                fechaHoy  = datetime.datetime.now()
                for estrategia in campos_plan['estrategias']:
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
                return Response(campos_plan, status = status.HTTP_200_OK)
            else:
                return Response('No se ha encontrado al plan', status = status.HTTP_200_OK)
        return Response('No se ha encontrado al plan', status = status.HTTP_200_OK)

class EliminarPlan(APIView):
    def delete(self, request,id=0):
        if id != "" and id > 0:
            IndicadorAsignado.objects.filter(Q(plan__id = id)).delete()
            Plan.objects.filter(id = id).delete()
            return Response('Plan eliminado',status=status.HTTP_200_OK)
        return Response('Plan no encontrado',status=status.HTTP_200_OK)

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
        subquery4 = Q()
        subquery5 = Q()

        subquery1.add(Q(propietario__id=idPropietario), Q.AND)

        if(cadena != ""):
            subquery1.add(Q(descripcion__contains=cadena), Q.AND)
        if(estado != "" and estado in ['0','1']):
            fecha  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
            if estado == "1":
                subquery1.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                subquery1.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            elif estado == "0":
                subquery4.add(Q(inicioVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                subquery4.add(Q(finVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                subquery5.add(Q(inicioVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                subquery5.add(Q(finVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
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
            programas = Estrategia.objects.filter(( (subquery2) | (subquery3)) & subquery1 & ( (subquery4) | (subquery5))).values('id', 'descripcion', 'sponsor', 'presupuesto','estado', 'tipo','inicioVigencia', 'finVigencia')
            subquery1.add(Q(tipo='1'), Q.AND)
            campanas = Campana.objects.filter(( (subquery2) | (subquery3)) & subquery1 & ( (subquery4) | (subquery5))).values('id', 'descripcion', 'sponsor', 'presupuesto','estado', 'tipo','inicioVigencia', 'finVigencia')
            listaEstrategias = list(programas) + list(campanas)
        elif (tipo == '0'):
            estrategias = Estrategia.objects.filter(( (subquery2) | (subquery3)) & subquery1 & ( (subquery4) | (subquery5))).values('id', 'descripcion', 'sponsor', 'presupuesto','estado', 'tipo','inicioVigencia', 'finVigencia')
            listaEstrategias = list(estrategias)
        elif (tipo == '1'):
            subquery1.add(Q(tipo='1'), Q.AND)
            estrategias = Campana.objects.filter(( (subquery2) | (subquery3)) & subquery1 & ( (subquery4) | (subquery5))).values('id', 'descripcion', 'sponsor', 'presupuesto','estado', 'tipo','inicioVigencia', 'finVigencia')
            listaEstrategias = list(estrategias)
        fechaHoy  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
        for estrategia in listaEstrategias:
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
            #contactos = request.data["contactos"]
            #for contacto in contactos:
            #    campos = {'contacto': contacto['id'],
            #              'estrategia': idEstrategia,
            #              'valor': indicador['valor']
            #            }
                #contactoxestrategia_serializer = ContactoXEstrategiaSerializer(data = campos)
                #if contactoxestrategia_serializer.is_valid():
                #    contactoxestrategia_serializer.save()
            estrategia = Estrategia.objects.filter(id=idEstrategia).first()
            campanas = request.data["campanas"]
            for campana in campanas:
                Campana.objects.filter(id=campana['id']).update(estrategia=estrategia)
            campos_estrategia = {
                 'descripcion': request.data["descripcion"],
                 'tipo': '0',
                 'sponsor': request.data["sponsor"],
                 'presupuesto': request.data["presupuesto"],
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
            estrategia = Estrategia.objects.filter(id=idEstrategia).first()
            campanas = request.data["campanas"]
            for campana in campanas:
                Campana.objects.filter(id=campana['id']).update(estrategia=estrategia)
            #contactos = request.data["contactos"]
            #for contacto in contactos:
            #    campos = {'contacto': contacto['id'],
            #              'estrategia': idEstrategia
            #            }
                #contactoxestrategia_serializer = ContactoXEstrategiaSerializer(data = campos)
                #if contactoxestrategia_serializer.is_valid():
                #    contactoxestrategia_serializer.save()
            indicadores = request.data["indicadores"]
            for indicador in indicadores:
                campos = {'indicador': indicador['id'],
                          'estrategia': idEstrategia,
                          'valor': indicador['valor']
                        }
                indicador_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicador_serializer.is_valid():
                    indicador_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'Estrategia registrada correctamente',
                        },)	

class BuscarDetalleEstrategia(APIView):
    def get(self, request,id):
        if id != "" and id > 0:
            estrategia = Estrategia.objects.filter(id=id).values('id','plan__id','plan__descripcion','descripcion', 'sponsor', 'presupuesto','tipo' ,'inicioVigencia','finVigencia', 'estado','propietario__id','leads__id').first()
            if estrategia is not None:
                campos_estrategia = {
                    "idEstrategia": estrategia['id'],
                    "idPlan": 0,
                    "descripcionPlan": "",
                    "tipo": estrategia['tipo'],
                    "descripcion": estrategia['descripcion'],
                    "sponsor": estrategia['sponsor'],
                    "presupuesto": estrategia['presupuesto'],
                    "estado": estrategia['estado'],
                    "propietario": estrategia['propietario__id'],
                    "leads": 0,
                    "leadsElementos": [],
                    "filtros": [],
                    "indicadores": [],
                    "campanas": [],
                    #"contactos": [],
                }
                if estrategia['plan__id'] is not None:
                    campos_estrategia["idPlan"] = estrategia['plan__id']
                    campos_estrategia["descripcionPlan"] = estrategia['plan__descripcion']
                if estrategia['leads__id'] is not None:
                    campos_estrategia["leads"] = estrategia['leads__id']
                    lista = Lista.objects.filter(id=estrategia['leads__id']).values('id','objeto').first()
                    if(lista['objeto']=="0"):
                        elementos = ListaXContacto.objects.filter(lista__id=estrategia['leads__id']).values('contacto__id','contacto__estado','contacto__persona__nombreCompleto', 'contacto__empresa__nombre')
                        campos_estrategia["leadsElementos"] = list(elementos)
                        for contacto in campos_estrategia["leadsElementos"]:
                            contacto['id'] = contacto['contacto__id']
                            del contacto['contacto__id']

                            if contacto['contacto__estado'] == '0':
                                contacto['estado'] = 'Suscriptor'
                            elif contacto['contacto__estado'] == '1':
                                contacto['estado'] = 'Lead'
                            elif contacto['contacto__estado'] == '2':
                                contacto['estado'] = 'Oportunidad'
                            elif contacto['contacto__estado'] == '3':
                                contacto['estado'] = 'Cliente'
                            del contacto['contacto__estado']

                            contacto['persona__nombreCompleto'] = contacto['contacto__persona__nombreCompleto']
                            del contacto['contacto__persona__nombreCompleto']

                            telefonosContacto = Telefono.objects.filter(contacto__id =contacto['id']).values()
                            if telefonosContacto.count()>0:
                                contacto['telefono'] = telefonosContacto[0]['numero']
                                for telefono in telefonosContacto:
                                    if telefono['principal'] == True: #ver si esta bien el if
                                        contacto['telefono'] = telefono['numero']
                            else:
                                contacto['telefono'] = '-'
                            correoContacto = CuentaCorreo.objects.filter(contacto__id =contacto['id']).values().first()
                            if correoContacto is not None:
                                contacto['correo'] = correoContacto['direccion']
                            else:
                                contacto['correo'] = '-'
                            if contacto['contacto__empresa__nombre'] is None:
                                contacto['empresa'] = "-"
                            else:
                                contacto['empresa'] = contacto['contacto__empresa__nombre']
                            del contacto['contacto__empresa__nombre']

                    elif(lista['objeto']=="1"):
                        elementos = ListaXEmpresa.objects.filter(lista__id=estrategia['leads__id']).values('empresa__id','empresa__nombre','empresa__tipo')
                        campos_estrategia["leadsElementos"] = list(elementos)
                        for empresa in campos_estrategia["leadsElementos"]:
                            empresa['id'] = empresa['empresa__id']
                            del empresa['empresa__id']

                            empresa['nombre'] = empresa['empresa__nombre']
                            del empresa['empresa__nombre']
                            
                            if empresa['empresa__tipo'] == '0':
                                empresa['tipo'] = 'Cliente potencial'
                            elif empresa['empresa__tipo'] == '1':
                                empresa['tipo'] = 'Socio'
                            elif empresa['empresa__tipo'] == '2':
                                empresa['tipo'] = 'Revendedor'
                            elif empresa['empresa__tipo'] == '3':
                                empresa['tipo'] = 'Proveedor'
                            del empresa['empresa__tipo']

                            telefonosEmpresa = Telefono.objects.filter(empresa__id =empresa['id']).values()
                            if telefonosEmpresa.count()>0:
                                empresa['telefono'] = telefonosEmpresa[0]['numero']
                                for telefono in telefonosEmpresa:
                                    if telefono['principal'] == True: #ver si esta bien el if
                                        empresa['telefono'] = telefono['numero']
                            else:
                                empresa['telefono'] = '-'
                    filtros = Filtro.objects.filter(lista__id = estrategia['leads__id']).values('propiedad','evaluacion','valorEvaluacion','nombre') #faltan values
                    campos_estrategia['filtros'] = list(filtros) 
                campos_estrategia['inicioVigencia'] = datetime.datetime.strftime(estrategia['inicioVigencia'], '%m/%d/%Y')
                campos_estrategia['finVigencia'] = datetime.datetime.strftime(estrategia['finVigencia'], '%m/%d/%Y')
                
                indicadores = IndicadorAsignado.objects.filter(estrategia__id = estrategia['id']).values('indicador__id','indicador__nombre','indicador__tipo','indicador__calculoAutomatico','valor') #faltan values
                campos_estrategia['indicadores'] = list(indicadores)
                for indicador in campos_estrategia['indicadores']:
                    indicador['id'] = indicador['indicador__id']
                    indicador['nombre'] = indicador['indicador__nombre']
                    indicador['tipo'] = indicador['indicador__tipo']
                    indicador['calculoAutomatico'] = indicador['indicador__calculoAutomatico']
                    del indicador['indicador__id']
                    del indicador['indicador__nombre']
                    del indicador['indicador__tipo']
                    del indicador['indicador__calculoAutomatico']
                campanas = Campana.objects.filter(estrategia__id = estrategia['id']).values('id', 'descripcion','estado', 'tipo','inicioVigencia', 'finVigencia')
                campos_estrategia['campanas'] = list(campanas)
                fechaHoy  = datetime.datetime.now()
                for campana in campos_estrategia['campanas']:
                    fecha = datetime.datetime(fechaHoy.year,fechaHoy.month,fechaHoy.day, 0,0,0)
                    inicioVigencia = campana['inicioVigencia'].replace(tzinfo=None)
                    finVigencia = campana['finVigencia'].replace(tzinfo=None)
                    if inicioVigencia <= fecha and finVigencia >= fecha:
                        campana['estado'] = 'Vigente'
                    else:
                        campana['estado'] = 'No vigente'
                    if campana['tipo'] == '0':
                        campana['tipo'] = 'De programa'
                    elif campana['tipo'] == '1':
                        campana['tipo'] = 'Campaña stand-alone'

                return Response(campos_estrategia, status = status.HTTP_200_OK)
            else:
                return Response('No se ha encontrado a la estrategia', status = status.HTTP_200_OK)
        return Response('No se ha encontrado a la estrategia', status = status.HTTP_200_OK)

class EliminarEstrategia(APIView):
    def delete(self, request,id=0):
        if id != "" and id > 0:
            IndicadorAsignado.objects.filter(Q(estrategia__id = id)).delete()
            Estrategia.objects.filter(id = id).delete()
            return Response('Estrategia eliminada',status=status.HTTP_200_OK)
        return Response('Estrategia no encontrada',status=status.HTTP_200_OK)

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
        subquery4 = Q()
        subquery5 = Q()

        subquery1.add(Q(propietario__id=idPropietario), Q.AND)

        if(cadena != ""):
            subquery1.add(Q(descripcion__contains=cadena), Q.AND)
        if(estado != "" and estado in ['0','1']):
            fecha  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
            if estado == "1":
                subquery1.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                subquery1.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            elif estado == "0":
                subquery4.add(Q(inicioVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                subquery4.add(Q(finVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                subquery5.add(Q(inicioVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                subquery5.add(Q(finVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)      
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
        
        campanas = Campana.objects.filter(( (subquery2) | (subquery3)) & subquery1 & ( (subquery4) | (subquery5))).values('id', 'descripcion', 'presupuesto','estado', 'tipo','inicioVigencia', 'finVigencia')
        listaCampanas = list(campanas)
        fechaHoy  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
        for campana in listaCampanas:
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
            CampanaXContacto.objects.filter(Q(campana__id = idCampana)).delete()
            indicadores = request.data["indicadores"]
            for indicador in indicadores:
                campos = {'indicador': indicador['id'],
                          'campana': idCampana,
                          'valor': indicador['valor']
                        }
                indicador_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicador_serializer.is_valid():
                    indicador_serializer.save()
            contactos = request.data["contactos"]
            for contacto in contactos:
                campos = {'contacto': contacto['id'],
                          'campana': idCampana
                        }
                contactoxcampana_serializer = CampanaXContactoSerializer(data = campos)
                if contactoxcampana_serializer.is_valid():
                    contactoxcampana_serializer.save()
            campana = Campana.objects.filter(id=idCampana).first()
            recursos = request.data["recursos"]
            for recurso in recursos:
                Recurso.objects.filter(id=recurso['id']).update(campana=campana)
            campos_campana = {
                'tipo': request.data["tipo"],
                 'descripcion': request.data["descripcion"],
                 'sponsor': request.data["sponsor"],
                 'presupuesto': request.data["presupuesto"],
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
            campana = Campana.objects.filter(id=idCampana).first()
            recursos = request.data["recursos"]
            for recurso in recursos:
                Recurso.objects.filter(id=recurso['id']).update(campana=campana)
            contactos = request.data["contactos"]
            for contacto in contactos:
                campos = {'contacto': contacto['id'],
                          'campana': idCampana
                        }
                contactoxcampana_serializer = CampanaXContactoSerializer(data = campos)
                if contactoxcampana_serializer.is_valid():
                    contactoxcampana_serializer.save()
            indicadores = request.data["indicadores"]
            for indicador in indicadores:
                campos = {'indicador': indicador['id'],
                          'campana': idCampana,
                          'valor': indicador['valor']
                        }
                indicador_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicador_serializer.is_valid():
                    indicador_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'Campaña registrada correctamente',
                        },)	

class BuscarDetalleCampana(APIView):
    def get(self, request,id):
        if id != "" and id > 0:
            campana = Campana.objects.filter(id=id).values('id','plan__id','plan__descripcion','estrategia__id','estrategia__descripcion','descripcion', 'sponsor', 'presupuesto','tipo' ,'inicioVigencia','finVigencia', 'estado','propietario__id','leads__id').first()
            if campana is not None:
                campos_campana = {
                    "idCampana": campana['id'],
                    "idPlan": 0,
                    "descripcionPlan": "",
                    "idEstrategia":0,
                    "descripcionEstrategia": "",
                    "tipo": campana['tipo'],
                    "descripcion": campana['descripcion'],
                    "sponsor": campana['sponsor'],
                    "presupuesto": campana['presupuesto'],
                    "estado": campana['estado'],
                    "propietario": campana['propietario__id'],
                    "leads": 0,
                    "recursos": [],
                    "leadsElementos": [],
                    "indicadores": [],
                    "contactos": [],
                    "filtros": []
                }
                if campana['plan__id'] is not None:
                    campos_campana["idPlan"] = campana['plan__id']
                    campos_campana["descripcionPlan"] = campana['plan__descripcion']
                if campana['estrategia__id'] is not None:
                    campos_campana["idEstrategia"] = campana['estrategia__id']
                    campos_campana["descripcionEstrategia"] = campana['estrategia__descripcion']
                contactos = CampanaXContacto.objects.filter(campana__id=campana['id']).values('contacto__id','contacto__estado','contacto__persona__nombreCompleto', 'contacto__empresa__nombre')
                campos_campana['contactos'] = list(contactos)
                ids_contactos = []
                for contacto in campos_campana["contactos"]:
                    contacto['id'] = contacto['contacto__id']
                    ids_contactos.append(contacto['id'])
                    del contacto['contacto__id']

                    if contacto['contacto__estado'] == '0':
                        contacto['estado'] = 'Suscriptor'
                    elif contacto['contacto__estado'] == '1':
                        contacto['estado'] = 'Lead'
                    elif contacto['contacto__estado'] == '2':
                        contacto['estado'] = 'Oportunidad'
                    elif contacto['contacto__estado'] == '3':
                        contacto['estado'] = 'Cliente'
                    del contacto['contacto__estado']

                    contacto['persona__nombreCompleto'] = contacto['contacto__persona__nombreCompleto']
                    del contacto['contacto__persona__nombreCompleto']

                    telefonosContacto = Telefono.objects.filter(contacto__id =contacto['id']).values()
                    if telefonosContacto.count()>0:
                        contacto['telefono'] = telefonosContacto[0]['numero']
                        for telefono in telefonosContacto:
                            if telefono['principal'] == True: #ver si esta bien el if
                                contacto['telefono'] = telefono['numero']
                    else:
                        contacto['telefono'] = '-'
                    correoContacto = CuentaCorreo.objects.filter(contacto__id =contacto['id']).values().first()
                    if correoContacto is not None:
                        contacto['correo'] = correoContacto['direccion']
                    else:
                        contacto['correo'] = '-'
                    if contacto['contacto__empresa__nombre'] is None:
                        contacto['empresa'] = "-"
                    else:
                        contacto['empresa'] = contacto['contacto__empresa__nombre']
                    del contacto['contacto__empresa__nombre']

                if campana['leads__id'] is not None:
                    campos_campana["leads"] = campana['leads__id']
                    lista = Lista.objects.filter(id=campana['leads__id']).values('id','objeto').first()
                    if(lista['objeto']=="0"):
                        elementos = ListaXContacto.objects.filter(lista__id=campana['leads__id']).values('contacto__id','contacto__estado','contacto__persona__nombreCompleto', 'contacto__empresa__nombre')
                        campos_campana["leadsElementos"] = list(elementos)
                        for contacto in campos_campana["leadsElementos"]:
                            if(contacto['contacto__id'] in ids_contactos):
                                index = ids_contactos.index(contacto['contacto__id'])
                                contacto = campos_campana["contactos"][index]
                            else:
                                contacto['id'] = contacto['contacto__id']
                                del contacto['contacto__id']

                                if contacto['contacto__estado'] == '0':
                                    contacto['estado'] = 'Suscriptor'
                                elif contacto['contacto__estado'] == '1':
                                    contacto['estado'] = 'Lead'
                                elif contacto['contacto__estado'] == '2':
                                    contacto['estado'] = 'Oportunidad'
                                elif contacto['contacto__estado'] == '3':
                                    contacto['estado'] = 'Cliente'
                                del contacto['contacto__estado']

                                contacto['persona__nombreCompleto'] = contacto['contacto__persona__nombreCompleto']
                                del contacto['contacto__persona__nombreCompleto']

                                telefonosContacto = Telefono.objects.filter(contacto__id =contacto['id']).values()
                                if telefonosContacto.count()>0:
                                    contacto['telefono'] = telefonosContacto[0]['numero']
                                    for telefono in telefonosContacto:
                                        if telefono['principal'] == True: #ver si esta bien el if
                                            contacto['telefono'] = telefono['numero']
                                else:
                                    contacto['telefono'] = '-'
                                correoContacto = CuentaCorreo.objects.filter(contacto__id =contacto['id']).values().first()
                                if correoContacto is not None:
                                    contacto['correo'] = correoContacto['direccion']
                                else:
                                    contacto['correo'] = '-'
                                if contacto['contacto__empresa__nombre'] is None:
                                    contacto['empresa'] = "-"
                                else:
                                    contacto['empresa'] = contacto['contacto__empresa__nombre']
                                del contacto['contacto__empresa__nombre']
                    elif(lista['objeto']=="1"):
                        elementos = ListaXEmpresa.objects.filter(lista__id=campana['leads__id']).values('empresa__id','empresa__nombre','empresa__tipo')
                        campos_campana["leadsElementos"] = list(elementos)
                        for empresa in campos_campana["leadsElementos"]:
                            empresa['id'] = empresa['empresa__id']
                            del empresa['empresa__id']

                            empresa['nombre'] = empresa['empresa__nombre']
                            del empresa['empresa__nombre']
                            
                            if empresa['empresa__tipo'] == '0':
                                empresa['tipo'] = 'Cliente potencial'
                            elif empresa['empresa__tipo'] == '1':
                                empresa['tipo'] = 'Socio'
                            elif empresa['empresa__tipo'] == '2':
                                empresa['tipo'] = 'Revendedor'
                            elif empresa['empresa__tipo'] == '3':
                                empresa['tipo'] = 'Proveedor'
                            del empresa['empresa__tipo']

                            telefonosEmpresa = Telefono.objects.filter(empresa__id =empresa['id']).values()
                            if telefonosEmpresa.count()>0:
                                empresa['telefono'] = telefonosEmpresa[0]['numero']
                                for telefono in telefonosEmpresa:
                                    if telefono['principal'] == True: #ver si esta bien el if
                                        empresa['telefono'] = telefono['numero']
                            else:
                                empresa['telefono'] = '-'
                    filtros = Filtro.objects.filter(lista__id = campana['leads__id']).values('propiedad','evaluacion','valorEvaluacion','nombre') #faltan values
                    campos_campana['filtros'] = list(filtros)    
                campos_campana['inicioVigencia'] = datetime.datetime.strftime(campana['inicioVigencia'], '%m/%d/%Y')
                campos_campana['finVigencia'] = datetime.datetime.strftime(campana['finVigencia'], '%m/%d/%Y')
                indicadores = IndicadorAsignado.objects.filter(campana__id = campana['id']).values('indicador__id','indicador__nombre','indicador__tipo','indicador__calculoAutomatico','valor') #faltan values
                campos_campana['indicadores'] = list(indicadores)
                for indicador in campos_campana['indicadores']:
                    indicador['id'] = indicador['indicador__id']
                    indicador['nombre'] = indicador['indicador__nombre']
                    indicador['tipo'] = indicador['indicador__tipo']
                    indicador['calculoAutomatico'] = indicador['indicador__calculoAutomatico']
                    del indicador['indicador__id']
                    del indicador['indicador__nombre']
                    del indicador['indicador__tipo']
                    del indicador['indicador__calculoAutomatico']

                recursos = Recurso.objects.filter(campana__id = campana['id']).values('id', 'descripcion','estado', 'tipo','inicioVigencia', 'finVigencia')
                campos_campana['recursos'] = list(recursos)

                fechaHoy  = datetime.datetime.now()
                for recurso in campos_campana['recursos']:
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

                return Response(campos_campana, status = status.HTTP_200_OK)
            else:
                return Response('No se ha encontrado a la campaña', status = status.HTTP_200_OK)
        return Response('No se ha encontrado a la campaña', status = status.HTTP_200_OK)

class EliminarCampana(APIView):
    def delete(self, request,id=0):
        if id != "" and id > 0:
            IndicadorAsignado.objects.filter(Q(campana__id = id)).delete()
            CampanaXContacto.objects.filter(Q(campana__id = id)).delete()
            Campana.objects.filter(id = id).delete()
            return Response('Campana eliminada',status=status.HTTP_200_OK)
        return Response('Campana no encontrada',status=status.HTTP_200_OK)

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
        subquery4 = Q()
        subquery5 = Q()

        subquery1.add(Q(propietario__id=idPropietario), Q.AND)

        if(cadena != ""):
            subquery1.add(Q(descripcion__contains=cadena), Q.AND)
        if(estado != "" and estado in ['0','1']):
            fecha  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
            if estado == "1":
                subquery1.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                subquery1.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
            elif estado == "0":
                subquery4.add(Q(inicioVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                subquery4.add(Q(finVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                subquery5.add(Q(inicioVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                subquery5.add(Q(finVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
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
        
        recursos = Recurso.objects.filter(( (subquery2) | (subquery3)) & subquery1 & ( (subquery4) | (subquery5))).values('id', 'descripcion', 'presupuesto','estado', 'tipo', 'inicioVigencia', 'finVigencia')
        listaRecursos = list(recursos)
        fechaHoy  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
        for recurso in listaRecursos:
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
            RecursoXContacto.objects.filter(Q(recurso__id = idRecurso)).delete()
            Imagen.objects.filter(Q(recurso__id = idRecurso)).delete()
            indicadores = request.data["indicadores"]
            for indicador in indicadores:
                campos = {'indicador': indicador['id'],
                          'recurso': idRecurso,
                          'valor': indicador['valor']
                        }
                indicador_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicador_serializer.is_valid():
                    indicador_serializer.save()
            contactos = request.data["contactos"]
            for contacto in contactos:
                campos = {'contacto': contacto['id'],
                          'recurso': idRecurso
                        }
                contactoxestrategia_serializer = RecursoXContactoSerializer(data = campos)
                if contactoxestrategia_serializer.is_valid():
                    contactoxestrategia_serializer.save()
            recurso = Recurso.objects.filter(id=idRecurso).first()
            campos_recurso = {
                 'descripcion': request.data["descripcion"],
                 'tipo': request.data["tipo"],
                 'presupuesto': request.data["presupuesto"],
                 'estado': request.data["estado"],
                 'propietario': request.data["propietario"],
                 'idUsuario': request.data["idUsuario"],
                 #falta poner los datos dependiendo del tipo
            }
            if(request.data["tipo"]=="0"):
                campos_recurso['contenido'] = request.data["contenido"]
                campos_recurso['contenidoHTML']  = request.data["contenidoHTML"]
                campos_recurso['asuntoCorreo'] = request.data["asuntoCorreo"]
                campos_recurso['remitenteCorreo'] = request.data["remitenteCorreo"]
                campos_recurso['remitenteContrasena'] = request.data["remitenteContrasena"]
                if request.data["fechaPublicacion"] != "" and request.data["horaPublicacion"] != "" and request.data["fechaPublicacion"] is not None and request.data["horaPublicacion"] is not None:
                    fecha  = datetime.datetime.strptime(request.data["fechaPublicacion"], '%d-%m-%Y').date()
                    hora = str(request.data["horaPublicacion"]).split(":")
                    fechaHora = datetime.datetime(fecha.year,fecha.month,fecha.day, int(hora[0]),int(hora[1]),0)
                    campos_recurso['fechaPublicacion'] = fechaHora
            elif (request.data["tipo"]=="1"):
                campos_recurso['servicioRedSocial'] = request.data["servicioRedSocial"]
                campos_recurso['usuarioRedSocial'] = request.data["usuarioRedSocial"]
                campos_recurso['audienciaRedSocial'] = request.data["audienciaRedSocial"]
                campos_recurso['contenido'] = request.data["contenido"]
                if request.data["fechaPublicacion"] != "" and request.data["horaPublicacion"] != "" and request.data["fechaPublicacion"] is not None and request.data["horaPublicacion"] is not None:
                    fecha  = datetime.datetime.strptime(request.data["fechaPublicacion"], '%d-%m-%Y').date()
                    hora = str(request.data["horaPublicacion"]).split(":")
                    fechaHora = datetime.datetime(fecha.year,fecha.month,fecha.day, int(hora[0]),int(hora[1]),0)
                    campos_recurso['fechaPublicacion'] = fechaHora
                for imagen in request.data["imagenes"]:
                    campos_imagen = {
                        'contenido': imagen['contenido'],
                        'enlace': imagen['enlace'],
                        'recurso': idRecurso
                    }
                    imagen_serializer = ImagenSerializer(data = campos_imagen)
                    if imagen_serializer.is_valid():
                        imagen_serializer.save()
            elif (request.data["tipo"]=="2"):
                campos_recurso['titulo'] = request.data["titulo"]
                campos_recurso['dominio'] = request.data["dominio"]
                campos_recurso['complementoDominio'] = request.data["complementoDominio"]
                campos_recurso['contenido'] = request.data["contenido"]
                campos_recurso['contenidoHTML']  = request.data["contenidoHTML"]
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
                 'estado': request.data["estado"],
                 'propietario': request.data["propietario"],
                 'idUsuario': request.data["idUsuario"],
                 #falta poner los datos dependiendo del tipo
            }
            if(request.data["tipo"]=="0"):
                campos_recurso['contenido'] = request.data["contenido"]
                campos_recurso['contenidoHTML']  = request.data["contenidoHTML"]
                campos_recurso['asuntoCorreo'] = request.data["asuntoCorreo"]
                campos_recurso['remitenteCorreo'] = request.data["remitenteCorreo"]
                campos_recurso['remitenteContrasena'] = request.data["remitenteContrasena"]
                if request.data["fechaPublicacion"] != "" and request.data["horaPublicacion"] != "" and request.data["fechaPublicacion"] is not None and request.data["horaPublicacion"] is not None:
                    fecha  = datetime.datetime.strptime(request.data["fechaPublicacion"], '%d-%m-%Y').date()
                    hora = str(request.data["horaPublicacion"]).split(":")
                    fechaHora = datetime.datetime(fecha.year,fecha.month,fecha.day, int(hora[0]),int(hora[1]),0)
                    campos_recurso['fechaPublicacion'] = fechaHora
            elif (request.data["tipo"]=="1"):
                campos_recurso['servicioRedSocial'] = request.data["servicioRedSocial"]
                campos_recurso['usuarioRedSocial'] = request.data["usuarioRedSocial"]
                campos_recurso['audienciaRedSocial'] = request.data["audienciaRedSocial"]
                campos_recurso['contenido'] = request.data["contenido"]
                if request.data["fechaPublicacion"] != "" and request.data["horaPublicacion"] != "" and request.data["fechaPublicacion"] is not None and request.data["horaPublicacion"] is not None:
                    fecha  = datetime.datetime.strptime(request.data["fechaPublicacion"], '%d-%m-%Y').date()
                    hora = str(request.data["horaPublicacion"]).split(":")
                    fechaHora = datetime.datetime(fecha.year,fecha.month,fecha.day, int(hora[0]),int(hora[1]),0)
                    campos_recurso['fechaPublicacion'] = fechaHora
            elif (request.data["tipo"]=="2"):
                campos_recurso['titulo'] = request.data["titulo"]
                campos_recurso['dominio'] = request.data["dominio"]
                campos_recurso['complementoDominio'] = request.data["complementoDominio"]
                campos_recurso['contenido'] = request.data["contenido"]
                campos_recurso['contenidoHTML']  = request.data["contenidoHTML"]
            if(request.data['idCampana']> 0 and request.data['idCampana'] != ""): campos_recurso['campana'] = request.data['idCampana']
            if(request.data["inicioVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["inicioVigencia"], '%d-%m-%Y').date()
                campos_recurso['inicioVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)
            if(request.data["finVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["finVigencia"], '%d-%m-%Y').date()
                campos_recurso['finVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)
            recurso_serializer = RecursoSerializer(data=campos_recurso)
            if recurso_serializer.is_valid():
                idRecurso = recurso_serializer.save()
                idRecurso = idRecurso.id
            if (request.data["tipo"]=="1"):
                for imagen in request.data["imagenes"]:
                    campos_imagen = {
                        'contenido': imagen['contenido'],
                        'enlace': imagen['enlace'],
                        'recurso': idRecurso
                    }
                    imagen_serializer = ImagenSerializer(data = campos_imagen)
                    if imagen_serializer.is_valid():
                        imagen_serializer.save()
            contactos = request.data["contactos"]
            for contacto in contactos:
                campos = {'contacto': contacto['id'],
                          'recurso': idRecurso
                        }
                contactoxestrategia_serializer = RecursoXContactoSerializer(data = campos)
                if contactoxestrategia_serializer.is_valid():
                    contactoxestrategia_serializer.save()
            indicadores = request.data["indicadores"]
            for indicador in indicadores:
                campos = {'indicador': indicador['id'],
                          'recurso': idRecurso,
                          'valor': indicador['valor']
                        }
                indicador_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicador_serializer.is_valid():
                    indicador_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'Recurso registrado correctamente',
                        },)	

class BuscarDetalleRecurso(APIView):
    def get(self, request,id):
        if id != "" and id > 0:
            recurso = Recurso.objects.filter(id=id).values('id','campana__id','campana__descripcion','descripcion', 'presupuesto','tipo' ,
                                                           'inicioVigencia','finVigencia', 'estado','propietario__id','contenido','contenidoHTML',
                                                           'fechaPublicacion','asuntoCorreo', 'remitenteCorreo', 'remitenteContrasena',
                                                           'servicioRedSocial','usuarioRedSocial','audienciaRedSocial','titulo','dominio','complementoDominio','idUsuario').first()
            if recurso is not None:
                campos_recurso = {
                    "idRecurso": recurso['id'],
                    "idCampana": 0,
                    "descripcionCampana": "",
                    "tipo": recurso['tipo'],
                    "presupuesto": recurso['presupuesto'],
                    "estado": recurso['estado'],
                    "descripcion": recurso['descripcion'],
                    "propietario": recurso['propietario__id'],
                    "contenido": recurso['contenido'],
                    "contenidoHTML": recurso['contenidoHTML'],
                    "asuntoCorreo": recurso['asuntoCorreo'],
                    "remitenteCorreo": recurso['remitenteCorreo'],
                    "remitenteContrasena": recurso['remitenteContrasena'],
                    "servicioRedSocial": recurso['servicioRedSocial'],
                    "usuarioRedSocial": recurso['usuarioRedSocial'],
                    "audienciaRedSocial": recurso['audienciaRedSocial'],
                    "titulo": recurso['titulo'],
                    "dominio": recurso['dominio'],
                    "complementoDominio": recurso['complementoDominio'],
                    "indicadores": [],
                    "contactos": [],
                    "imagenesContenido": [],
                    "imagenesEnlaces": [],
                    "fechaPublicacion": "",
                    "horaPublicacion": "",
                    "idUsuario": recurso['idUsuario'],
                }
                if recurso['campana__id'] is not None:
                    campos_recurso["idCampana"] = recurso['campana__id']
                    campos_recurso["descripcionCampana"] = recurso['campana__descripcion']
                if recurso['fechaPublicacion'] is not None:
                    fechapub = recurso['fechaPublicacion'].replace(tzinfo=None)
                    campos_recurso["fechaPublicacion"] = datetime.datetime.strftime(fechapub, '%m/%d/%Y')
                    campos_recurso["horaPublicacion"] = str(fechapub.hour) + ":" + str(fechapub.minute)
                contactos = RecursoXContacto.objects.filter(recurso__id=recurso['id']).values('contacto__id','contacto__estado','contacto__persona__nombreCompleto', 'contacto__empresa__nombre')
                campos_recurso['contactos'] = list(contactos)
                ids_contactos = []
                for contacto in campos_recurso["contactos"]:
                    contacto['id'] = contacto['contacto__id']
                    ids_contactos.append(contacto['id'])
                    del contacto['contacto__id']

                    if contacto['contacto__estado'] == '0':
                        contacto['estado'] = 'Suscriptor'
                    elif contacto['contacto__estado'] == '1':
                        contacto['estado'] = 'Lead'
                    elif contacto['contacto__estado'] == '2':
                        contacto['estado'] = 'Oportunidad'
                    elif contacto['contacto__estado'] == '3':
                        contacto['estado'] = 'Cliente'
                    del contacto['contacto__estado']

                    contacto['nombreCompleto'] = contacto['contacto__persona__nombreCompleto']
                    del contacto['contacto__persona__nombreCompleto']

                    telefonosContacto = Telefono.objects.filter(contacto__id =contacto['id']).values()
                    if telefonosContacto.count()>0:
                        contacto['telefono'] = telefonosContacto[0]['numero']
                        for telefono in telefonosContacto:
                            if telefono['principal'] == True: #ver si esta bien el if
                                contacto['telefono'] = telefono['numero']
                    else:
                        contacto['telefono'] = '-'
                    correoContacto = CuentaCorreo.objects.filter(contacto__id =contacto['id']).values().first()
                    if correoContacto is not None:
                        contacto['correo'] = correoContacto['direccion']
                    else:
                        contacto['correo'] = '-'
                    if contacto['contacto__empresa__nombre'] is None:
                        contacto['empresa'] = "-"
                    else:
                        contacto['empresa'] = contacto['contacto__empresa__nombre']
                    del contacto['contacto__empresa__nombre']

                campos_recurso['inicioVigencia'] = datetime.datetime.strftime(recurso['inicioVigencia'], '%m/%d/%Y')
                campos_recurso['finVigencia'] = datetime.datetime.strftime(recurso['finVigencia'], '%m/%d/%Y')
                indicadores = IndicadorAsignado.objects.filter(recurso__id = recurso['id']).values('indicador__id','indicador__nombre','indicador__tipo','indicador__calculoAutomatico','valor') #faltan values
                campos_recurso['indicadores'] = list(indicadores)
                for indicador in campos_recurso['indicadores']:
                    indicador['id'] = indicador['indicador__id']
                    indicador['nombre'] = indicador['indicador__nombre']
                    indicador['tipo'] = indicador['indicador__tipo']
                    indicador['calculoAutomatico'] = indicador['indicador__calculoAutomatico']
                    del indicador['indicador__id']
                    del indicador['indicador__nombre']
                    del indicador['indicador__tipo']
                    del indicador['indicador__calculoAutomatico']

                imgs = Imagen.objects.filter(recurso__id=recurso['id']).values('contenido','enlace')
                for img in imgs:
                    campos_recurso['imagenesContenido'].append(img['contenido'])
                    campos_recurso['imagenesEnlaces'].append(img['enlace'])
                
                return Response(campos_recurso, status = status.HTTP_200_OK)
            else:
                return Response('No se ha encontrado al recurso', status = status.HTTP_200_OK)
        return Response('No se ha encontrado al recurso', status = status.HTTP_200_OK)

class EliminarRecurso(APIView):
    def delete(self, request,id=0):
        if id != "" and id > 0:
            IndicadorAsignado.objects.filter(Q(recurso__id = id)).delete()
            RecursoXContacto.objects.filter(Q(recurso__id = id)).delete()
            Imagen.objects.filter(Q(recurso__id = id)).delete()
            Recurso.objects.filter(id = id).delete()
            return Response('Recurso eliminado',status=status.HTTP_200_OK)
        return Response('Recurso no encontrado',status=status.HTTP_200_OK)

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
        tipo = request.data["tipo"]
        query = Q()
        if (cadena != ""):
            query.add(Q(nombre__contains=cadena), Q.AND)
        if (tipo != ""):
            query.add(Q(tipo=tipo), Q.AND)
        variables = Variable.objects.filter(query).values('id', 'nombre','abreviatura','tipo','automatica')
        listaVariables = list(variables)
        for variable in listaVariables:
            if variable['tipo'] == "0": variable['tipo'] = "Plan"
            elif variable['tipo'] == "1": variable['tipo'] = "Programa"
            elif variable['tipo'] == "2": variable['tipo'] = "Campaña stand-alone"
            elif variable['tipo'] == "3": variable['tipo'] = "Campaña de programa"
            elif variable['tipo'] == "4": variable['tipo'] = "Correo"
            elif variable['tipo'] == "5": variable['tipo'] = "Publicación"
            elif variable['tipo'] == "6": variable['tipo'] = "Página web"
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
            asociaciones = request.data["asociaciones"]
            for asociacion in asociaciones:
                campos = {
                          'indicador': idIndicador,
                          'valor': asociacion['valor']
                        }
                if request.data["tipo"] == "0": campos['plan'] = asociacion['id']
                elif request.data["tipo"] == "1": campos['estrategia'] = asociacion['id']
                elif request.data["tipo"] == "2" or request.data["tipo"] == "3": campos['campana'] = asociacion['id']
                elif request.data["tipo"] == "4" or request.data["tipo"] == "5" or request.data["tipo"] == "6": campos['recurso'] = asociacion['id']
                indicadorAsignado_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicadorAsignado_serializer.is_valid():
                    indicadorAsignado_serializer.save()
            indicador = Indicador.objects.filter(id=idIndicador).first()
            campos_indicador = {
                'nombre': request.data['nombre'],
                 'descripcion': request.data["descripcion"],
                 'formula': request.data["formula"],
                 'tipo': request.data["tipo"],
                 'automatica': request.data["automatica"],
                 'calculoAutomatico': request.data["calculoAutomatico"],
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
                 'tipo': request.data["tipo"],
                 'automatica': request.data["automatica"],
                 'calculoAutomatico': request.data["calculoAutomatico"],
                 'propietario': request.data["propietario"]
            }
            indicador_serializer = IndicadorSerializer(data=campos_indicador)
            if indicador_serializer.is_valid():
                idIndicador = indicador_serializer.save()
                idIndicador = idIndicador.id
            asociaciones = request.data["asociaciones"]
            for asociacion in asociaciones:
                campos = {
                          'indicador': idIndicador,
                          'valor': asociacion['valor']
                        }
                if request.data["tipo"] == "0": campos['plan'] = asociacion['id']
                elif request.data["tipo"] == "1": campos['estrategia'] = asociacion['id']
                elif request.data["tipo"] == "2" or request.data["tipo"] == "3": campos['campana'] = asociacion['id']
                elif request.data["tipo"] == "4" or request.data["tipo"] == "5" or request.data["tipo"] == "6": campos['recurso'] = asociacion['id']
                indicadorAsignado_serializer = IndicadorAsignadoSerializer(data = campos)
                if indicadorAsignado_serializer.is_valid():
                    indicadorAsignado_serializer.save()
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
        
        indicadores = Indicador.objects.filter((subquery1 | subquery3) & query).values('id', 'nombre','fechaCreacion', 'fechaModificacion','tipo','calculoAutomatico')
        listaIndicadores = list(indicadores)
        for indicador in listaIndicadores:
            indicador['fechaCreacion'] = datetime.datetime.strftime(indicador['fechaCreacion'], '%d-%m-%Y')
            indicador['fechaModificacion'] = datetime.datetime.strftime(indicador['fechaModificacion'], '%d-%m-%Y')
        return Response(listaIndicadores, status = status.HTTP_200_OK)

class BuscarDetalleIndicador(APIView):
    def get(self, request,id):
        if id != "" and id > 0:
            indicador = Indicador.objects.filter(id=id).values('id', 'nombre', 'descripcion', 'formula','tipo','calculoAutomatico','automatica','propietario__id').first()
            if indicador is not None:
                campos_indicador = {
                    "idIndicador": indicador['id'],
                    "nombre": indicador['nombre'],
                    "descripcion": indicador['descripcion'],
                    "formula": indicador['formula'],
                    "tipo": indicador['tipo'],
                    "calculoAutomatico": indicador['calculoAutomatico'],
                    "automatica": indicador['automatica'],
                    "propietario": indicador['propietario__id'],
                    "variables": [],
                    "asociaciones": []
                }
                fechaHoy  = datetime.datetime.now()
                if (indicador['tipo']=="0"):
                    asociaciones = IndicadorAsignado.objects.filter(indicador__id=id).values('plan__id', 'plan__descripcion', 'valor','plan__inicioVigencia','plan__finVigencia')
                    campos_indicador['asociaciones'] = list(asociaciones)
                    for asociacion in campos_indicador['asociaciones']:
                        asociacion['id'] = asociacion['plan__id']
                        asociacion['descripcion'] = asociacion['plan__descripcion']
                        fecha = datetime.datetime(fechaHoy.year,fechaHoy.month,fechaHoy.day, 0,0,0)
                        inicioVigencia = asociacion['plan__inicioVigencia'].replace(tzinfo=None)
                        finVigencia = asociacion['plan__finVigencia'].replace(tzinfo=None)
                        if inicioVigencia <= fecha and finVigencia >= fecha:
                            asociacion['estado'] = 'Vigente'
                        else:
                            asociacion['estado'] = 'No vigente'
                elif (indicador['tipo']=="1"):
                    asociaciones = IndicadorAsignado.objects.filter(indicador__id=id).values('estrategia__id', 'estrategia__descripcion', 'valor','estrategia__inicioVigencia','estrategia__finVigencia')
                    campos_indicador['asociaciones'] = list(asociaciones)
                    for asociacion in campos_indicador['asociaciones']:
                        asociacion['id'] = asociacion['estrategia__id']
                        asociacion['descripcion'] = asociacion['estrategia__descripcion']
                        fecha = datetime.datetime(fechaHoy.year,fechaHoy.month,fechaHoy.day, 0,0,0)
                        inicioVigencia = asociacion['estrategia__inicioVigencia'].replace(tzinfo=None)
                        finVigencia = asociacion['estrategia__finVigencia'].replace(tzinfo=None)
                        if inicioVigencia <= fecha and finVigencia >= fecha:
                            asociacion['estado'] = 'Vigente'
                        else:
                            asociacion['estado'] = 'No vigente'
                elif (indicador['tipo']=="2" or indicador['tipo']=="3"):
                    asociaciones = IndicadorAsignado.objects.filter(indicador__id=id).values('campana__id', 'campana__descripcion', 'valor','campana__inicioVigencia','campana__finVigencia')
                    campos_indicador['asociaciones'] = list(asociaciones)
                    for asociacion in campos_indicador['asociaciones']:
                        asociacion['id'] = asociacion['campana__id']
                        asociacion['descripcion'] = asociacion['campana__descripcion']
                        fecha = datetime.datetime(fechaHoy.year,fechaHoy.month,fechaHoy.day, 0,0,0)
                        inicioVigencia = asociacion['campana__inicioVigencia'].replace(tzinfo=None)
                        finVigencia = asociacion['campana__finVigencia'].replace(tzinfo=None)
                        if inicioVigencia <= fecha and finVigencia >= fecha:
                            asociacion['estado'] = 'Vigente'
                        else:
                            asociacion['estado'] = 'No vigente'
                elif (indicador['tipo']=="4" or indicador['tipo']=="5" or indicador['tipo']=="6"):
                    asociaciones = IndicadorAsignado.objects.filter(indicador__id=id).values('recurso__id', 'recurso__descripcion', 'valor','recurso__inicioVigencia','recurso__finVigencia')
                    campos_indicador['asociaciones'] = list(asociaciones)
                    for asociacion in campos_indicador['asociaciones']:
                        asociacion['id'] = asociacion['recurso__id']
                        asociacion['descripcion'] = asociacion['recurso__descripcion']
                        fecha = datetime.datetime(fechaHoy.year,fechaHoy.month,fechaHoy.day, 0,0,0)
                        inicioVigencia = asociacion['recurso__inicioVigencia'].replace(tzinfo=None)
                        finVigencia = asociacion['recurso__finVigencia'].replace(tzinfo=None)
                        if inicioVigencia <= fecha and finVigencia >= fecha:
                            asociacion['estado'] = 'Vigente'
                        else:
                            asociacion['estado'] = 'No vigente'
                variables = VariableXIndicador.objects.filter(indicador__id=id).values('variable__id', 'variable__nombre', 'variable__abreviatura','variable__tipo','variable__automatica')
                campos_indicador['variables'] = list(variables)
                for variable in campos_indicador['variables']:
                    variable['id'] = variable['variable__id']
                    variable['nombre'] = variable['variable__nombre']
                    variable['abreviatura'] = variable['variable__abreviatura']
                    if variable['variable__tipo'] == "0": variable['tipo']="Plan"
                    elif variable['variable__tipo'] == "1": variable['tipo']="Programa"
                    elif variable['variable__tipo'] == "2": variable['tipo']="Campaña stand-alone"
                    elif variable['variable__tipo'] == "3": variable['tipo']="Campaña de programa"
                    elif variable['variable__tipo'] == "4": variable['tipo']="Correo"
                    elif variable['variable__tipo'] == "5": variable['tipo']="Publicación"
                    elif variable['variable__tipo'] == "6": variable['tipo']="Página web"
                    variable['automatica'] = variable['variable__automatica']
                return Response(campos_indicador, status = status.HTTP_200_OK)
            else:
                return Response('No se ha encontrado el indicador', status = status.HTTP_200_OK)
        return Response('No se ha encontrado el indicador', status = status.HTTP_200_OK)

class EliminarIndicador(APIView):
    def delete(self, request,id=0):
        if id != "" and id > 0:
            IndicadorAsignado.objects.filter(Q(indicador__id = id)).delete()
            VariableXIndicador.objects.filter(Q(indicador__id = id)).delete()
            Indicador.objects.filter(id = id).delete()
            return Response('Indicador eliminado',status=status.HTTP_200_OK)
        return Response('Indicador no encontrado',status=status.HTTP_200_OK)

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
        fechaHoy  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
        for oportunidad in listaOportunidades:
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
                 'estado': request.data["estado"],
                 'propietario': request.data["propietario"],
            }
            if(request.data["idCampana"] != "" and request.data["idCampana"]>0):
                campos_oportunidad['campana'] = request.data["idCampana"]
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
                 'estado': request.data["estado"],
                 'propietario': request.data["propietario"]
            }
            print(campos_oportunidad)
            if(request.data["idCampana"] != "" and request.data["idCampana"] >0):
                campos_oportunidad['campana'] = request.data["idCampana"]
            if(request.data["inicioVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["inicioVigencia"], '%d-%m-%Y').date()
                campos_oportunidad['inicioVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)
            if(request.data["finVigencia"] != ""):
                fecha  = datetime.datetime.strptime(request.data["finVigencia"], '%d-%m-%Y').date()
                campos_oportunidad['finVigencia'] = datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)
            oportunidad_serializer = OportunidadSerializer(data=campos_oportunidad)
            print(campos_oportunidad)
            if oportunidad_serializer.is_valid():
                print("fue valido")
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

class BuscarDetalleOportunidad(APIView):
    def get(self, request,id):
        if id != "" and id > 0:
            oportunidad = Oportunidad.objects.filter(id=id).values('id','campana__id','campana__descripcion','descripcion', 'importe','tipo' ,'etapa' ,'inicioVigencia','finVigencia', 'estado','propietario__id').first()
            if oportunidad is not None:
                campos_oportunidad = {
                    "idOportunidad": oportunidad['id'],
                    "idCampana": 0,
                    "descripcionCampana": "",
                    "descripcion": oportunidad['descripcion'],
                    "tipo": oportunidad['tipo'],
                    "etapa": oportunidad['etapa'],
                    "importe": oportunidad['importe'],
                    "estado": oportunidad['estado'],
                    "propietario": oportunidad['propietario__id'],
                    "contactos": [],
                }
                if oportunidad['campana__id'] is not None:
                    campos_oportunidad["idCampana"] = oportunidad['campana__id']
                    campos_oportunidad["descripcionCampana"] = oportunidad['campana__descripcion']
                contactos = OportunidadXContacto.objects.filter(oportunidad__id=oportunidad['id']).values('contacto__id','contacto__estado','contacto__persona__nombreCompleto', 'contacto__empresa__nombre')
                campos_oportunidad['contactos'] = list(contactos)
                ids_contactos = []
                for contacto in campos_oportunidad["contactos"]:
                    contacto['id'] = contacto['contacto__id']
                    ids_contactos.append(contacto['id'])
                    del contacto['contacto__id']

                    if contacto['contacto__estado'] == '0':
                        contacto['estado'] = 'Suscriptor'
                    elif contacto['contacto__estado'] == '1':
                        contacto['estado'] = 'Lead'
                    elif contacto['contacto__estado'] == '2':
                        contacto['estado'] = 'Oportunidad'
                    elif contacto['contacto__estado'] == '3':
                        contacto['estado'] = 'Cliente'
                    del contacto['contacto__estado']

                    contacto['persona__nombreCompleto'] = contacto['contacto__persona__nombreCompleto']
                    del contacto['contacto__persona__nombreCompleto']

                    telefonosContacto = Telefono.objects.filter(contacto__id =contacto['id']).values()
                    if telefonosContacto.count()>0:
                        contacto['telefono'] = telefonosContacto[0]['numero']
                        for telefono in telefonosContacto:
                            if telefono['principal'] == True: #ver si esta bien el if
                                contacto['telefono'] = telefono['numero']
                    else:
                        contacto['telefono'] = '-'
                    correoContacto = CuentaCorreo.objects.filter(contacto__id =contacto['id']).values().first()
                    if correoContacto is not None:
                        contacto['correo'] = correoContacto['direccion']
                    else:
                        contacto['correo'] = '-'
                    if contacto['contacto__empresa__nombre'] is None:
                        contacto['empresa'] = "-"
                    else:
                        contacto['empresa'] = contacto['contacto__empresa__nombre']
                    del contacto['contacto__empresa__nombre']

                campos_oportunidad['inicioVigencia'] = datetime.datetime.strftime(oportunidad['inicioVigencia'], '%m/%d/%Y')
                campos_oportunidad['finVigencia'] = datetime.datetime.strftime(oportunidad['finVigencia'], '%m/%d/%Y')

                return Response(campos_oportunidad, status = status.HTTP_200_OK)
            else:
                return Response('No se ha encontrado la oportunidad', status = status.HTTP_200_OK)
        return Response('No se ha encontrado la oportunidad', status = status.HTTP_200_OK)

class EliminarOportunidad(APIView):
    def delete(self, request,id=0):
        if id != "" and id > 0:
            OportunidadXContacto.objects.filter(Q(oportunidad__id = id)).delete()
            Oportunidad.objects.filter(id = id).delete()
            return Response('Oportunidad eliminada',status=status.HTTP_200_OK)
        return Response('Oportunidad no encontrada',status=status.HTTP_200_OK)

class FiltrarReportes(APIView):
    def post(self, request,id=0):
        cadena = request.data["cadena"]
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
        
        reportes = Reporte.objects.filter((subquery1 | subquery3) & query).values('id', 'nombre','fechaCreacion', 'fechaModificacion','tipo')
        listaReportes = list(reportes)
        for reporte in listaReportes:
            reporte['fechaCreacion'] = datetime.datetime.strftime(reporte['fechaCreacion'], '%d-%m-%Y')
            reporte['fechaModificacion'] = datetime.datetime.strftime(reporte['fechaModificacion'], '%d-%m-%Y')
        return Response(listaReportes, status = status.HTTP_200_OK)

class EliminarReporte(APIView):
    def delete(self, request,id=0):
        if id != "" and id > 0:
            Filtro.objects.filter(Q(reporte__id = id)).delete()
            Columna.objects.filter(Q(reporte__id = id)).delete()
            Fila.objects.filter(Q(reporte__id = id)).delete()
            Reporte.objects.filter(id=id).delete()
            return Response('Reporte eliminado',status=status.HTTP_200_OK)
        return Response('Reporte no encontrado',status=status.HTTP_200_OK)

class AplicarFiltrosReporte(APIView):
    def post(self, request,id=0):
        elementos = []
        idPropietario = int(request.data["propietario"])
        fechaHoy = request.data["fechaHoy"]
        columnas = []
        filas = []
        if request.data["filtros"] != []:
            if request.data["tipo"] in ['0','1','2','3']:
                query = Q()
                subquery1 = Q()
                subquery2 = Q()
                query.add(Q(propietario__id=idPropietario), Q.AND)
                for filtro in request.data["filtros"]:
                    if(filtro['propiedad']=="descripcion"):
                        query.add(Q(descripcion__contains=filtro['valorEvaluacion']), Q.AND)
                    elif(filtro['propiedad']=="sponsor"):
                        query.add(Q(sponsor__contains=filtro['valorEvaluacion']), Q.AND)
                    elif(filtro['propiedad'] == "presupuesto"):
                        presupuesto = int(filtro['valorEvaluacion'])
                        if(filtro['evaluacion'] == "0"):
                            query.add(Q(presupuesto=presupuesto), Q.AND)
                        elif(filtro['evaluacion'] == "1"):
                            query.add(Q(presupuesto__lt=presupuesto), Q.AND)
                        elif(filtro['evaluacion'] == "2"):
                            query.add(Q(presupuesto__gt=presupuesto), Q.AND)
                        elif(filtro['evaluacion'] == "3"):
                            query.add(Q(presupuesto__lte=presupuesto), Q.AND)
                        elif(filtro['evaluacion'] == "4"):
                            query.add(Q(presupuesto__gte=presupuesto), Q.AND)
                    elif(filtro['propiedad'] == "inicioVigencia"):
                        fecha  = datetime.datetime.strptime(filtro['valorEvaluacion'], '%d-%m-%Y').date()
                        if(filtro['evaluacion'] == "0"):
                            query.add(Q(inicioVigencia=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "1"):
                            query.add(Q(inicioVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "2"):
                            query.add(Q(inicioVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "3"):
                            query.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "4"):
                            query.add(Q(inicioVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                    elif(filtro['propiedad'] == "finVigencia"):
                        fecha  = datetime.datetime.strptime(filtro['valorEvaluacion'], '%d-%m-%Y').date()
                        if(filtro['evaluacion'] == "0"):
                            query.add(Q(finVigencia=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "1"):
                            query.add(Q(finVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "2"):
                            query.add(Q(finVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "3"):
                            query.add(Q(finVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "4"):
                            query.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                    elif(filtro['propiedad'] == "fechaCreacion"):
                        fecha  = datetime.datetime.strptime(filtro['valorEvaluacion'], '%d-%m-%Y').date()
                        if(filtro['evaluacion'] == "0"):
                            query.add(Q(fechaCreacion=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "1"):
                            query.add(Q(fechaCreacion__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "2"):
                            query.add(Q(fechaCreacion__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "3"):
                            query.add(Q(fechaCreacion__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "4"):
                            query.add(Q(fechaCreacion__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                    elif(filtro['propiedad'] == "fechaPublicacion"):
                        fecha  = datetime.datetime.strptime(filtro['valorEvaluacion'], '%d-%m-%Y').date()
                        if(filtro['evaluacion'] == "0"):
                            query.add(Q(fechaPublicacion=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "1"):
                            query.add(Q(fechaPublicacion__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "2"):
                            query.add(Q(fechaPublicacion__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "3"):
                            query.add(Q(fechaPublicacion__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "4"):
                            query.add(Q(fechaPublicacion__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                    elif(filtro['propiedad'] == "estado"):
                        fecha  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
                        if(filtro['valorEvaluacion'] == "0"):
                            subquery1.add(Q(inicioVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                            subquery1.add(Q(finVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                            subquery2.add(Q(inicioVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                            subquery2.add(Q(finVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['valorEvaluacion'] == "1"):
                            query.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                            query.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                    elif(filtro['propiedad'] == "tipo"):
                        query.add(Q(tipo=filtro['valorEvaluacion']), Q.AND)
                if request.data["tipo"] == "0":
                    elementosBD = Plan.objects.filter(query & (subquery1 | subquery2)).values('id', 'descripcion', 'sponsor', 'presupuesto','inicioVigencia','finVigencia','estado','fechaCreacion', 'fechaModificacion')
                elif request.data["tipo"] == "1":
                    query.add(Q(tipo="0"), Q.AND)
                    elementosBD = Estrategia.objects.filter(query & (subquery1 | subquery2)).values('id', 'descripcion', 'sponsor', 'presupuesto','inicioVigencia','finVigencia','estado','fechaCreacion', 'fechaModificacion','tipo')
                elif request.data["tipo"] == "2":
                    elementosBD = Campana.objects.filter(query & (subquery1 | subquery2)).values('id', 'descripcion', 'sponsor', 'presupuesto','inicioVigencia','finVigencia','estado','fechaCreacion', 'fechaModificacion','tipo')
                elif request.data["tipo"] == "3":
                    elementosBD = Recurso.objects.filter(query & (subquery1 | subquery2)).values('id', 'descripcion', 'sponsor', 'presupuesto','inicioVigencia','finVigencia','estado','fechaCreacion', 'fechaModificacion','tipo')
                elementos = list(elementosBD)
                fechaActual  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
                if request.data["tipo"] == "0":
                    columnas = ['plan-descripcion', 'plan-sponsor', 'plan-presupuesto','plan-inicioVigencia','plan-finVigencia','plan-estado','plan-fechaCreacion', 'plan-fechaModificacion']
                    for elemento in elementos:
                        fecha = datetime.datetime(fechaActual.year,fechaActual.month,fechaActual.day, 0,0,0)
                        inicioVigencia = elemento['inicioVigencia'].replace(tzinfo=None)
                        finVigencia = elemento['finVigencia'].replace(tzinfo=None)
                        estado = ""
                        if inicioVigencia <= fecha and finVigencia >= fecha:
                            estado = 'Vigente'
                        else:
                            estado = 'No vigente'
                        if request.data["tipo"] == "1":
                            if elemento['tipo'] == "0": elemento['tipo'] = "Programa"
                            elif elemento['tipo'] == "1": elemento['tipo'] = "Campaña stand-alone"
                        if request.data["tipo"] == "2":
                            if elemento['tipo'] == "0": elemento['tipo'] = "Campaña de programa"
                            elif elemento['tipo'] == "1": elemento['tipo'] = "Campaña stand-alone"
                        if request.data["tipo"] == "3":
                            if elemento['tipo'] == "0": elemento['tipo'] = "Correo"
                            elif elemento['tipo'] == "1": elemento['tipo'] = "Publicación"
                            elif elemento['tipo'] == "2": elemento['tipo'] = "Página web"
                        fila = [['plan-descripcion', elemento['descripcion']], 
                                ['plan-sponsor',elemento['sponsor']], 
                                ['plan-presupuesto',str(elemento['presupuesto'])],
                                ['plan-inicioVigencia', datetime.datetime.strftime(elemento['inicioVigencia'], '%d-%m-%Y')],
                                ['plan-finVigencia', datetime.datetime.strftime(elemento['finVigencia'], '%d-%m-%Y')],
                                ['plan-estado',estado],
                                ['plan-fechaCreacion', datetime.datetime.strftime(elemento['fechaCreacion'], '%d-%m-%Y')], 
                                ['plan-fechaModificacion', datetime.datetime.strftime(elemento['fechaModificacion'], '%d-%m-%Y')]]
                        filas.append(fila)
                elif request.data["tipo"] == "1":
                    columnas = ['programa-descripcion','programa-tipo' ,'programa-sponsor', 'programa-presupuesto','programa-inicioVigencia','programa-finVigencia','programa-estado','programa-fechaCreacion', 'programa-fechaModificacion']
                    for elemento in elementos:
                        fecha = datetime.datetime(fechaActual.year,fechaActual.month,fechaActual.day, 0,0,0)
                        inicioVigencia = elemento['inicioVigencia'].replace(tzinfo=None)
                        finVigencia = elemento['finVigencia'].replace(tzinfo=None)
                        estado = ""
                        tipo = ""
                        if inicioVigencia <= fecha and finVigencia >= fecha:
                            estado = 'Vigente'
                        else:
                            estado = 'No vigente'
                        if elemento['tipo'] == "0": tipo = "Programa"
                        elif elemento['tipo'] == "1": tipo = "Campaña stand-alone"
                        fila = [['programa-descripcion', elemento['descripcion']], 
                                ['programa-tipo', tipo],
                                ['programa-sponsor',elemento['sponsor']], 
                                ['programa-presupuesto',str(elemento['presupuesto'])],
                                ['programa-inicioVigencia', datetime.datetime.strftime(elemento['inicioVigencia'], '%d-%m-%Y')],
                                ['programa-finVigencia', datetime.datetime.strftime(elemento['finVigencia'], '%d-%m-%Y')],
                                ['programa-estado',estado],
                                ['programa-fechaCreacion', datetime.datetime.strftime(elemento['fechaCreacion'], '%d-%m-%Y')], 
                                ['programa-fechaModificacion', datetime.datetime.strftime(elemento['fechaModificacion'], '%d-%m-%Y')]]
                        filas.append(fila)
                elif request.data["tipo"] == "2":
                    columnas = ['campana-descripcion','campana-tipo' ,'campana-sponsor', 'campana-presupuesto','campana-inicioVigencia','campana-finVigencia','campana-estado','campana-fechaCreacion', 'campana-fechaModificacion']
                    for elemento in elementos:
                        fecha = datetime.datetime(fechaActual.year,fechaActual.month,fechaActual.day, 0,0,0)
                        inicioVigencia = elemento['inicioVigencia'].replace(tzinfo=None)
                        finVigencia = elemento['finVigencia'].replace(tzinfo=None)
                        estado = ""
                        tipo = ""
                        if inicioVigencia <= fecha and finVigencia >= fecha:
                            estado = 'Vigente'
                        else:
                            estado = 'No vigente'
                        if elemento['tipo'] == "0": tipo = "Campaña de programa"
                        elif elemento['tipo'] == "1": tipo = "Campaña stand-alone"
                        fila = [['campana-descripcion', elemento['descripcion']], 
                                ['campana-tipo', tipo],
                                ['campana-sponsor',elemento['sponsor']], 
                                ['campana-presupuesto',str(elemento['presupuesto'])],
                                ['campana-inicioVigencia', datetime.datetime.strftime(elemento['inicioVigencia'], '%d-%m-%Y')],
                                ['campana-finVigencia', datetime.datetime.strftime(elemento['finVigencia'], '%d-%m-%Y')],
                                ['campana-estado',estado],
                                ['campana-fechaCreacion', datetime.datetime.strftime(elemento['fechaCreacion'], '%d-%m-%Y')], 
                                ['campana-fechaModificacion', datetime.datetime.strftime(elemento['fechaModificacion'], '%d-%m-%Y')]]
                        filas.append(fila)
                elif request.data["tipo"] == "3":
                    columnas = ['recurso-descripcion','recurso-tipo' ,'recurso-presupuesto','recurso-inicioVigencia','recurso-finVigencia','recurso-estado','recurso-fechaCreacion', 'recurso-fechaModificacion']
                    for elemento in elementos:
                        fecha = datetime.datetime(fechaActual.year,fechaActual.month,fechaActual.day, 0,0,0)
                        inicioVigencia = elemento['inicioVigencia'].replace(tzinfo=None)
                        finVigencia = elemento['finVigencia'].replace(tzinfo=None)
                        estado = ""
                        tipo = ""
                        if inicioVigencia <= fecha and finVigencia >= fecha:
                            estado = 'Vigente'
                        else:
                            estado = 'No vigente'
                        if elemento['tipo'] == "0": tipo = "Correo"
                        elif elemento['tipo'] == "1": tipo = "Publicación"
                        elif elemento['tipo'] == "2": tipo = "Página web"
                        fila = [['recurso-descripcion', elemento['descripcion']], 
                                ['recurso-tipo', tipo],
                                ['recurso-sponsor',elemento['sponsor']], 
                                ['recurso-presupuesto',str(elemento['presupuesto'])],
                                ['recurso-inicioVigencia', datetime.datetime.strftime(elemento['inicioVigencia'], '%d-%m-%Y')],
                                ['recurso-finVigencia', datetime.datetime.strftime(elemento['finVigencia'], '%d-%m-%Y')],
                                ['recurso-estado',estado],
                                ['recurso-fechaCreacion', datetime.datetime.strftime(elemento['fechaCreacion'], '%d-%m-%Y')], 
                                ['recurso-fechaModificacion', datetime.datetime.strftime(elemento['fechaModificacion'], '%d-%m-%Y')]]
                        filas.append(fila)                         
            if request.data["tipo"] =="4":
                query = Q()
                subquery1 = Q()
                subquery2 = Q()
                query.add(Q(propietario__id=idPropietario), Q.AND)
                for filtro in request.data["filtros"]:
                    if(filtro['propiedad']=="descripcion"):
                        query.add(Q(descripcion__contains=filtro['valorEvaluacion']), Q.AND)
                    elif(filtro['propiedad'] == "importe"):
                        importe = int(filtro['valorEvaluacion'])
                        if(filtro['evaluacion'] == "0"):
                            query.add(Q(importe=importe), Q.AND)
                        elif(filtro['evaluacion'] == "1"):
                            query.add(Q(importe__lt=importe), Q.AND)
                        elif(filtro['evaluacion'] == "2"):
                            query.add(Q(importe__gt=importe), Q.AND)
                        elif(filtro['evaluacion'] == "3"):
                            query.add(Q(importe__lte=importe), Q.AND)
                        elif(filtro['evaluacion'] == "4"):
                            query.add(Q(importe__gte=importe), Q.AND)
                    elif(filtro['propiedad'] == "inicioVigencia"):
                        fecha  = datetime.datetime.strptime(filtro['valorEvaluacion'], '%d-%m-%Y').date()
                        if(filtro['evaluacion'] == "0"):
                            query.add(Q(inicioVigencia=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "1"):
                            query.add(Q(inicioVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "2"):
                            query.add(Q(inicioVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "3"):
                            query.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "4"):
                            query.add(Q(inicioVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                    elif(filtro['propiedad'] == "finVigencia"):
                        fecha  = datetime.datetime.strptime(filtro['valorEvaluacion'], '%d-%m-%Y').date()
                        if(filtro['evaluacion'] == "0"):
                            query.add(Q(finVigencia=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "1"):
                            query.add(Q(finVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "2"):
                            query.add(Q(finVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "3"):
                            query.add(Q(finVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "4"):
                            query.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                    elif(filtro['propiedad'] == "fechaCreacion"):
                        fecha  = datetime.datetime.strptime(filtro['valorEvaluacion'], '%d-%m-%Y').date()
                        if(filtro['evaluacion'] == "0"):
                            query.add(Q(fechaCreacion=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "1"):
                            query.add(Q(fechaCreacion__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "2"):
                            query.add(Q(fechaCreacion__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "3"):
                            query.add(Q(fechaCreacion__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "4"):
                            query.add(Q(fechaCreacion__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                    elif(filtro['propiedad'] == "estado"):
                        fecha  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
                        if(filtro['valorEvaluacion'] == "0"):
                            subquery1.add(Q(inicioVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                            subquery1.add(Q(finVigencia__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                            subquery2.add(Q(inicioVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                            subquery2.add(Q(finVigencia__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['valorEvaluacion'] == "1"):
                            query.add(Q(inicioVigencia__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                            query.add(Q(finVigencia__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                    elif(filtro['propiedad'] == "tipo"):
                        query.add(Q(tipo=filtro['valorEvaluacion']), Q.AND)
                    elif(filtro['propiedad'] == "etapa"):
                        query.add(Q(tipo=filtro['valorEvaluacion']), Q.AND)
                elementosBD = Oportunidad.objects.filter(query & (subquery1 | subquery2)).values('id', 'descripcion', 'importe','tipo','etapa','inicioVigencia','finVigencia','estado','fechaCreacion', 'fechaModificacion')
                elementos = list(elementosBD)
                fechaActual  = datetime.datetime.strptime(fechaHoy, '%d-%m-%Y').date()
                columnas = ['oportunidad-descripcion','oportunidad-tipo' , 'oportunidad-etapa', 'oportunidad-importe','oportunidad-inicioVigencia','oportunidad-finVigencia','oportunidad-estado','oportunidad-fechaCreacion', 'oportunidad-fechaModificacion']
                for elemento in elementos:
                    fecha = datetime.datetime(fechaActual.year,fechaActual.month,fechaActual.day, 0,0,0)
                    inicioVigencia = elemento['inicioVigencia'].replace(tzinfo=None)
                    finVigencia = elemento['finVigencia'].replace(tzinfo=None)
                    estado = ""
                    tipo = ""
                    etapa = ""
                    if inicioVigencia <= fecha and finVigencia >= fecha:
                        estado = 'Vigente'
                    else:
                        estado = 'No vigente'
                    if elemento['tipo'] == "0": tipo = "Negocio existente"
                    elif elemento['tipo'] == "1": tipo = "Nuevo negocio"
                    if elemento['etapa']=='0':
                        etapa = "Calificación"
                    elif elemento['etapa'] == '1':
                        etapa = "Necesidad de análisis"
                    elif elemento['etapa'] == '2':
                        etapa = "Propuesta"
                    elif elemento['etapa'] == '3':
                        etapa = "Negociación"
                    elif elemento['etapa'] == '4':
                        etapa = "Perdida"
                    elif elemento['etapa'] == '5':
                        etapa = "Ganada"
                    fila = [['oportunidad-descripcion', elemento['descripcion']], 
                            ['oportunidad-tipo', tipo],
                            ['oportunidad-etapa',etapa], 
                            ['oportunidad-importe',str(elemento['importe'])],
                            ['oportunidad-inicioVigencia', datetime.datetime.strftime(elemento['inicioVigencia'], '%d-%m-%Y')],
                            ['oportunidad-finVigencia', datetime.datetime.strftime(elemento['finVigencia'], '%d-%m-%Y')],
                            ['oportunidad-estado',estado],
                            ['oportunidad-fechaCreacion', datetime.datetime.strftime(elemento['fechaCreacion'], '%d-%m-%Y')], 
                            ['oportunidad-fechaModificacion', datetime.datetime.strftime(elemento['fechaModificacion'], '%d-%m-%Y')]]
                    filas.append(fila)
            if request.data["tipo"] == "5":
                query = Q()
                subquery1 = Q()
                subquery2 = Q()
                query.add(Q(propietario__id=idPropietario), Q.AND)
                for filtro in request.data["filtros"]:
                    if(filtro['propiedad']=="nombreCompleto"):
                        query.add(Q(persona_nombreCompleto__contains=filtro['valorEvaluacion']), Q.AND)
                    elif (filtro['propiedad']=="correo"):
                        correos = CuentaCorreo.objects.filter(direccion__contains = filtro['valorEvaluacion']).values('contacto__id')
                        contactosCorreo = [correo['contacto__id'] for correo in list(correos)]
                        query.add(Q(id__in=contactosCorreo), Q.AND)
                    elif(filtro['propiedad'] == "telefono"):
                        telefonos = Telefono.objects.filter(numero__contains = filtro['valorEvaluacion']).values('contacto__id')
                        contactosTelefono = [telefono['contacto__id'] for telefono in list(telefonos)]
                        query.add(Q(id__in=contactosTelefono), Q.AND)
                    elif(filtro['propiedad'] == "paisDir"):
                        direcciones = Direccion.objects.filter(pais__contains = filtro['valorEvaluacion']).values('contacto__id')
                        contactosDireccion = [direccion['contacto__id'] for direccion in list(direcciones)]
                        query.add(Q(id__in=contactosDireccion), Q.AND)
                    elif(filtro['propiedad'] == "estadoDir"):
                        direcciones = Direccion.objects.filter(estado__contains = filtro['valorEvaluacion']).values('contacto__id')
                        contactosDireccion = [direccion['contacto__id'] for direccion in list(direcciones)]
                        query.add(Q(id__in=contactosDireccion), Q.AND)
                    elif(filtro['propiedad'] == "ciudadDir"):
                        direcciones = Direccion.objects.filter(ciudad__contains = filtro['valorEvaluacion']).values('contacto__id')
                        contactosDireccion = [direccion['contacto__id'] for direccion in list(direcciones)]
                        query.add(Q(id__in=contactosDireccion), Q.AND)
                    elif(filtro['propiedad'] == "direccionDir"):
                        direcciones = Direccion.objects.filter(direccion__contains = filtro['valorEvaluacion']).values('contacto__id')
                        contactosDireccion = [direccion['contacto__id'] for direccion in list(direcciones)]
                        query.add(Q(id__in=contactosDireccion), Q.AND)
                    elif(filtro['propiedad'] == "estado"):
                        query.add(Q(estado=filtro['valorEvaluacion']), Q.AND)
                    elif(filtro['propiedad'] == "calificado"):
                        if(filtro['valorEvaluacion'] == "0"):
                            query.add(Q(calificado=False), Q.AND)
                        elif(filtro['valorEvaluacion'] == "1"):
                            query.add(Q(calificado=True), Q.AND)
                    elif(filtro['propiedad'] == "red"):
                        redes = CuentaRedSocial.objects.filter(redSocial = filtro['valorEvaluacion']).values('contacto__id')
                        contactosRed = [red['contacto__id'] for red in list(redes)]
                        query.add(Q(id__in=contactosRed), Q.AND)
                    elif(filtro['propiedad'] == "empresa"):
                        if(filtro['valorEvaluacion'] == "0"):
                            query.add(Q(empresa__id__isnull=True), Q.AND) #revisar si funciona
                        elif(filtro['valorEvaluacion'] == "1"):
                            query.add(Q(empresa__id__gte = 1), Q.AND)
                    elif(filtro['propiedad'] == "empresaNombre"):
                        query.add(Q(empresa__nombre__contains = filtro['valorEvaluacion']), Q.AND)
                    elif(filtro['propiedad'] == "fechaCreacion"):
                        fecha  = datetime.datetime.strptime(filtro['valorEvaluacion'], '%d-%m-%Y').date()
                        if(filtro['evaluacion'] == "0"):
                            query.add(Q(fechaCreacion=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "1"):
                            query.add(Q(fechaCreacion__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "2"):
                            query.add(Q(fechaCreacion__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "3"):
                            query.add(Q(fechaCreacion__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "4"):
                            query.add(Q(fechaCreacion__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                contactos = Contacto.objects.filter(query).values('id', 'persona__id', 'persona__nombreCompleto', 'estado','fechaCreacion', 'fechaModificacion','empresa__nombre')
                elementos = list(contactos)
                columnas = ['contacto-nombreCompleto','contacto-estado' , 'contacto-fechaCreacion', 'contacto-fechaModificacion', 'contacto-empresa']
                for elemento in elementos:
                    estado = ""
                    if elemento['estado'] == "0": estado = "Suscriptor"
                    elif elemento['estado'] == "1": estado = "Lead"
                    elif elemento['estado'] == "2": estado = "Oportunidad"
                    elif elemento['estado'] == "3": estado = "Cliente"
                    fila = [['contacto-nombreCompleto', elemento['persona__nombreCompleto']], 
                            ['contacto-estado', estado],
                            ['contacto-fechaCreacion', datetime.datetime.strftime(elemento['fechaCreacion'], '%d-%m-%Y')], 
                            ['contacto-fechaModificacion', datetime.datetime.strftime(elemento['fechaModificacion'], '%d-%m-%Y')],
                            ['contacto-empresa', elemento['empresa__nombre']]]
                    filas.append(fila)
            elif request.data["tipo"] == "6":
                query = Q()
                subquery1 = Q()
                subquery2 = Q()
                query.add(Q(propietario__id=idPropietario), Q.AND)
                for filtro in request.data["filtros"]:
                    if(filtro['propiedad']=="nombre"):
                        query.add(Q(nombre__contains=filtro['valorEvaluacion']), Q.AND)
                    if(filtro['propiedad']=="sector"):
                        query.add(Q(sector__contains=filtro['valorEvaluacion']), Q.AND)
                    elif(filtro['propiedad'] == "telefono"):
                        telefonos = Telefono.objects.filter(numero__contains = filtro['valorEvaluacion']).values('empresa__id')
                        empresasTelefono = [telefono['empresa__id'] for telefono in list(telefonos)]
                        query.add(Q(id__in=empresasTelefono), Q.AND)
                    elif(filtro['propiedad'] == "paisDir"):
                        direcciones = Direccion.objects.filter(pais__contains = filtro['valorEvaluacion']).values('empresa__id')
                        empresasDireccion = [direccion['empresa__id'] for direccion in list(direcciones)]
                        query.add(Q(id__in=empresasDireccion), Q.AND)
                    elif(filtro['propiedad'] == "estadoDir"):
                        direcciones = Direccion.objects.filter(estado__contains = filtro['valorEvaluacion']).values('empresa__id')
                        empresasDireccion = [direccion['empresa__id'] for direccion in list(direcciones)]
                        query.add(Q(id__in=empresasDireccion), Q.AND)
                    elif(filtro['propiedad'] == "ciudadDir"):
                        direcciones = Direccion.objects.filter(ciudad__contains = filtro['valorEvaluacion']).values('empresa__id')
                        empresasDireccion = [direccion['empresa__id'] for direccion in list(direcciones)]
                        query.add(Q(id__in=empresasDireccion), Q.AND)
                    elif(filtro['propiedad'] == "direccionDir"):
                        direcciones = Direccion.objects.filter(direccion__contains = filtro['valorEvaluacion']).values('empresa__id')
                        empresasDireccion = [direccion['empresa__id'] for direccion in list(direcciones)]
                        query.add(Q(id__in=empresasDireccion), Q.AND)
                    elif(filtro['propiedad'] == "tipo"):
                        query.add(Q(tipo=filtro['valorEvaluacion']), Q.AND)
                    elif(filtro['propiedad'] == "cantEmpleados"):
                        cantEmpleados = int(filtro['valorEvaluacion'])
                        if(filtro['evaluacion'] == "0"):
                            query.add(Q(cantEmpleados=cantEmpleados), Q.AND)
                        elif(filtro['evaluacion'] == "1"):
                            query.add(Q(cantEmpleados__lt=cantEmpleados), Q.AND)
                        elif(filtro['evaluacion'] == "2"):
                            query.add(Q(cantEmpleados__gt=cantEmpleados), Q.AND)
                        elif(filtro['evaluacion'] == "3"):
                            query.add(Q(cantEmpleados__lte=cantEmpleados), Q.AND)
                        elif(filtro['evaluacion'] == "4"):
                            query.add(Q(cantEmpleados__gte=cantEmpleados), Q.AND)
                    elif(filtro['propiedad'] == "contacto"):
                        contactos = Contacto.objects.filter(empresa__id__gte = 1).values('empresa__id')
                        contactosEmpresa = [contacto['empresa__id'] for contacto in list(contactos)]
                        if(filtro['valorEvaluacion'] == "0"):
                            query.add(~Q(id__in=contactosEmpresa), Q.AND) #revisar si funciona
                        elif(filtro['valorEvaluacion'] == "1"):
                            query.add(Q(id__in=contactosEmpresa), Q.AND) #revisar si funciona
                    elif(filtro['propiedad'] == "contactoNombre"):
                        contactos = Contacto.objects.filter(persona_nombreCompleto__contains=filtro['valorEvaluacion']).values('empresa__id')
                        contactosEmpresa = [contacto['empresa__id'] for contacto in list(contactos)]
                        query.add(Q(id__in=contactosEmpresa), Q.AND)
                    elif(filtro['propiedad'] == "fechaCreacion"):
                        fecha  = datetime.datetime.strptime(filtro['valorEvaluacion'], '%d-%m-%Y').date()
                        if(filtro['evaluacion'] == "0"):
                            query.add(Q(fechaCreacion=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "1"):
                            query.add(Q(fechaCreacion__lt=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "2"):
                            query.add(Q(fechaCreacion__gt=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                        elif(filtro['evaluacion'] == "3"):
                            query.add(Q(fechaCreacion__lte=datetime.datetime(fecha.year,fecha.month,fecha.day, 23,59,59)), Q.AND)
                        elif(filtro['evaluacion'] == "4"):
                            query.add(Q(fechaCreacion__gte=datetime.datetime(fecha.year,fecha.month,fecha.day, 0,0,0)), Q.AND)
                empresas = Empresa.objects.filter(query).values('id', 'nombre', 'sector', 'tipo','fechaCreacion', 'fechaModificacion')
                elementos = list(empresas)
                columnas = ['empresa-nombre','empresa-sector','empresa-tipo' , 'empresa-fechaCreacion', 'empresa-fechaModificacion']
                for elemento in elementos:
                    tipo = ""
                    if elemento['tipo'] == "0": tipo = "Suscriptor"
                    elif elemento['tipo'] == "1": tipo = "Lead"
                    elif elemento['tipo'] == "2": tipo = "Oportunidad"
                    elif elemento['tipo'] == "3": tipo = "Cliente"
                    fila = [['empresa-nombre', elemento['nombre']], 
                            ['empresa-sector', elemento['sector']],
                            ['empresa-tipo', tipo],
                            ['empresa-fechaCreacion', datetime.datetime.strftime(elemento['fechaCreacion'], '%d-%m-%Y')], 
                            ['empresa-fechaModificacion', datetime.datetime.strftime(elemento['fechaModificacion'], '%d-%m-%Y')]]
                    filas.append(fila)
        return Response({"columnas": columnas, "filas": filas}, status = status.HTTP_200_OK)

class RegistrarReporte(APIView):
    def post(self, request,id=0):
        if request.data["idReporte"] is not None and request.data["idReporte"]>0:
            idReporte = request.data["idReporte"]
            Columna.objects.filter(Q(reporte__id = idReporte)).delete()
            Fila.objects.filter(Q(reporte__id = idReporte)).delete()
            Filtro.objects.filter(Q(reporte__id = id)).delete()
            columnas = request.data["columnas"]
            filas = request.data['filas']
            filtros = request.data['filtros']
            for filtro in filtros:
                campos = {'reporte': idReporte,
                          'propiedad': filtro['propiedad'], #cambiar esta parte
                          'evaluacion': filtro['evaluacion'],
                          'valorEvaluacion': str(filtro['valorEvaluacion']) ,
                          'nombre': filtro['nombre']
                        }
                filtro_serializer = FiltroSerializer(data = campos)
                if filtro_serializer.is_valid():
                    filtro_serializer.save()
            for columna in columnas:
                campos_columna = {
                 'nombre': columna,
                 'reporte': idReporte
                }
                columna_serializer = ColumnaSerializer(data=campos_columna)
                if columna_serializer.is_valid():
                    columna_serializer.save()
            for fila in filas:
                contenido = ""
                for dato in fila:
                    contenido = contenido + dato[0] + ":"
                    if dato[0] == "plan-estado" or dato[0] == "programa-estado" or dato[0] == "campana-estado" or dato[0] == "recurso-estado"  or dato[0] == "oportunidad-estado":
                        if dato[1] == "No vigente":
                            contenido = contenido + "0" + ";"
                        elif dato[1] == "Vigente":
                            contenido = contenido + "1" + ";"
                    elif dato[0] == "programa-tipo":
                        if dato[1] == "Programa":
                            contenido = contenido + "0" + ";"
                        else:
                            contenido = contenido + "1" + ";" 
                    elif dato[0] == "campana-tipo":
                        if dato[1] == "Campaña de programa" or dato[1] == "Campana de programa":
                            contenido = contenido + "0" + ";"
                        else:
                            contenido = contenido + "1" + ";"
                    elif dato[0] == "recurso-tipo":
                        if dato[1] == "Correo":
                            contenido = contenido + "0" + ";"
                        elif dato[1] == "Publicación" or dato[1] == "Publicacion":
                            contenido = contenido + "1" + ";" 
                        elif dato[1] == "Página web" or dato[1] == "Pagina web":
                            contenido = contenido + "2" + ";"
                    elif dato[0] == "oportunidad-tipo":
                        if dato[1] == "Negocio existente":
                            contenido = contenido + "0" + ";"
                        else:
                            contenido = contenido + "1" + ";"
                    elif dato[0] == "oportunidad-etapa":
                        if dato[1] == "Calificación" or dato[1] == "Calificacion":
                            contenido = contenido + "0" + ";"
                        elif dato[1] == "Necesidad de análisis" or dato[1] == "Necesidad de analisis":
                            contenido = contenido + "1" + ";"
                        elif dato[1] == "Propuesta":
                            contenido = contenido + "2" + ";"
                        elif dato[1] == "Negociación" or dato[1] == "Negociacion":
                            contenido = contenido + "3" + ";"
                        elif dato[1] == "Perdida":
                            contenido = contenido + "4" + ";"
                        elif dato[1] == "Ganada":
                            contenido = contenido + "5" + ";"
                    elif dato[0] == "contacto-estado":
                        if dato[1] == "Suscriptor":
                            contenido = contenido + "0" + ";"
                        elif dato[1] == "Lead":
                            contenido = contenido + "1" + ";" 
                        elif dato[1] == "Oportunidad":
                            contenido = contenido + "2" + ";"
                        elif dato[1] == "Cliente":
                            contenido = contenido + "3" + ";"
                    elif dato[0] == "empresa-tipo":
                        if dato[1] == "Cliente potencial":
                            contenido = contenido + "0" + ";"
                        elif dato[1] == "Socio":
                            contenido = contenido + "1" + ";" 
                        elif dato[1] == "Revendedor":
                            contenido = contenido + "2" + ";"
                        elif dato[1] == "Proveedor":
                            contenido = contenido + "3" + ";"
                    else:
                        contenido = contenido + dato[1] + ";"
                campos_fila = {
                 'contenido': contenido,
                 'reporte': idReporte
                }
                fila_serializer = FilaSerializer(data=campos_fila)
                if fila_serializer.is_valid():
                    fila_serializer.save()
            reporte = Reporte.objects.filter(id=idReporte).first()
            campos_reporte = {
                'nombre': request.data["nombre"],
                 'descripcion': request.data["descripcion"],
                 'tipo': request.data["tipo"],
                 'propietario': request.data["propietario"]
            }
            reporte_serializer = ReporteSerializer(reporte, data=campos_reporte)
            if reporte_serializer.is_valid():
                reporte_serializer.save()
        else:
            campos_reporte = {
                'nombre': request.data["nombre"],
                 'descripcion': request.data["descripcion"],
                 'tipo': request.data["tipo"],
                 'propietario': request.data["propietario"]
            }
            reporte_serializer = ReporteSerializer(data=campos_reporte)
            if reporte_serializer.is_valid():
                idReporte = reporte_serializer.save()
                idReporte = idReporte.id
            columnas = request.data["columnas"]
            filas = request.data['filas']
            filtros = request.data['filtros']
            for filtro in filtros:
                campos = {'reporte': idReporte,
                          'propiedad': filtro['propiedad'], #cambiar esta parte
                          'evaluacion': filtro['evaluacion'],
                          'valorEvaluacion': str(filtro['valorEvaluacion']) ,
                          'nombre': filtro['nombre']
                        }
                filtro_serializer = FiltroSerializer(data = campos)
                if filtro_serializer.is_valid():
                    filtro_serializer.save()
            for columna in columnas:
                campos_columna = {
                 'nombre': columna,
                 'reporte': idReporte
                }
                columna_serializer = ColumnaSerializer(data=campos_columna)
                if columna_serializer.is_valid():
                    columna_serializer.save()
            for fila in filas:
                contenido = ""
                for dato in fila:
                    contenido = contenido + dato[0] + ":"
                    if dato[0] == "plan-estado" or dato[0] == "programa-estado" or dato[0] == "campana-estado" or dato[0] == "recurso-estado"  or dato[0] == "oportunidad-estado":
                        if dato[1] == "No vigente":
                            contenido = contenido + "0" + ";"
                        elif dato[1] == "Vigente":
                            contenido = contenido + "1" + ";"
                    elif dato[0] == "programa-tipo":
                        if dato[1] == "Programa":
                            contenido = contenido + "0" + ";"
                        else:
                            contenido = contenido + "1" + ";" 
                    elif dato[0] == "campana-tipo":
                        if dato[1] == "Campaña de programa" or dato[1] == "Campana de programa":
                            contenido = contenido + "0" + ";"
                        else:
                            contenido = contenido + "1" + ";"
                    elif dato[0] == "recurso-tipo":
                        if dato[1] == "Correo":
                            contenido = contenido + "0" + ";"
                        elif dato[1] == "Publicación" or dato[1] == "Publicacion":
                            contenido = contenido + "1" + ";" 
                        elif dato[1] == "Página web" or dato[1] == "Pagina web":
                            contenido = contenido + "2" + ";"
                    elif dato[0] == "oportunidad-tipo":
                        if dato[1] == "Negocio existente":
                            contenido = contenido + "0" + ";"
                        else:
                            contenido = contenido + "1" + ";"
                    elif dato[0] == "oportunidad-etapa":
                        if dato[1] == "Calificación" or dato[1] == "Calificacion":
                            contenido = contenido + "0" + ";"
                        elif dato[1] == "Necesidad de análisis" or dato[1] == "Necesidad de analisis":
                            contenido = contenido + "1" + ";"
                        elif dato[1] == "Propuesta":
                            contenido = contenido + "2" + ";"
                        elif dato[1] == "Negociación" or dato[1] == "Negociacion":
                            contenido = contenido + "3" + ";"
                        elif dato[1] == "Perdida":
                            contenido = contenido + "4" + ";"
                        elif dato[1] == "Ganada":
                            contenido = contenido + "5" + ";"
                    elif dato[0] == "contacto-estado":
                        if dato[1] == "Suscriptor":
                            contenido = contenido + "0" + ";"
                        elif dato[1] == "Lead":
                            contenido = contenido + "1" + ";" 
                        elif dato[1] == "Oportunidad":
                            contenido = contenido + "2" + ";"
                        elif dato[1] == "Cliente":
                            contenido = contenido + "3" + ";"
                    elif dato[0] == "empresa-tipo":
                        if dato[1] == "Cliente potencial":
                            contenido = contenido + "0" + ";"
                        elif dato[1] == "Socio":
                            contenido = contenido + "1" + ";" 
                        elif dato[1] == "Revendedor":
                            contenido = contenido + "2" + ";"
                        elif dato[1] == "Proveedor":
                            contenido = contenido + "3" + ";"
                    else:
                        contenido = contenido + dato[1] + ";"
                campos_fila = {
                 'contenido': contenido,
                 'reporte': idReporte
                }
                fila_serializer = FilaSerializer(data=campos_fila)
                if fila_serializer.is_valid():
                    fila_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'Reporte registrado correctamente',
                        },)	

class BuscarDetalleReporte(APIView):
    def get(self, request,id):
        if id != "" and id > 0:
            reporte = Reporte.objects.filter(id=id).values('id','nombre','descripcion','tipo' ,'propietario__id').first()
            if reporte is not None:
                campos_reporte = {
                    "idReporte": reporte['id'],
                    "nombre": reporte['nombre'],
                    "descripcion": reporte['descripcion'],
                    "tipo": reporte['tipo'],
                    "propietario": reporte['propietario__id'],
                    "columnas": [],
                    "filas": [],
                    "filtros": [],
                }
                
                filtros = Filtro.objects.filter(reporte__id=reporte['id']).values('id','propiedad','evaluacion', 'valorEvaluacion','nombre')
                campos_reporte['filtros'] = list(filtros)
                columnas = Columna.objects.filter(reporte__id=reporte['id']).values('id','nombre')
                campos_reporte['columnas'] = [d['nombre'] for d in columnas]

                filas = Fila.objects.filter(reporte__id=reporte['id']).values('id','contenido')
                filasLista = [d['contenido'] for d in filas]
                
                for fila in filasLista:
                    datos = str(fila).split(";")
                    datosFila = []
                    for dato in datos:
                        if dato != "":
                            propiedad_valor = dato.split(":")
                            propiedad = propiedad_valor[0]
                            valor = propiedad_valor[1]
                            if(propiedad == "contacto-estado"):
                                if(valor=="0"): valor = "Suscriptor"
                                elif(valor=="1"): valor = "Lead"
                                elif(valor=="2"): valor = "Oportunidad"
                                elif(valor=="3"): valor = "Cliente"
                            elif(propiedad == "empresa-tipo"):
                                if(valor=="0"): valor = "Cliente potencial"
                                elif(valor=="1"): valor = "Socio"
                                elif(valor=="2"): valor = "Revendedor"
                                elif(valor=="3"): valor = "Proveedor"
                            elif(propiedad == "plan-estado" or propiedad == "programa-estado" or propiedad == "campana-estado" or propiedad == "recurso-estado" or propiedad == "oportunidad-estado"):
                                if(valor=="0"): valor = "No vigente"
                                elif(valor=="1"): valor = "Vigente"
                            elif(propiedad == "programa-tipo"):
                                if(valor=="0"): valor = "Programa"
                                elif(valor=="1"): valor = "Campaña stand-alone"
                            elif(propiedad == "campana-tipo"):
                                if(valor=="0"): valor = "Campaña de programa"
                                elif(valor=="1"): valor = "Campaña stand-alone"
                            elif(propiedad == "recurso-tipo"):
                                if(valor=="0"): valor = "Correo"
                                elif(valor=="1"): valor = "Publicación"
                                elif(valor=="2"): valor = "Página web"
                            elif(propiedad == "oportunidad-tipo"):
                                if(valor=="0"): valor = "Negocio existente"
                                elif(valor=="1"): valor = "Nuevo negocio"
                            elif(propiedad == "oportunidad-etapa"):
                                if(valor=="0"): valor = "Calificación"
                                elif(valor=="1"): valor = "Necesidad de análisis"
                                elif(valor=="2"): valor = "Propuesta"
                                elif(valor=="3"): valor = "Negociación"
                                elif(valor=="4"): valor = "Perdida"
                                elif(valor=="5"): valor = "Ganada"
                            datosFila.append([propiedad, valor])
                    campos_reporte['filas'].append(datosFila)
                return Response(campos_reporte, status = status.HTTP_200_OK)
            else:
                return Response('No se ha encontrado el reporte', status = status.HTTP_200_OK)
        return Response('No se ha encontrado el reporte', status = status.HTTP_200_OK)

class CrearComponenteInforme(APIView):
    def post(self, request,id=0):
        elementos = []
        idPropietario = int(request.data["propietario"])
        tipo = request.data["tipo"]
        idReporte = request.data["idReporte"]
        #reporte = Reporte.objects.filter(id=idReporte).values('id','tipo').first()
        columnas = Columna.objects.filter(reporte__id=idReporte).values('id','nombre')
        filas = Fila.objects.filter(reporte__id=idReporte).values('id','contenido')
        labelsx = []
        cantsy = []
        if tipo == "0" or tipo == "1" or tipo=="2":
            ejex = request.data["ejex"]
            ejey = request.data["ejey"]
            if ejex=="plan-estado":
                labelsx = ["No vigente", "Vigente"]
                cantsy = [0,0]
                for fila in filas:
                    datos = str(fila).split(";")
                    index=0
                    presupuesto = 0
                    for dato in datos:
                        par = str(dato).split(":")
                        if par[0] == 'plan-estado':
                            if par[1]=='0':
                                index = 0
                            elif par[1] == '1':
                                index = 1
                    if ejey == "cantidad":
                        cantsy[index] = cantsy[index] + 1
                    elif ejey == "plan-presupuesto":
                        for dato in datos:
                            par = str(dato).split(":")
                            if par[0] == 'plan-presupuesto':
                                cantsy[index] = cantsy[index] + float(par[1])
            # elif ejex == "plan-fechaCreacion":
            #     fechas = []
            #     for fila in filas:
            #         datos = str(fila).split(";")
            #         for dato in datos:
            #             par = str(dato).split(":")
            #             if par[0] == 'plan-fechaCreacion':
            #                 fecha  = datetime.datetime.strptime(par[1], '%d-%m-%Y').date()
            #                 fecha = datetime.datetime(fecha.year,fecha.month,fecha.day,0,0,0)
            #                 fechas.append(fecha)
                
            #         #seleccionar todas las fechas y encontrar la menor y mayor
            #     #crear el arreglo de labels
            #     for fila in filas:
            #          #obtener a que label pertenece la fila
            #         if ejey == "cantidad":
            #             #segun lo obtenido se suma 1 a cantsy segun el label
            #         elif ejey == "plan-presupuesto":
            #             #segun lo obtenido se encuentra el valor de presupuesto y se suma a cantsy segun el label
            # elif ejex == "plan-inicioVigencia":
            #     for fila in filas:
            #         e
            # elif ejex == "plan-finVigencia":
                for fila in filas:
                    e
            elif ejex=="programa-estado":
                labelsx = ["No vigente", "Vigente"]
                cantsy = [0,0]
                for fila in filas:
                    datos = str(fila).split(";")
                    index=0
                    presupuesto = 0
                    for dato in datos:
                        par = str(dato).split(":")
                        if par[0] == 'programa-estado':
                            if par[1]=='0':
                                index = 0
                            elif par[1] == '1':
                                index = 1
                    if ejey == "cantidad":
                        cantsy[index] = cantsy[index] + 1
                    elif ejey == "programa-presupuesto":
                        for dato in datos:
                            par = str(dato).split(":")
                            if par[0] == 'programa-presupuesto':
                                cantsy[index] = cantsy[index] + float(par[1])
            elif ejex=="campana-estado":
                labelsx = ["No vigente", "Vigente"]
                cantsy = [0,0]
                for fila in filas:
                    datos = str(fila).split(";")
                    index=0
                    presupuesto = 0
                    for dato in datos:
                        par = str(dato).split(":")
                        if par[0] == 'campana-estado':
                            if par[1]=='0':
                                index = 0
                            elif par[1] == '1':
                                index = 1
                    if ejey == "cantidad":
                        cantsy[index] = cantsy[index] + 1
                    elif ejey == "campana-presupuesto":
                        for dato in datos:
                            par = str(dato).split(":")
                            if par[0] == 'campana-presupuesto':
                                cantsy[index] = cantsy[index] + float(par[1])
            elif ejex=="campana-tipo":
                labelsx = ["Campaña de programa", "Campaña stand-alone"]
                cantsy = [0,0]
                for fila in filas:
                    datos = str(fila).split(";")
                    index=0
                    presupuesto = 0
                    for dato in datos:
                        par = str(dato).split(":")
                        if par[0] == 'campana-tipo':
                            if par[1]=='0':
                                index = 0
                            elif par[1] == '1':
                                index = 1
                    if ejey == "cantidad":
                        cantsy[index] = cantsy[index] + 1
                    elif ejey == "campana-presupuesto":
                        for dato in datos:
                            par = str(dato).split(":")
                            if par[0] == 'campana-presupuesto':
                                cantsy[index] = cantsy[index] + float(par[1])
            elif ejex=="recurso-estado":
                labelsx = ["No vigente", "Vigente"]
                cantsy = [0,0]
                for fila in filas:
                    datos = str(fila).split(";")
                    index=0
                    presupuesto = 0
                    for dato in datos:
                        par = str(dato).split(":")
                        if par[0] == 'recurso-estado':
                            if par[1]=='0':
                                index = 0
                            elif par[1] == '1':
                                index = 1
                    if ejey == "cantidad":
                        cantsy[index] = cantsy[index] + 1
                    elif ejey == "recurso-presupuesto":
                        for dato in datos:
                            par = str(dato).split(":")
                            if par[0] == 'recurso-presupuesto':
                                cantsy[index] = cantsy[index] + float(par[1])
            elif ejex=="recurso-tipo":
                labelsx = ["Correo", "Publicación", "Página web"]
                cantsy = [0,0,0]
                for fila in filas:
                    datos = str(fila).split(";")
                    index=0
                    presupuesto = 0
                    for dato in datos:
                        par = str(dato).split(":")
                        if par[0] == 'recurso-tipo':
                            if par[1]=='0':
                                index = 0
                            elif par[1] == '1':
                                index = 1
                            elif par[1] == '2':
                                index = 2
                    if ejey == "cantidad":
                        cantsy[index] = cantsy[index] + 1
                    elif ejey == "recurso-presupuesto":
                        for dato in datos:
                            par = str(dato).split(":")
                            if par[0] == 'recurso-presupuesto':
                                cantsy[index] = cantsy[index] + float(par[1])
            elif ejex=="oportunidad-estado":
                labelsx = ["No vigente", "Vigente"]
                cantsy = [0,0]
                for fila in filas:
                    datos = str(fila).split(";")
                    index=0
                    presupuesto = 0
                    for dato in datos:
                        par = str(dato).split(":")
                        if par[0] == 'oportunidad-estado':
                            if par[1]=='0':
                                index = 0
                            elif par[1] == '1':
                                index = 1
                    if ejey == "cantidad":
                        cantsy[index] = cantsy[index] + 1
                    elif ejey == "oportunidad-presupuesto":
                        for dato in datos:
                            par = str(dato).split(":")
                            if par[0] == 'oportunidad-presupuesto':
                                cantsy[index] = cantsy[index] + float(par[1])
            elif ejex=="oportunidad-tipo":
                labelsx = ["Negocio existente", "Nuevo negocio"]
                cantsy = [0,0]
                for fila in filas:
                    datos = str(fila).split(";")
                    index=0
                    presupuesto = 0
                    for dato in datos:
                        par = str(dato).split(":")
                        if par[0] == 'oportunidad-tipo':
                            if par[1]=='0':
                                index = 0
                            elif par[1] == '1':
                                index = 1
                    if ejey == "cantidad":
                        cantsy[index] = cantsy[index] + 1
                    elif ejey == "oportunidad-importe":
                        for dato in datos:
                            par = str(dato).split(":")
                            if par[0] == 'oportunidad-importe':
                                cantsy[index] = cantsy[index] + float(par[1])
            elif ejex=="oportunidad-etapa":
                labelsx = ["Calificación", "Necesidad de análisis", "Propuesta", "Negociación", "Perdida", "Ganada"]
                cantsy = [0,0,0,0,0,0]
                for fila in filas:
                    datos = str(fila).split(";")
                    index=0
                    presupuesto = 0
                    for dato in datos:
                        par = str(dato).split(":")
                        if par[0] == 'oportunidad-etapa':
                            if par[1]=='0':
                                index = 0
                            elif par[1] == '1':
                                index = 1
                            elif par[1] == '2':
                                index = 2
                            elif par[1] == '3':
                                index = 3
                            elif par[1] == '4':
                                index = 4
                            elif par[1] == '5':
                                index = 5
                    if ejey == "cantidad":
                        cantsy[index] = cantsy[index] + 1
                    elif ejey == "oportunidad-importe":
                        for dato in datos:
                            par = str(dato).split(":")
                            if par[0] == 'oportunidad-importe':
                                cantsy[index] = cantsy[index] + float(par[1])
            elif ejex=="contacto-estado":
                labelsx = ["Suscriptor", "Lead", "Oportunidad", "Cliente"]
                cantsy = [0,0,0,0]
                for fila in filas:
                    datos = str(fila).split(";")
                    index=0
                    presupuesto = 0
                    for dato in datos:
                        par = str(dato).split(":")
                        if par[0] == 'contacto-estado':
                            if par[1]=='0':
                                index = 0
                            elif par[1] == '1':
                                index = 1
                            elif par[1] == '2':
                                index = 2
                            elif par[1] == '3':
                                index = 3
                    if ejey == "cantidad":
                        cantsy[index] = cantsy[index] + 1
            elif ejex=="empresa-tipo":
                labelsx = ["Cliente potencial", "Socio", "Revendedor", "Proveedor"]
                cantsy = [0,0,0,0]
                for fila in filas:
                    datos = str(fila).split(";")
                    index=0
                    presupuesto = 0
                    for dato in datos:
                        par = str(dato).split(":")
                        if par[0] == 'empresa-tipo':
                            if par[1]=='0':
                                index = 0
                            elif par[1] == '1':
                                index = 1
                            elif par[1] == '2':
                                index = 2
                            elif par[1] == '3':
                                index = 3
                    if ejey == "cantidad":
                        cantsy[index] = cantsy[index] + 1
                    elif ejey == "empresa-cantEmpleados":
                        for dato in datos:
                            par = str(dato).split(":")
                            if par[0] == 'empresa-cantEmpleados':
                                cantsy[index] = cantsy[index] + int(par[1])
        return Response({"labels": labelsx, "cantidades": cantsy}, status = status.HTTP_200_OK)

class FiltrarDashboards(APIView):
    def post(self, request,id=0):
        cadena = request.data["cadena"]
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
        
        dashboards = Dashboard.objects.filter((subquery1 | subquery3) & query).values('id', 'nombre','fechaCreacion', 'fechaModificacion')
        listaDashboards = list(dashboards)
        for dashboard in listaDashboards:
            dashboard['fechaCreacion'] = datetime.datetime.strftime(dashboard['fechaCreacion'], '%d-%m-%Y')
            dashboard['fechaModificacion'] = datetime.datetime.strftime(dashboard['fechaModificacion'], '%d-%m-%Y')
        return Response(listaDashboards, status = status.HTTP_200_OK)

class RegistrarDashboard(APIView):
    def post(self, request,id=0):
        if request.data["idDashboard"] is not None and request.data["idDashboard"]>0:
            idDashboard = request.data["idDashboard"]
            ComponenteLabel.objects.filter(Q(componente__dashboard__id = idDashboard)).delete()
            ComponenteCantidad.objects.filter(Q(componente__dashboard__id = idDashboard)).delete()
            Componente.objects.filter(Q(dashboard__id = idDashboard)).delete()
            componentes = request.data["componentes"]
            for componente in componentes:
                campos = {'dashboard': idDashboard,
                          'tipo': componente['tipo'], #cambiar esta parte
                          'titulo': componente['titulo'],
                          'subtitulo': componente['subtitulo']
                        }
                componente_serializer = ComponenteSerializer(data = campos)
                idComponente = 0
                if componente_serializer.is_valid():
                    idComponente = componente_serializer.save()
                    idComponente = idComponente.id
                for label in componente['labels']:
                    campos_label = {
                        'componente': idComponente,
                        'label': label
                    }
                    label_serializer = ComponenteLabelSerializer(data = campos_label)
                    if label_serializer.is_valid():
                        label_serializer.save()
                for cantidad in componente['cantidades']:
                    campos_cantidad = {
                        'componente': idComponente,
                        'cantidad': cantidad
                    }
                    cantidad_serializer = ComponenteCantidadSerializer(data = campos_cantidad)
                    if cantidad_serializer.is_valid():
                        cantidad_serializer.save()
            dashboard = Dashboard.objects.filter(id=idDashboard).first()
            if request.data["principal"] == True: Dashboard.objects.filter(propietario__id=request.data["propietario"]).update(principal=False)
            campos_dashboard = {
                'nombre': request.data["nombre"],
                 'descripcion': request.data["descripcion"],
                 'principal': request.data["principal"],
                 'propietario': request.data["propietario"]
            }
            dashboard_serializer = DashboardSerializer(dashboard, data=campos_dashboard)
            if dashboard_serializer.is_valid():
                dashboard_serializer.save()
        else:
            if request.data["principal"] == True: Dashboard.objects.filter(propietario__id=request.data["propietario"]).update(principal=False)
            campos_dashboard = {
                'nombre': request.data["nombre"],
                 'descripcion': request.data["descripcion"],
                 'principal': request.data["principal"],
                 'propietario': request.data["propietario"]
            }
            dashboard_serializer = DashboardSerializer(data=campos_dashboard)
            if dashboard_serializer.is_valid():
                idDashboard = dashboard_serializer.save()
                idDashboard = idDashboard.id
            componentes = request.data["componentes"]
            for componente in componentes:
                campos = {'dashboard': idDashboard,
                          'tipo': componente['tipo'], #cambiar esta parte
                          'titulo': componente['titulo'],
                          'subtitulo': componente['subtitulo']
                        }
                componente_serializer = ComponenteSerializer(data = campos)
                idComponente = 0
                if componente_serializer.is_valid():
                    idComponente = componente_serializer.save()
                    idComponente = idComponente.id
                for label in componente['labels']:
                    campos_label = {
                        'componente': idComponente,
                        'label': label
                    }
                    label_serializer = ComponenteLabelSerializer(data = campos_label)
                    if label_serializer.is_valid():
                        label_serializer.save()
                for cantidad in componente['cantidades']:
                    campos_cantidad = {
                        'componente': idComponente,
                        'cantidad': cantidad
                    }
                    cantidad_serializer = ComponenteCantidadSerializer(data = campos_cantidad)
                    if cantidad_serializer.is_valid():
                        cantidad_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'Dashboard registrado correctamente',
                        },)	

class BuscarDetalleDashboard(APIView):
    def get(self, request,id):
        if id != "" and id > 0:
            dashboard = Dashboard.objects.filter(id=id).values('id','nombre','descripcion','principal' ,'propietario__id').first()
            if dashboard is not None:
                campos_dashboard = {
                    "idDashboard": dashboard['id'],
                    "nombre": dashboard['nombre'],
                    "descripcion": dashboard['descripcion'],
                    "principal": dashboard['principal'],
                    "propietario": dashboard['propietario__id'],
                    "componentes": [],
                    "filtros": [],
                }
                #filtros = Filtro.objects.filter(reporte__id=reporte['id']).values('id','propiedad','evaluacion', 'valorEvaluacion','nombre')
                #campos_reporte['filtros'] = list(filtros)
                componentes = Componente.objects.filter(dashboard__id=dashboard['id']).values('id','tipo','titulo','subtitulo')
                campos_dashboard['componentes'] = list(componentes)
                for componente in campos_dashboard['componentes']:
                    labels = ComponenteLabel.objects.filter(componente__id=componente['id']).values('id','label')
                    labelLista = [d['label'] for d in labels]
                    componente['labels'] = labelLista
                    cantidades = ComponenteCantidad.objects.filter(componente__id=componente['id']).values('id','cantidad')
                    cantidadLista = [d['cantidad'] for d in cantidades]
                    componente['cantidades'] = cantidadLista
                return Response(campos_dashboard, status = status.HTTP_200_OK)
            else:
                return Response('No se ha encontrado el dashboard', status = status.HTTP_200_OK)
        return Response('No se ha encontrado el dashboard', status = status.HTTP_200_OK)

class EliminarDashboard(APIView):
    def delete(self, request,id=0):
        if id != "" and id > 0:
            ComponenteLabel.objects.filter(Q(componente__dashboard__id = id)).delete()
            ComponenteCantidad.objects.filter(Q(componente__dashboard__id = id)).delete()
            Componente.objects.filter(Q(dashboard__id = id)).delete()
            Dashboard.objects.filter(id=id).delete()
            return Response('Dashboard eliminado',status=status.HTTP_200_OK)
        return Response('Dashboard no encontrado',status=status.HTTP_200_OK)

class FiltrarFlujos(APIView):
    def post(self, request,id=0):
        cadena = request.data["cadena"]
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
        
        flujos = Flujo.objects.filter((subquery1 | subquery3) & query).values('id', 'nombre','fechaCreacion', 'fechaModificacion')
        listaFLujos = list(flujos)
        for flujo in listaFLujos:
            flujo['fechaCreacion'] = datetime.datetime.strftime(flujo['fechaCreacion'], '%d-%m-%Y')
            flujo['fechaModificacion'] = datetime.datetime.strftime(flujo['fechaModificacion'], '%d-%m-%Y')
        return Response(listaFLujos, status = status.HTTP_200_OK)

class RegistrarFlujo(APIView):
    def post(self, request,id=0):
        if request.data["idFlujo"] is not None and request.data["idFlujo"]>0:
            idFlujo = request.data["idFlujo"]
            flujo = Flujo.objects.filter(id=idFlujo).first()
            campos_flujo = {
                'nombre': request.data["nombre"],
                 'descripcion': request.data["descripcion"],
                 'contenido': request.data["contenido"],
                 'propietario': request.data["propietario"]
            }
            flujo_serializer = FlujoSerializer(flujo, data=campos_flujo)
            if flujo_serializer.is_valid():
                flujo_serializer.save()
        else:
            campos_flujo = {
                'nombre': request.data["nombre"],
                 'descripcion': request.data["descripcion"],
                 'contenido': request.data["contenido"],
                 'propietario': request.data["propietario"]
            }
            flujo_serializer = FlujoSerializer(data=campos_flujo)
            if flujo_serializer.is_valid():
                flujo_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'Flujo registrado correctamente',
                        },)	

class BuscarDetalleFlujo(APIView):
    def get(self, request,id):
        if id != "" and id > 0:
            flujo = Flujo.objects.filter(id=id).values('id', 'nombre', 'descripcion', 'contenido','propietario__id').first()
            if flujo is not None:
                campos_flujo = {
                    "idFlujo": flujo['id'],
                    "nombre": flujo['nombre'],
                    "descripcion": flujo['descripcion'],
                    "contenido": flujo['contenido'],
                    "propietario": flujo['propietario__id'],
                }
                return Response(campos_flujo, status = status.HTTP_200_OK)
            else:
                return Response('No se ha encontrado el flujo', status = status.HTTP_200_OK)
        return Response('No se ha encontrado el flujo', status = status.HTTP_200_OK)

class EliminarFlujo(APIView):
    def delete(self, request,id=0):
        if id != "" and id > 0:
            Flujo.objects.filter(id = id).delete()
            return Response('Flujo eliminado',status=status.HTTP_200_OK)
        return Response('Flujo no encontrado',status=status.HTTP_200_OK)

class BuscarPrincipalDashboard(APIView):
    def get(self, request,id):
        if id != "" and id > 0:
            dashboard = Dashboard.objects.filter(Q(propietario__id=id)& Q(principal=True)).values('id','nombre','descripcion','principal' ,'propietario__id').first()
            if dashboard is not None:
                campos_dashboard = {
                    "idDashboard": dashboard['id'],
                    "nombre": dashboard['nombre'],
                    "descripcion": dashboard['descripcion'],
                    "principal": dashboard['principal'],
                    "propietario": dashboard['propietario__id'],
                    "componentes": [],
                    "filtros": [],
                }
                #filtros = Filtro.objects.filter(reporte__id=reporte['id']).values('id','propiedad','evaluacion', 'valorEvaluacion','nombre')
                #campos_reporte['filtros'] = list(filtros)
                componentes = Componente.objects.filter(dashboard__id=dashboard['id']).values('id','tipo','titulo','subtitulo')
                campos_dashboard['componentes'] = list(componentes)
                for componente in campos_dashboard['componentes']:
                    labels = ComponenteLabel.objects.filter(componente__id=componente['id']).values('id','label')
                    labelLista = [d['label'] for d in labels]
                    componente['labels'] = labelLista
                    cantidades = ComponenteCantidad.objects.filter(componente__id=componente['id']).values('id','cantidad')
                    cantidadLista = [d['cantidad'] for d in cantidades]
                    componente['cantidades'] = cantidadLista
                return Response(campos_dashboard, status = status.HTTP_200_OK)
            else:
                return Response({}, status = status.HTTP_200_OK)
        return Response({}, status = status.HTTP_200_OK)