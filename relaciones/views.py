from django.shortcuts import render
from django.db.models import Q
from rest_framework import status
from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core import serializers as core_serializers
import datetime
from django.utils import timezone
from relaciones.models import *
from relaciones.serializers import *
from usuarios.models import *
from usuarios.serializers import *
from marketing.serializers import FiltroSerializer
from marketing.models import Filtro, CampanaXContacto, RecursoXContacto, OportunidadXContacto
from sistema.serializers import LogSerializer
from sistema.models import Log
# Create your views here.


class BuscarCorreosNoDisponibles(APIView):
    def post (self, request, id=0):
        idPropietario = int(request.data["propietario"])
        tipoDeCorreo = request.data["tipo"]
        resultado = []
        if tipoDeCorreo == "0":
            correosNoDisponibles = CuentaCorreo.objects.filter(usuario__id__gte = 1).values('direccion')
            resultado = [d['direccion'] for d in correosNoDisponibles]
        elif tipoDeCorreo == "1":
            correosNoDisponibles = CuentaCorreo.objects.filter(contacto__id__gte = 1, contacto__propietario__id = idPropietario).values('direccion')
            resultado = [d['direccion'] for d in correosNoDisponibles]
        return Response(resultado, status = status.HTTP_200_OK)
    
class BuscarNombresNoDisponibles(APIView):
    def post (self, request, id=0):
        idPropietario = int(request.data["propietario"])
        resultado = []
        nombresNoDisponibles = Empresa.objects.filter(propietario__id = idPropietario).values('nombre')
        resultado = [d['nombre'] for d in nombresNoDisponibles]
        return Response(resultado, status = status.HTTP_200_OK)

class BuscarDetalleContacto(APIView):
    def get(self, request,id):
        if id is not None and id > 0:
            contacto = Contacto.objects.filter(id=id).values('id','persona__id', 'persona__nombreCompleto', 'calificado', 'estado', 'propietario__id').first()
            if contacto is not None:
                campos_contacto = {
                    "idContacto": contacto['id'],
                    "idPersona": contacto['persona__id'],
                    "nombreCompleto": contacto['persona__nombreCompleto'],
                    "calificado": contacto['calificado'],
                    "estado": contacto['estado'],
                    "propietario": contacto['propietario__id'],
                    "telefonos": [],
                    "direcciones": [],
                    "correo":{"servicio": "", "direccion": ""},
                    "redes": [],
                    "campañas": [],
                    "recursos": [],
                    "oportunidades": [],
                    #"actividades": [],
                    "empresas": [],
                    "correosNoDisponibles": []
                }
                telefonos = Telefono.objects.filter(contacto__id = contacto['id']).values('numero','principal')
                direcciones = Direccion.objects.filter(contacto__id = contacto['id']).values('pais','estado','ciudad','direccion','principal')
                correo = CuentaCorreo.objects.filter(contacto__id = contacto['id']).values('servicio','direccion').first()
                redes = CuentaRedSocial.objects.filter(contacto__id = contacto['id']).values('redSocial','nombreUsuario')

                fechaHoy  = datetime.datetime.now()
                campanas = CampanaXContacto.objects.filter(contacto__id = contacto['id']).values('campana__descripcion','campana__tipo', 'campana__estado','campana__inicioVigencia', 'campana__finVigencia')
                campos_contacto['campanas'] = list(campanas)
                for campana in campos_contacto['campanas']:
                    campana['descripcion'] = campana['campana__descripcion']
                    if campana['campana__tipo'] == "0": campana['tipo'] = "Campaña de programa"
                    elif campana['campana__tipo'] == "1": campana['tipo'] = "Campaña stand-alone"
                    fecha = datetime.datetime(fechaHoy.year,fechaHoy.month,fechaHoy.day, 0,0,0)
                    inicioVigencia = campana['campana__inicioVigencia'].replace(tzinfo=None)
                    finVigencia = campana['campana__finVigencia'].replace(tzinfo=None)
                    if inicioVigencia <= fecha and finVigencia >= fecha:
                        campana['estado'] = 'Vigente'
                    else:
                        campana['estado'] = 'No vigente'

                recursos = RecursoXContacto.objects.filter(contacto__id = contacto['id']).values('recurso__descripcion','recurso__tipo', 'recurso__estado','recurso__inicioVigencia', 'recurso__finVigencia')
                campos_contacto['recursos'] = list(recursos)
                for recurso in campos_contacto['recursos']:
                    recurso['descripcion'] = recurso['recurso__descripcion']
                    if recurso['recurso__tipo'] == "0": recurso['tipo'] = "Correo"
                    elif recurso['recurso__tipo'] == "1": recurso['tipo'] = "Publicación"
                    elif recurso['recurso__tipo'] == "2": recurso['tipo'] = "Página web"
                    fecha = datetime.datetime(fechaHoy.year,fechaHoy.month,fechaHoy.day, 0,0,0)
                    inicioVigencia = recurso['recurso__inicioVigencia'].replace(tzinfo=None)
                    finVigencia = recurso['recurso__finVigencia'].replace(tzinfo=None)
                    if inicioVigencia <= fecha and finVigencia >= fecha:
                        recurso['estado'] = 'Vigente'
                    else:
                        recurso['estado'] = 'No vigente'

                oportunidades = OportunidadXContacto.objects.filter(contacto__id = contacto['id']).values('oportunidad__descripcion','oportunidad__etapa', 'oportunidad__estado','oportunidad__inicioVigencia', 'oportunidad__finVigencia')
                campos_contacto['oportunidades'] = list(oportunidades)
                for oportunidad in campos_contacto['oportunidades']:
                    oportunidad['descripcion'] = oportunidad['oportunidad__descripcion']
                    if oportunidad['oportunidad__etapa'] == "0": oportunidad['etapa'] = "Calificación"
                    elif oportunidad['oportunidad__etapa'] == "1": oportunidad['etapa'] = "Necesidad de análisis"
                    elif oportunidad['oportunidad__etapa'] == "2": oportunidad['etapa'] = "Propuesta"
                    elif oportunidad['oportunidad__etapa'] == "3": oportunidad['etapa'] = "Negociación"
                    elif oportunidad['oportunidad__etapa'] == "4": oportunidad['etapa'] = "Perdida"
                    elif oportunidad['oportunidad__etapa'] == "5": oportunidad['etapa'] = "Ganada"
                    fecha = datetime.datetime(fechaHoy.year,fechaHoy.month,fechaHoy.day, 0,0,0)
                    inicioVigencia = oportunidad['oportunidad__inicioVigencia'].replace(tzinfo=None)
                    finVigencia = oportunidad['oportunidad__finVigencia'].replace(tzinfo=None)
                    if inicioVigencia <= fecha and finVigencia >= fecha:
                        oportunidad['estado'] = 'Vigente'
                    else:
                        oportunidad['estado'] = 'No vigente'

                #actividades = Actividad.objects.filter(contacto__id = contacto['id']).values('tipo','titulo','descripcion','fechaHora')
                empresas = Contacto.objects.filter(id =contacto['id']).values('empresa__id','empresa__nombre','empresa__sector')
                correosNoDisponibles = CuentaCorreo.objects.filter(contacto__id__gte = 1, contacto__propietario__id = contacto['propietario__id']).values('direccion')
                campos_contacto['telefonos'] = list(telefonos)
                campos_contacto['direcciones'] = list(direcciones)
                if correo is not None:
                    campos_contacto['correo'] = {"servicio": correo['servicio'], "direccion": correo['direccion']}
                campos_contacto['redes'] = list(redes)
                #campos_contacto['actividades'] = list(actividades)
                campos_contacto['empresas'] = list(empresas)
                campos_contacto['correosNoDisponibles'] = [d['direccion'] for d in correosNoDisponibles]
                if correo is not None:
                    if correo['direccion'] in campos_contacto['correosNoDisponibles']: campos_contacto['correosNoDisponibles'].remove(correo['direccion'])
                for empresa in campos_contacto['empresas']:
                    empresa['empresa'] = empresa['empresa__id']
                    empresa['nombre'] = empresa['empresa__nombre']
                    empresa['sector'] = empresa['empresa__sector']
                    empresa['telefono'] = "-"
                    telefonosEmpresa = Telefono.objects.filter(empresa__id =empresa['empresa__id']).values()
                    #print(telefonosEmpresa)
                    if telefonosEmpresa.count()>0:
                        empresa['telefono'] = telefonosEmpresa[0]['numero']
                        for telefono in telefonosEmpresa:
                            if telefono['principal'] == True: #ver si esta bien el if
                                empresa['telefono'] = telefono['numero']
                    del empresa['empresa__id']
                    del empresa['empresa__nombre']
                    del empresa['empresa__sector']
                return Response(campos_contacto, status = status.HTTP_200_OK)
            else:
                return Response('No se ha encontrado al contacto', status = status.HTTP_200_OK)
        return Response('No se ha encontrado al contacto', status = status.HTTP_200_OK)

class RegistrarContacto(APIView):
    def post(self, request,id=0):
        propietarioId = request.data["propietario"]
        fechaActual = datetime.datetime.now()
        try:
            if request.data["idContacto"] is not None and request.data["idContacto"]>0:
                idContacto = request.data["idContacto"]
                persona = Contacto.objects.filter(id=idContacto).values("persona__id").first()
                idPersona = persona['persona__id']
                Telefono.objects.filter(Q(contacto__id = idContacto)).delete()
                Direccion.objects.filter(Q(contacto__id = idContacto)).delete()
                CuentaCorreo.objects.filter(Q(contacto__id = idContacto)).delete()
                CuentaRedSocial.objects.filter(Q(contacto__id = idContacto)).delete()
                #Actividad.objects.filter(Q(contacto__id = idContacto)).delete()
                #ContactoXEmpresa.objects.filter(Q(contacto__id = idContacto)).delete()
                telefonos = request.data["telefonos"]
                for telefono in telefonos:
                    campos = {'numero': telefono['numero'],
                            'principal': telefono['principal'],
                            'contacto': idContacto
                            }
                    telefono_serializer = TelefonoSerializer(data = campos)
                    if telefono_serializer.is_valid():
                        telefono_serializer.save()
                direcciones = request.data["direcciones"]
                for direccion in direcciones:
                    campos = {'pais': direccion['pais'],
                    'estado': direccion['estado'],
                    'ciudad': direccion['ciudad'],
                    'direccion': direccion['direccion'],
                            'principal': direccion['principal'],
                            'contacto': idContacto
                            }
                    direccion_serializer = DireccionSerializer(data = campos)
                    if direccion_serializer.is_valid():
                        direccion_serializer.save()
                correo = request.data["correo"]
                if correo != {}:
                    campos = {'servicio': "",
                                'direccion': correo['direccion'],
                                'contacto': idContacto
                                }
                    if "@gmail" in correo['direccion']:
                        campos['servicio'] = "0"
                    elif "@hotmail" in correo['direccion'] or "@outlook" in correo['direccion']:
                        campos['servicio'] = "1"
                    correo_serializer = CuentaCorreoSerializer(data = campos)
                    if correo_serializer.is_valid():
                        correo_serializer.save()
                redes = request.data["redes"]
                for red in redes:
                    campos = {'redSocial': red['redSocial'],
                            'nombreUsuario': red['nombreUsuario'],
                            'contacto': idContacto
                            }
                    red_serializer = CuentaRedSocialSerializer(data = campos)
                    if red_serializer.is_valid():
                        red_serializer.save()
                empresas = request.data["empresas"]
                contacto = Contacto.objects.filter(id=idContacto).first()
                campos_contacto = {
                    'calificado': request.data["calificado"],
                    'estado': request.data["estado"],
                    'propietario': request.data["propietario"],
                        'fechaModificacion': fechaActual
                }
                if request.data["calificado"] == True:
                    campos_contacto['fechaConversion'] = fechaActual
                if empresas!=[]:
                    campos_contacto['empresa'] = empresas[0]['empresa']
                contacto_serializer = ContactoSerializer(contacto, data=campos_contacto)
                if contacto_serializer.is_valid():
                    contacto_serializer.save()
                persona = Persona.objects.filter(id=idPersona).first()
                campos_persona = {
                    'nombreCompleto': request.data["nombreCompleto"],
                        'fechaModificacion': fechaActual
                }
                persona_serializer = PersonaSerializer(persona, data=campos_persona)
                if persona_serializer.is_valid():
                    persona_serializer.save()
                campos_log = {'tipo': "0",
                                'fuente': "Sección Contactos",
                                'descripcion': "Modificación de contacto: " + request.data["nombreCompleto"],
                                'propietario': propietarioId,
                                'fechaHora': fechaActual
                                }
                log_serializer = LogSerializer(data = campos_log)
                if log_serializer.is_valid():
                    log_serializer.save()
            else:
                campos_persona = {
                    'nombreCompleto': request.data["nombreCompleto"],
                    'fechaCreacion': fechaActual,
                        'fechaModificacion': fechaActual
                }
                persona_serializer = PersonaSerializer(data=campos_persona)
                idPersona = 0
                if persona_serializer.is_valid():
                    idPersona = persona_serializer.save()
                    idPersona = idPersona.id
                empresas = request.data["empresas"]
                campos_contacto = {
                    'persona': idPersona,
                    'calificado': request.data["calificado"],
                    'estado': request.data["estado"],
                    'propietario': request.data["propietario"],
                    'fechaCreacion': fechaActual,
                        'fechaModificacion': fechaActual
                }
                if empresas!=[]:
                    #print('tiene empresas')
                    campos_contacto['empresa'] = empresas[0]['empresa']
                #print(campos_contacto)
                contacto_serializer = ContactoSerializer(data=campos_contacto)
                idContacto = 0
                if contacto_serializer.is_valid():
                    idContacto = contacto_serializer.save()
                    idContacto = idContacto.id
                telefonos = request.data["telefonos"]
                for telefono in telefonos:
                    campos = {'numero': telefono['numero'],
                            'principal': telefono['principal'],
                            'contacto': idContacto
                            }
                    telefono_serializer = TelefonoSerializer(data = campos)
                    if telefono_serializer.is_valid():
                        telefono_serializer.save()
                direcciones = request.data["direcciones"]
                for direccion in direcciones:
                    campos = {'pais': direccion['pais'],
                    'estado': direccion['estado'],
                    'ciudad': direccion['ciudad'],
                    'direccion': direccion['direccion'],
                            'principal': direccion['principal'],
                            'contacto': idContacto
                            }
                    direccion_serializer = DireccionSerializer(data = campos)
                    if direccion_serializer.is_valid():
                        direccion_serializer.save()
                correo = request.data["correo"]
                if correo != {}:
                    campos = {'servicio': "",
                                'direccion': correo['direccion'],
                                'contacto': idContacto
                                }
                    if "@gmail" in correo['direccion']:
                        campos['servicio'] = "0"
                    elif "@hotmail" in correo['direccion'] or "@outlook" in correo['direccion']:
                        campos['servicio'] = "1"
                    correo_serializer = CuentaCorreoSerializer(data = campos)
                    if correo_serializer.is_valid():
                        correo_serializer.save()
                redes = request.data["redes"]
                for red in redes:
                    campos = {'redSocial': red['redSocial'],
                            'nombreUsuario': red['nombreUsuario'],
                            'contacto': idContacto
                            }
                    red_serializer = CuentaRedSocialSerializer(data = campos)
                    if red_serializer.is_valid():
                        red_serializer.save()
                campos_log = {'tipo': "0",
                                'fuente': "Sección Contactos",
                                'descripcion': "Creación de contacto: " + request.data["nombreCompleto"],
                                'propietario': propietarioId,
                                'fechaHora': fechaActual
                                }
                log_serializer = LogSerializer(data = campos_log)
                if log_serializer.is_valid():
                    log_serializer.save()
            return Response(status=status.HTTP_200_OK,
                            data={
                                'message': 'Contacto registrado correctamente',
                            },)	
        except Exception as e:
            #guardar error con propietarioId
            campos_log = {'tipo': "1",
                        'fuente': "Sección Contactos",
                        'codigo': "RCR001",
                        'descripcion': "Error en registro de contacto",
                        'propietario': propietarioId,
                        'fechaHora': fechaActual
                        }
            log_serializer = LogSerializer(data = campos_log)
            if log_serializer.is_valid():
                log_serializer.save()
            return Response(status=status.HTTP_200_OK,
                            data={
                                'message': 'Error en registro de contacto',
                            },)	

class FiltrarContactos(APIView):
    def post(self, request,id=0):
        cadena = request.data["cadena"]
        estado = request.data["estado"]
        fechaCreacionIni = request.data["fechaCreacionIni"]
        fechaCreacionFin = request.data["fechaCreacionFin"]
        fechaModificacionIni = request.data["fechaModificacionIni"]
        fechaModificacionFin = request.data["fechaModificacionFin"]
        idPropietario = int(request.data["propietario"])
        query = Q()
        subquery1 = Q()
        subquery3 = Q()
        subquery4 = Q()

        telefonos = Telefono.objects.filter(numero__contains = cadena).values('contacto__id')
        contactosTelefono = [telefono['contacto__id'] for telefono in list(telefonos)]
        correos = CuentaCorreo.objects.filter(direccion__contains = cadena).values('contacto__id')
        contactosCorreo = [correo['contacto__id'] for correo in list(correos)]
        query.add(Q(propietario__id=idPropietario), Q.AND)

        if (cadena != ""):
            subquery1.add(Q(persona__nombreCompleto__contains=cadena), Q.OR)
            subquery3.add(Q(id__in=contactosTelefono), Q.OR)
            subquery4.add(Q(id__in=contactosCorreo), Q.OR)
        if(estado != "" and estado in ['0','1','2','3']):
            query.add(Q(estado=estado), Q.AND)
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
        
        contactos = Contacto.objects.filter((subquery1 | subquery3 | subquery4) & query).values('id', 'persona__id', 'persona__nombreCompleto', 'estado','fechaCreacion', 'fechaModificacion','empresa__nombre')
        listaContactos = list(contactos)
        for contacto in listaContactos:
            print(contacto['fechaCreacion'])
            contacto['fechaCreacion'] = datetime.datetime.strftime(contacto['fechaCreacion'], '%d-%m-%Y')
            contacto['fechaModificacion'] = datetime.datetime.strftime(contacto['fechaModificacion'], '%d-%m-%Y')
            if contacto['estado'] == '0':
                contacto['estado'] = 'Suscriptor'
            elif contacto['estado'] == '1':
                contacto['estado'] = 'Lead'
            elif contacto['estado'] == '2':
                contacto['estado'] = 'Oportunidad'
            elif contacto['estado'] == '3':
                contacto['estado'] = 'Cliente'
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
            if contacto['empresa__nombre'] is None:
                contacto['empresa'] = "-"
            else:
                contacto['empresa'] = contacto['empresa__nombre']
            del contacto['empresa__nombre']
        #poner el formato para mostrar contactos
        return Response(listaContactos, status = status.HTTP_200_OK)
    
class BuscarDetalleEmpresa(APIView):
    def get(self, request,id):
        if id is not None and id > 0:
            empresa = Empresa.objects.filter(id=id).values('id','nombre','sector','cantEmpleados','tipo','propietario__id').first()
            #print(empresa)
            if empresa is not None:
                campos_empresas = {
                    "idEmpresa": empresa['id'],
                    "nombre": empresa['nombre'],
                    "sector": empresa['sector'],
                    "cantEmpleados": empresa['cantEmpleados'],
                    "tipo": empresa['tipo'],
                    "propietario": empresa['propietario__id'],
                    "empresasNoDisponibles": [],
                    "telefonos": [],
                    "direcciones": [],
                    #"correos": [],
                    #"redes": [],
                    #"actividades": [],
                    "contactos": []
                }
                telefonos = Telefono.objects.filter(empresa__id = empresa['id']).values('numero','principal')
                direcciones = Direccion.objects.filter(empresa__id = empresa['id']).values('pais','estado','ciudad','direccion','principal')
                #correos = CuentaCorreo.objects.filter(empresa__id = empresa['id']).values('servicio','direccion')
                #redes = CuentaRedSocial.objects.filter(empresa__id = empresa['id']).values('redSocial','nombreUsuario')
                #actividades = Actividad.objects.filter(empresa__id = empresa['id']).values('tipo','titulo','descripcion','fechaHora')
                contactos = Contacto.objects.filter(empresa__id =empresa['id']).values('id','persona__nombreCompleto')
                empresasNoDisponibles = Empresa.objects.filter(propietario__id = empresa['propietario__id']).values('nombre')
                campos_empresas['telefonos'] = list(telefonos)
                campos_empresas['direcciones'] = list(direcciones)
                #campos_empresas['correos'] = list(correos)
                #campos_empresas['redes'] = list(redes)
                #campos_empresas['actividades'] = list(actividades)
                campos_empresas['contactos'] = list(contactos)
                campos_empresas['empresasNoDisponibles'] = [d['nombre'] for d in empresasNoDisponibles]
                if empresa['nombre'] in campos_empresas['empresasNoDisponibles']: campos_empresas['empresasNoDisponibles'].remove(empresa['nombre'])
                # for actividad in campos_empresas['actividades']:
                #     fecha = str(actividad['fechaHora'].date().day) + "-" + str(actividad['fechaHora'].date().month) + "-" + str(actividad['fechaHora'].date().year)
                #     hora = str(actividad['fechaHora'].time().hour)
                #     minuto = str(actividad['fechaHora'].time().minute)
                #     actividad['fecha'] = fecha
                #     actividad['hora'] = hora
                #     actividad['minuto'] = minuto
                #     del actividad['fechaHora']
                for contacto in campos_empresas['contactos']:
                    contacto['contacto'] = contacto['id']
                    contacto['nombreCompleto'] = contacto['persona__nombreCompleto']
                    contacto['correo'] = "-"
                    contacto['telefono'] = "-"
                    telefonosContacto = Telefono.objects.filter(contacto__id =contacto['id']).values()
                    #print(telefonosContacto)
                    if telefonosContacto.count()>0:
                        contacto['telefono'] = telefonosContacto[0]['numero']
                        for telefono in telefonosContacto:
                            if telefono['principal'] == True: #ver si esta bien el if
                                contacto['telefono'] = telefono['numero']
                    correoContacto = CuentaCorreo.objects.filter(contacto__id =contacto['id']).values().first()
                    if correoContacto is not None:
                        contacto['correo'] = correoContacto['direccion']
                    del contacto['id']
                    del contacto['persona__nombreCompleto']
                return Response(campos_empresas, status = status.HTTP_200_OK)
            else:
                return Response('No se ha encontrado a la empresa', status = status.HTTP_200_OK)
        return Response('No se ha encontrado a la empresa', status = status.HTTP_200_OK)

class RegistrarEmpresa(APIView):
    def post(self, request,id=0):
        propietarioId = request.data["propietario"]
        fechaActual = datetime.datetime.now()
        try:
            if request.data["idEmpresa"] is not None and request.data["idEmpresa"]>0:
                idEmpresa = request.data["idEmpresa"]
                Telefono.objects.filter(Q(empresa__id = idEmpresa)).delete()
                Direccion.objects.filter(Q(empresa__id = idEmpresa)).delete()
                #CuentaCorreo.objects.filter(Q(empresa__id = idEmpresa)).delete()
                #CuentaRedSocial.objects.filter(Q(empresa__id = idEmpresa)).delete()
                #Actividad.objects.filter(Q(empresa__id = idEmpresa)).delete()
                #ContactoXEmpresa.objects.filter(Q(empresa__id = idEmpresa)).delete()
                telefonos = request.data["telefonos"]
                for telefono in telefonos:
                    campos = {'numero': telefono['numero'],
                            'principal': telefono['principal'],
                            'empresa': idEmpresa
                            }
                    telefono_serializer = TelefonoSerializer(data = campos)
                    if telefono_serializer.is_valid():
                        telefono_serializer.save()
                direcciones = request.data["direcciones"]
                for direccion in direcciones:
                    campos = {'pais': direccion['pais'],
                    'estado': direccion['estado'],
                    'ciudad': direccion['ciudad'],
                    'direccion': direccion['direccion'],
                            'principal': direccion['principal'],
                            'empresa': idEmpresa
                            }
                    direccion_serializer = DireccionSerializer(data = campos)
                    if direccion_serializer.is_valid():
                        direccion_serializer.save()
                # correos = request.data["correos"]
                # for correo in correos:
                #     campos = {'servicio': correo['servicio'],
                #               'direccion': correo['direccion'],
                #             'empresa': idEmpresa
                #             }
                #     correo_serializer = CuentaCorreoSerializer(data = campos)
                #     if correo_serializer.is_valid():
                #         correo_serializer.save()
                # redes = request.data["redes"]
                # for red in redes:
                #     campos = {'redSocial': red['redSocial'],
                #               'nombreUsuario': red['nombreUsuario'],
                #             'empresa': idEmpresa
                #             }
                #     red_serializer = CuentaRedSocialSerializer(data = campos)
                #     if red_serializer.is_valid():
                #         red_serializer.save()
                contactos = request.data["contactos"]
                for contacto in contactos:
                    contactoEnBD = Contacto.objects.filter(id=contacto['contacto']).first()
                    campos_contacto = {
                        'empresa': idEmpresa
                    }
                    contacto_serializer = ContactoSerializer(contactoEnBD, data=campos_contacto)
                    if contacto_serializer.is_valid():
                        contacto_serializer.save()
                    # campos = {'contacto': contacto['contacto'],
                    #         'empresa': idEmpresa
                    #         }
                    # contacto_empresa_serializer = ContactoXEmpresaSerializer(data = campos)
                    # if contacto_empresa_serializer.is_valid():
                    #     contacto_empresa_serializer.save()
                # actividades = request.data["actividades"]
                # for actividad in actividades:
                #     fecha  = datetime.datetime.strptime(actividad['fecha'], '%d-%m-%Y').date()
                #     campos = {'tipo': actividad['tipo'],
                #               'titulo': actividad['titulo'],
                #               'descripcion': actividad['descripcion'],
                #               'fechaHora': datetime.datetime(fecha.year,fecha.month,fecha.day, actividad['hora'],actividad['minuto'],0),
                #             'empresa': idEmpresa
                #             }
                #     actividad_serializer = ActividadSerializer(data = campos)
                #     if actividad_serializer.is_valid():
                #         actividad_serializer.save()
                empresa = Empresa.objects.filter(id=idEmpresa).first()
                campos_empresa = {
                    'nombre': request.data["nombre"],
                    'sector': request.data["sector"],
                    'cantEmpleados': request.data["cantEmpleados"],
                    'tipo': request.data["tipo"],
                    'propietario': request.data["propietario"],
                        'fechaModificacion': fechaActual
                }
                empresa_serializer = EmpresaSerializer(empresa, data=campos_empresa)
                if empresa_serializer.is_valid():
                    empresa_serializer.save()
                campos_log = {'tipo': "0",
                                'fuente': "Sección Empresas",
                                'descripcion': "Modificación de empresa: " + request.data["nombre"],
                                'propietario': propietarioId,
                                'fechaHora': fechaActual
                                }
                log_serializer = LogSerializer(data = campos_log)
                if log_serializer.is_valid():
                    log_serializer.save()
            else:
                campos_empresa = {
                    'nombre': request.data["nombre"],
                    'sector': request.data["sector"],
                    'cantEmpleados': request.data["cantEmpleados"],
                    'tipo': request.data["tipo"],
                    'propietario': request.data["propietario"],
                    'fechaCreacion': fechaActual,
                        'fechaModificacion': fechaActual
                }
                empresa_serializer = EmpresaSerializer(data=campos_empresa)
                idEmpresa = 0
                if empresa_serializer.is_valid():
                    idEmpresa = empresa_serializer.save()
                    idEmpresa = idEmpresa.id
                telefonos = request.data["telefonos"]
                for telefono in telefonos:
                    campos = {'numero': telefono['numero'],
                            'principal': telefono['principal'],
                            'empresa': idEmpresa
                            }
                    telefono_serializer = TelefonoSerializer(data = campos)
                    if telefono_serializer.is_valid():
                        telefono_serializer.save()
                direcciones = request.data["direcciones"]
                for direccion in direcciones:
                    campos = {'pais': direccion['pais'],
                    'estado': direccion['estado'],
                    'ciudad': direccion['ciudad'],
                    'direccion': direccion['direccion'],
                            'principal': direccion['principal'],
                            'empresa': idEmpresa
                            }
                    direccion_serializer = DireccionSerializer(data = campos)
                    if direccion_serializer.is_valid():
                        direccion_serializer.save()
                # correos = request.data["correos"]
                # for correo in correos:
                #     campos = {'servicio': correo['servicio'],
                #               'direccion': correo['direccion'],
                #             'empresa': idEmpresa
                #             }
                #     correo_serializer = CuentaCorreoSerializer(data = campos)
                #     if correo_serializer.is_valid():
                #         correo_serializer.save()
                # redes = request.data["redes"]
                # for red in redes:
                #     campos = {'redSocial': red['redSocial'],
                #               'nombreUsuario': red['nombreUsuario'],
                #             'empresa': idEmpresa
                #             }
                #     red_serializer = CuentaRedSocialSerializer(data = campos)
                #     if red_serializer.is_valid():
                #         red_serializer.save()
                contactos = request.data["contactos"]
                for contacto in contactos:
                    contactoEnBD = Contacto.objects.filter(id=contacto['contacto']).first()
                    campos_contacto = {
                        'empresa': idEmpresa
                    }
                    contacto_serializer = ContactoSerializer(contactoEnBD, data=campos_contacto)
                    if contacto_serializer.is_valid():
                        contacto_serializer.save()
                campos_log = {'tipo': "0",
                                'fuente': "Sección Empresas",
                                'descripcion': "Creación de empresa: " + request.data["nombre"],
                                'propietario': propietarioId,
                                'fechaHora': fechaActual
                                }
                log_serializer = LogSerializer(data = campos_log)
                if log_serializer.is_valid():
                    log_serializer.save()
                # contactos = request.data["contactos"]
                # for contacto in contactos:
                #     campos = {'contacto': contacto['contacto'],
                #             'empresa': idEmpresa
                #             }
                #     contacto_empresa_serializer = ContactoXEmpresaSerializer(data = campos)
                #     if contacto_empresa_serializer.is_valid():
                #         contacto_empresa_serializer.save()
            return Response(status=status.HTTP_200_OK,
                            data={
                                'message': 'Empresa registrada correctamente',
                            },)	
        except Exception as e:
            #guardar error con propietarioId
            campos_log = {'tipo': "1",
                        'fuente': "Sección Empresas",
                        'codigo': "RER001",
                        'descripcion': "Error en registro de empresa",
                        'propietario': propietarioId,
                        'fechaHora': fechaActual
                        }
            log_serializer = LogSerializer(data = campos_log)
            if log_serializer.is_valid():
                log_serializer.save()
            return Response(status=status.HTTP_200_OK,
                            data={
                                'message': 'Error en registro de empresa',
                            },)	

class FiltrarEmpresas(APIView):
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
        subquery2 = Q()
        subquery3 = Q()

        telefonos = Telefono.objects.filter(numero__contains = cadena).values('empresa__id')
        empresasTelefono = [telefono['empresa__id'] for telefono in list(telefonos)]

        query.add(Q(propietario__id=idPropietario), Q.AND)
        if (cadena != ""):
            subquery1.add(Q(nombre__contains=cadena), Q.OR)
            subquery2.add(Q(sector__contains=cadena), Q.OR)
            subquery3.add(Q(id__in=empresasTelefono), Q.OR)
        if(tipo != "" and tipo in ['0','1','2','3']):
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
        
        empresas = Empresa.objects.filter((subquery1 | subquery2 | subquery3) & query).values('id', 'nombre', 'sector', 'tipo','fechaCreacion', 'fechaModificacion')
        listaEmpresas = list(empresas)
        for empresa in listaEmpresas:
            empresa['fechaCreacion'] = datetime.datetime.strftime(empresa['fechaCreacion'], '%d-%m-%Y')
            empresa['fechaModificacion'] = datetime.datetime.strftime(empresa['fechaModificacion'], '%d-%m-%Y')            
            if empresa['tipo'] == '0':
                empresa['tipo'] = 'Cliente potencial'
            elif empresa['tipo'] == '1':
                empresa['tipo'] = 'Socio'
            elif empresa['tipo'] == '2':
                empresa['tipo'] = 'Revendedor'
            elif empresa['tipo'] == '3':
                empresa['tipo'] = 'Proveedor'
            telefonosEmpresa = Telefono.objects.filter(empresa__id =empresa['id']).values()
            if telefonosEmpresa.count()>0:
                empresa['telefono'] = telefonosEmpresa[0]['numero']
                for telefono in telefonosEmpresa:
                    if telefono['principal'] == True: #ver si esta bien el if
                        empresa['telefono'] = telefono['numero']
            else:
                empresa['telefono'] = '-'

        #poner el formato para mostrar contactos
        return Response(listaEmpresas, status = status.HTTP_200_OK)

class EliminarContacto(APIView):
    def delete(self, request,id=0):
        if id != "" and id > 0:
            fechaActual = datetime.datetime.now()
            contacto = Contacto.objects.filter(id=id).values("persona__id","persona__nombreCompleto","propietario__id").first()
            if contacto is not None:
                propietarioId = contacto['propietario__id']
                nombre = contacto['persona__nombreCompleto']
                idPersona = contacto['persona__id']
                try:
                    Telefono.objects.filter(Q(contacto__id = id)).delete()
                    Direccion.objects.filter(Q(contacto__id = id)).delete()
                    CuentaCorreo.objects.filter(Q(contacto__id = id)).delete()
                    CuentaRedSocial.objects.filter(Q(contacto__id = id)).delete()
                    CampanaXContacto.objects.filter(Q(contacto__id = id)).delete()
                    RecursoXContacto.objects.filter(Q(contacto__id = id)).delete()
                    OportunidadXContacto.objects.filter(Q(contacto__id = id)).delete()
                    Contacto.objects.filter(id=id).delete()
                    Persona.objects.filter(id=idPersona).delete()
                    campos_log = {'tipo': "0",
                                    'fuente': "Sección Contactos",
                                    'descripcion': "Eliminación de contacto: " + nombre,
                                    'propietario': propietarioId,
                                    'fechaHora': fechaActual
                                    }
                    log_serializer = LogSerializer(data = campos_log)
                    if log_serializer.is_valid():
                        log_serializer.save()
                    return Response('Contacto eliminado',status=status.HTTP_200_OK)
                except Exception as e:
                    #guardar error con propietarioId
                    campos_log = {'tipo': "1",
                                'fuente': "Sección Contactos",
                                'codigo': "RCE001",
                                'descripcion': "Error en eliminación de contacto",
                                'propietario': propietarioId,
                                'fechaHora': fechaActual
                                }
                    log_serializer = LogSerializer(data = campos_log)
                    if log_serializer.is_valid():
                        log_serializer.save()
                    return Response(status=status.HTTP_200_OK,
                                    data={
                                        'message': 'Error en eliminación de contacto',
                                    },)
        return Response('Contacto no encontrado',status=status.HTTP_200_OK)
    
class EliminarEmpresa(APIView):
    def delete(self, request,id=0):
        if id != "" and id > 0:
            fechaActual = datetime.datetime.now()
            empresa = Empresa.objects.filter(id=id).values("nombre","propietario__id").first()
            if empresa is not None:
                propietarioId = empresa['propietario__id']
                nombre = empresa['nombre']
                try:
                    Telefono.objects.filter(Q(empresa__id = id)).delete()
                    Direccion.objects.filter(Q(empresa__id = id)).delete()
                    Empresa.objects.filter(id=id).delete()
                    campos_log = {'tipo': "0",
                                    'fuente': "Sección Empresas",
                                    'descripcion': "Eliminación de empresa: " + nombre,
                                    'propietario': propietarioId,
                                    'fechaHora': fechaActual
                                    }
                    log_serializer = LogSerializer(data = campos_log)
                    if log_serializer.is_valid():
                        log_serializer.save()
                    return Response('Empresa eliminada',status=status.HTTP_200_OK)
                except Exception as e:
                    #guardar error con propietarioId
                    campos_log = {'tipo': "1",
                                'fuente': "Sección Empresas",
                                'codigo': "REE001",
                                'descripcion': "Error en eliminación de empresa",
                                'propietario': propietarioId,
                                'fechaHora': fechaActual
                                }
                    log_serializer = LogSerializer(data = campos_log)
                    if log_serializer.is_valid():
                        log_serializer.save()
                    return Response(status=status.HTTP_200_OK,
                                    data={
                                        'message': 'Error en eliminación de empresa',
                                    },)
        return Response('Empresa no encontrada',status=status.HTTP_200_OK)

class CargarContactos(APIView):
    def post(self, request,id=0):
        propietarioId = request.data["propietario"]
        fechaActual = datetime.datetime.now()
        try:
            if request.data["campos"] is not None and request.data["campos"]!=[]:
                contactos = []
                for dato in request.data["datos"]:
                    contacto = {"nombreCompleto": "","estado": "0","correo": {}, "redes": [], "telefonos": [], "direcciones": [], "empresa": {}}
                    for campo in request.data["campos"]:
                        if(campo=="Nombre completo"):
                            contacto['nombreCompleto'] = dato[campo]
                        elif(campo=="Estado"):
                            if(dato[campo]=="Suscriptor"): contacto['estado'] = "0"
                            elif(dato[campo]=="Lead"): contacto['estado'] = "1"
                            elif(dato[campo]=="Oportunidad"): contacto['estado'] = "2"
                            elif(dato[campo]=="Cliente"): contacto['estado'] = "3"
                        elif(campo=="Correo"):
                            correo = str(dato[campo])
                            servicio = ""
                            direccion = ""
                            if ":" in correo:
                                servicioCorreo = correo.split(":")
                                if(servicioCorreo[0]=="Google"): servicio = "0"
                                elif(servicioCorreo[0]=="Microsoft"): servicio = "1"
                                direccion = servicioCorreo[1]
                            elif "@gmail" in correo:
                                servicio = "0"
                                direccion = correo
                            elif "@hotmail" in correo or "@outlook" in correo:
                                servicio = "1"
                                direccion = correo
                            else:
                                direccion = correo
                            contacto['correo']={"servicio": servicio,"direccion": direccion}
                        elif(campo=="Direcciones"):
                            direcciones = str(dato[campo]).split(",")
                            for direccionElemento in direcciones:
                                principal = False
                                direccion = ""
                                if ":" in direccionElemento:
                                    direccionPrincipal = direccionElemento.split(":")
                                    if(direccionPrincipal[0]=="Principal" or direccionPrincipal[0]=="principal"): principal = True
                                    direccion = direccionPrincipal[1]
                                else:
                                    direccion = direccionElemento
                                contacto['direcciones'].append({"direccion": direccion,"principal": principal})
                        elif(campo=="Telefonos"):
                            telefonos = str(dato[campo]).split(",")
                            for telefono in telefonos:
                                principal = False
                                numero = ""
                                if ":" in telefono:
                                    direccionPrincipal = telefono.split(":")
                                    if(direccionPrincipal[0]=="Principal" or direccionPrincipal[0]=="principal"): principal = True
                                    numero = direccionPrincipal[1]
                                else:
                                    numero = telefono
                                contacto['telefonos'].append({"numero": numero,"principal": principal})
                        elif(campo=="Redes"):
                            redes = str(dato[campo]).split(",")
                            for red in redes:
                                redSocial = ""
                                nombreUsuario = ""
                                if ":" in red:
                                    redUsuario = red.split(":")
                                    if(redUsuario[0]=="Facebook"): redSocial = "0"
                                    elif(redUsuario[0]=="Linkedin"): redSocial = "1"
                                    elif(redUsuario[0]=="Twitter"): redSocial = "2"
                                    elif(redUsuario[0]=="Instagram"): redSocial = "3"
                                    nombreUsuario = redUsuario[1]
                                else:
                                    nombreUsuario = red
                                contacto['redes'].append({"redSocial": redSocial,"nombreUsuario": nombreUsuario})
                        elif(campo=="Empresa"):
                            contacto['empresa'] = {"nombre": str(dato[campo])}
                            # empresas = str(dato[campo]).split(",")
                            # for empresa in empresas:
                            #     contacto['empresa'].append({"nombre": empresa})
                    contactos.append(contacto)
                # for dato in request.data["datos"]:
                #     contacto = {"nombreCompleto": "","estado": "0","correos": [], "redes": [], "telefonos": [], "direcciones": [], "empresas": []}
                #     for campo in request.data["campos"]:
                #         if(campo=="Nombre completo"):
                #             contacto['nombreCompleto'] = dato[campo]
                #         elif(campo=="Estado"):
                #             if(dato[campo]=="Suscriptor"): contacto['estado'] = "0"
                #             elif(dato[campo]=="Lead"): contacto['estado'] = "1"
                #             elif(dato[campo]=="Oportunidad"): contacto['estado'] = "2"
                #             elif(dato[campo]=="Cliente"): contacto['estado'] = "3"
                #         elif(campo=="Correos"):
                #             correos = str(dato[campo]).split(",")
                #             for correo in correos:
                #                 servicio = ""
                #                 direccion = ""
                #                 if ":" in correo:
                #                     servicioCorreo = correo.split(":")
                #                     if(servicioCorreo[0]=="Google"): servicio = "0"
                #                     elif(servicioCorreo[0]=="Microsoft"): servicio = "1"
                #                     direccion = servicioCorreo[1]
                #                 elif "gmail" in correo:
                #                     servicio = "0"
                #                     direccion = correo
                #                 elif "hotmail" in correo:
                #                     servicio = "1"
                #                     direccion = correo
                #                 else:
                #                     direccion = correo
                #                 contacto['correos'].append({"servicio": servicio,"direccion": direccion})
                #         elif(campo=="Direcciones"):
                #             direcciones = str(dato[campo]).split(",")
                #             for direccionElemento in direcciones:
                #                 principal = False
                #                 direccion = ""
                #                 if ":" in direccionElemento:
                #                     direccionPrincipal = direccionElemento.split(":")
                #                     if(direccionPrincipal[0]=="Principal" or direccionPrincipal[0]=="principal"): principal = True
                #                     direccion = direccionPrincipal[1]
                #                 else:
                #                     direccion = direccionElemento
                #                 contacto['direcciones'].append({"direccion": direccion,"principal": principal})
                #         elif(campo=="Telefonos"):
                #             telefonos = str(dato[campo]).split(",")
                #             for telefono in telefonos:
                #                 principal = False
                #                 numero = ""
                #                 if ":" in telefono:
                #                     direccionPrincipal = telefono.split(":")
                #                     if(direccionPrincipal[0]=="Principal" or direccionPrincipal[0]=="principal"): principal = True
                #                     numero = direccionPrincipal[1]
                #                 else:
                #                     numero = telefono
                #                 contacto['telefonos'].append({"numero": numero,"principal": principal})
                #         elif(campo=="Redes"):
                #             redes = str(dato[campo]).split(",")
                #             for red in redes:
                #                 redSocial = ""
                #                 nombreUsuario = ""
                #                 if ":" in red:
                #                     redUsuario = red.split(":")
                #                     if(redUsuario[0]=="Facebook"): redSocial = "0"
                #                     elif(redUsuario[0]=="Linkedin"): redSocial = "1"
                #                     elif(redUsuario[0]=="Twitter"): redSocial = "2"
                #                     elif(redUsuario[0]=="Instagram"): redSocial = "3"
                #                     nombreUsuario = redUsuario[1]
                #                 else:
                #                     nombreUsuario = red
                #                 contacto['redes'].append({"redSocial": redSocial,"nombreUsuario": nombreUsuario})
                #         elif(campo=="Empresas"):
                #             empresas = str(dato[campo]).split(",")
                #             for empresa in empresas:
                #                 contacto['empresas'].append({"nombre": empresa})
                #     contactos.append(contacto)
                for contacto in contactos:
                    idEmpresa = 0
                    if contacto["empresa"] != {}:
                        #ContactoXEmpresa.objects.filter(Q(contacto__id = idContacto)).delete()
                        empresaGuardada = Empresa.objects.filter(nombre=contacto["empresa"]["nombre"], propietario__id = request.data["propietario"]).values("id").first()
                        if empresaGuardada is not None:
                            idEmpresa = empresaGuardada['id']
                        else:
                            campos_empresa ={"nombre": contacto["empresa"]["nombre"], "propietario": request.data["propietario"], "tipo": "0", 'fechaCreacion': fechaActual,
                        'fechaModificacion': fechaActual}
                            empresa_serializer = EmpresaSerializer(data=campos_empresa)
                            if empresa_serializer.is_valid():
                                idEmpresa = empresa_serializer.save()
                                idEmpresa = idEmpresa.id
                    correoEnBD = None
                    if contacto["correo"] != {}:
                        correoEnBD = CuentaCorreo.objects.filter(contacto__propietario__id = request.data["propietario"], direccion = contacto["correo"]["direccion"], contacto__id__gte = 1).values("contacto__id","contacto__persona__id").first()
                    idContacto = 0
                    idPersona = 0
                    if correoEnBD is not None:
                        contactoGuardado = Contacto.objects.filter(id=correoEnBD['contacto__id']).first()
                        idContacto = correoEnBD['contacto__id']
                        campos_contacto = {
                                'estado': contacto["estado"],
                        'fechaModificacion': fechaActual
                        }
                        if idEmpresa != 0:
                            campos_contacto['empresa'] = idEmpresa
                        contacto_serializer = ContactoSerializer(contactoGuardado, data=campos_contacto)
                        if contacto_serializer.is_valid():
                            contacto_serializer.save()
                        personaGuardada = Persona.objects.filter(id=correoEnBD['contacto__persona__id']).first()
                        idPersona = correoEnBD['contacto__persona__id']
                        campos_persona = {
                            'nombreCompleto': contacto["nombreCompleto"],
                        'fechaModificacion': fechaActual
                        }
                        persona_serializer = PersonaSerializer(personaGuardada, data=campos_persona)
                        if persona_serializer.is_valid():
                            persona_serializer.save()                        
                    else:
                        campos_persona = {
                            'nombreCompleto': contacto["nombreCompleto"],
                            'fechaCreacion': fechaActual,
                        'fechaModificacion': fechaActual
                        }
                        persona_serializer = PersonaSerializer(data=campos_persona)
                        if persona_serializer.is_valid():
                            idPersona = persona_serializer.save()
                            idPersona = idPersona.id
                        campos_contacto = {
                            'persona': idPersona,
                            'propietario': request.data["propietario"],
                            'estado': contacto["estado"],
                            'fechaCreacion': fechaActual,
                        'fechaModificacion': fechaActual
                        }
                        if idEmpresa != 0:
                            campos_contacto['empresa'] = idEmpresa
                        contacto_serializer = ContactoSerializer(data=campos_contacto)
                        if contacto_serializer.is_valid():
                            idContacto = contacto_serializer.save()
                            idContacto = idContacto.id
                    
                    contactoGuardadoBD = Contacto.objects.filter(id = idContacto).first()
                    telefonos = []
                    for tel in contacto["telefonos"]:
                        nuevoTel = Telefono()
                        nuevoTel.principal = tel['principal']
                        nuevoTel.numero = tel['numero']
                        nuevoTel.contacto = contactoGuardadoBD
                        telefonos.append(nuevoTel)
                    direcciones = []
                    for dir in contacto["direcciones"]:
                        nuevoDir = Direccion()
                        nuevoDir.principal = dir['principal']
                        nuevoDir.direccion = dir['direccion']
                        nuevoDir.contacto = contactoGuardadoBD
                        direcciones.append(nuevoDir)                    
                    redes = []
                    for red in contacto["redes"]:
                        nuevaRed = CuentaRedSocial()
                        nuevaRed.redSocial = red['redSocial']
                        nuevaRed.nombreUsuario = red['nombreUsuario']
                        nuevaRed.contacto = contactoGuardadoBD
                        redes.append(nuevaRed)
                    if telefonos !=[]:
                        Telefono.objects.filter(Q(contacto__id = idContacto)).delete()
                        Telefono.objects.bulk_create(telefonos)
                    if direcciones !=[]:
                        Direccion.objects.filter(Q(contacto__id = idContacto)).delete()
                        Direccion.objects.bulk_create(direcciones)
                    if redes !=[]:
                        CuentaRedSocial.objects.filter(Q(contacto__id = idContacto)).delete()
                        CuentaRedSocial.objects.bulk_create(redes)  
                    if contacto["correo"] != {}:
                        CuentaCorreo.objects.filter(Q(contacto__id = idContacto)).delete()
                        campos = {'servicio': contacto["correo"]['servicio'],
                                'direccion': contacto["correo"]['direccion'],
                                'contacto': idContacto
                                }
                        correo_serializer = CuentaCorreoSerializer(data = campos)
                        if correo_serializer.is_valid():
                            correo_serializer.save()
                campos_log = {'tipo': "0",
                                'fuente': "Sección Contactos",
                                'descripcion': "Carga de contactos",
                                'propietario': propietarioId,
                                'fechaHora': fechaActual
                                }
                log_serializer = LogSerializer(data = campos_log)
                if log_serializer.is_valid():
                    log_serializer.save()
                return Response(status=status.HTTP_200_OK,
                            data={
                                'message': 'Contactos cargados correctamente',
                            },)	
            return Response(status=status.HTTP_200_OK,
                            data={
                                'message': 'Contactos no cargados correctamente',
                            },)	
        except Exception as e:
            #guardar error con propietarioId
            campos_log = {'tipo': "1",
                        'fuente': "Sección Contactos",
                        'codigo': "RCR002",
                        'descripcion': "Error en carga de contactos",
                        'propietario': propietarioId,
                        'fechaHora': fechaActual
                        }
            log_serializer = LogSerializer(data = campos_log)
            if log_serializer.is_valid():
                log_serializer.save()
            return Response(status=status.HTTP_200_OK,
                            data={
                                'message': 'Error en carga de contactos',
                            },)	

class CargarEmpresas(APIView):
    def post(self, request,id=0):
        propietarioId = request.data["propietario"]
        fechaActual = datetime.datetime.now()
        try:
            if request.data["campos"] is not None and request.data["campos"]!=[]:
                empresas = []
                for dato in request.data["datos"]:
                    empresa = {"nombre": "","sector": "","pais": "","ciudad": "","cantEmpleados": 0,"tipo": "0", "telefonos": [], "direcciones": [], "contactos": []}
                    for campo in request.data["campos"]:
                        if(campo=="Nombre"):
                            empresa['nombre'] = dato[campo]
                        elif(campo=="Sector"):
                            empresa['sector'] = dato[campo]
                        elif(campo=="Pais"):
                            empresa['pais'] = dato[campo]
                        elif(campo=="Ciudad"):
                            empresa['ciudad'] = dato[campo]
                        elif(campo=="Cantidad de empleados"):
                            empresa['cantEmpleados'] = int(dato[campo])
                        elif(campo=="Tipo"):
                            if(dato[campo]=="Cliente potencial"): empresa['tipo'] = "0"
                            elif(dato[campo]=="Socio"): empresa['tipo'] = "1"
                            elif(dato[campo]=="Revendedor"): empresa['tipo'] = "2"
                            elif(dato[campo]=="Proveedor"): empresa['tipo'] = "3"
                        # elif(campo=="Correos"):
                        #     correos = str(dato[campo]).split(",")
                        #     for correo in correos:
                        #         servicio = ""
                        #         direccion = ""
                        #         if ":" in correo:
                        #             servicioCorreo = correo.split(":")
                        #             if(servicioCorreo[0]=="Google"): servicio = "0"
                        #             elif(servicioCorreo[0]=="Microsoft"): servicio = "1"
                        #             direccion = servicioCorreo[1]
                        #         elif "gmail" in correo:
                        #             servicio = "0"
                        #             direccion = correo
                        #         elif "hotmail" in correo:
                        #             servicio = "1"
                        #             direccion = correo
                        #         else:
                        #             direccion = correo
                        #         empresa['correos'].append({"servicio": servicio,"direccion": direccion})
                        elif(campo=="Telefonos"):
                            telefonos = str(dato[campo]).split(",")
                            for telefono in telefonos:
                                principal = False
                                numero = ""
                                if ":" in telefono:
                                    telefonoPrincipal = telefono.split(":")
                                    if(telefonoPrincipal[0]=="Principal" or telefonoPrincipal[0]=="principal"): principal = True
                                    numero = telefonoPrincipal[1]
                                else:
                                    numero = telefono
                                empresa['telefonos'].append({"numero": numero,"principal": principal})
                        elif(campo=="Direcciones"):
                            direcciones = str(dato[campo]).split(",")
                            for direccion in direcciones:
                                principal = False
                                detalleDireccion = ""
                                if ":" in direccion:
                                    direccionPrincipal = telefono.split(":")
                                    if(direccionPrincipal[0]=="Principal" or direccionPrincipal[0]=="principal"): principal = True
                                    detalleDireccion = direccionPrincipal[1]
                                else:
                                    detalleDireccion = telefono
                                empresa['direcciones'].append({"direccion": detalleDireccion,"principal": principal})
                        # elif(campo=="Redes"):
                        #     redes = str(dato[campo]).split(",")
                        #     for red in redes:
                        #         redSocial = ""
                        #         nombreUsuario = ""
                        #         if ":" in red:
                        #             redUsuario = red.split(":")
                        #             if(redUsuario[0]=="Facebook"): redSocial = "0"
                        #             elif(redUsuario[0]=="Linkedin"): redSocial = "1"
                        #             elif(redUsuario[0]=="Twitter"): redSocial = "2"
                        #             elif(redUsuario[0]=="Instagram"): redSocial = "3"
                        #             nombreUsuario = redUsuario[1]
                        #         else:
                        #             nombreUsuario = red
                        #         empresa['redes'].append({"redSocial": redSocial,"nombreUsuario": nombreUsuario})
                        elif(campo=="Correos de contacto"):
                            contactos = str(dato[campo]).split(",")
                            for correo in contactos:
                                correo = str(dato[campo])
                                servicio = ""
                                direccion = ""
                                if ":" in correo:
                                    servicioCorreo = correo.split(":")
                                    if(servicioCorreo[0]=="Google"): servicio = "0"
                                    elif(servicioCorreo[0]=="Microsoft"): servicio = "1"
                                    direccion = servicioCorreo[1]
                                elif "@gmail" in correo:
                                    servicio = "0"
                                    direccion = correo
                                elif "@hotmail" in correo or "@outlook" in correo:
                                    servicio = "1"
                                    direccion = correo
                                else:
                                    direccion = correo
                                empresa['contactos'].append({"servicio": servicio,"direccion": direccion})
                    empresas.append(empresa)

                for empresa in empresas:
                    empresaGuardadaValor = Empresa.objects.filter(nombre=empresa['nombre'], propietario__id = request.data["propietario"]).values("id").first()
                    idEmpresa = 0
                    if empresaGuardadaValor is not None:
                        empresaGuardada = Empresa.objects.filter(id=empresaGuardadaValor['id']).first()
                        idEmpresa = empresaGuardadaValor['id']
                        Telefono.objects.filter(Q(empresa__id = idEmpresa)).delete()
                        #CuentaCorreo.objects.filter(Q(empresa__id = idEmpresa)).delete()
                        #CuentaRedSocial.objects.filter(Q(empresa__id = idEmpresa)).delete()
                        #ContactoXEmpresa.objects.filter(Q(empresa__id = idEmpresa)).delete()
                        campos_empresa = {
                            'nombre': empresa["nombre"],
                            'sector': empresa["sector"],
                            'pais': empresa["pais"],
                            'ciudad': empresa["ciudad"],
                            'cantEmpleados': empresa["cantEmpleados"],
                            'tipo': empresa["tipo"],
                            'propietario': request.data["propietario"],
                        'fechaModificacion': fechaActual
                        }
                        empresa_serializer = EmpresaSerializer(empresaGuardada, data=campos_empresa)
                        if empresa_serializer.is_valid():
                            empresa_serializer.save()                      
                    else:
                        campos_empresa = {
                            'nombre': empresa["nombre"],
                            'sector': empresa["sector"],
                            'pais': empresa["pais"],
                            'ciudad': empresa["ciudad"],
                            'cantEmpleados': empresa["cantEmpleados"],
                            'tipo': empresa["tipo"],
                            'propietario': request.data["propietario"],
                            'fechaCreacion': fechaActual,
                        'fechaModificacion': fechaActual
                        }
                        empresa_serializer = EmpresaSerializer(data=campos_empresa)
                        if empresa_serializer.is_valid():
                            idEmpresa = empresa_serializer.save()
                            idEmpresa = idEmpresa.id
                    empresaGuardadaBD = Empresa.objects.filter(id = idEmpresa).first()
                    telefonos = []
                    for tel in empresa["telefonos"]:
                        nuevoTel = Telefono()
                        nuevoTel.principal = tel['principal']
                        nuevoTel.numero = tel['numero']
                        nuevoTel.empresa = empresaGuardadaBD
                        telefonos.append(nuevoTel)
                    direcciones = []
                    for dir in empresa["direcciones"]:
                        nuevaDir = Direccion()
                        nuevaDir.principal = dir['principal']
                        nuevaDir.direccion = dir['direccion']
                        nuevaDir.empresa = empresaGuardadaBD
                        direcciones.append(nuevaDir)
                    # correos = []
                    # for cor in empresa["correos"]:
                    #     nuevoCor = CuentaCorreo()
                    #     nuevoCor.servicio = cor['servicio']
                    #     nuevoCor.direccion = cor['direccion']
                    #     nuevoCor.empresa = empresaGuardadaBD
                    #     correos.append(nuevoCor)
                    # redes = []
                    # for red in empresa["redes"]:
                    #     nuevaRed = CuentaRedSocial()
                    #     nuevaRed.redSocial = red['redSocial']
                    #     nuevaRed.nombreUsuario = red['nombreUsuario']
                    #     nuevaRed.empresa = empresaGuardadaBD
                    #     redes.append(nuevaRed)
                    for con in empresa["contactos"]:
                        correoGuardado = CuentaCorreo.objects.filter(direccion=con['direccion'],contacto__propietario__id = request.data["propietario"]).values("contacto__id","persona__id").first()
                        idPersona = 0
                        idContacto = 0
                        if correoGuardado is not None:
                            idContacto = correoGuardado['contacto__id']
                        else:
                            campos_persona ={"nombreCompleto": "", 'fechaCreacion': fechaActual,
                        'fechaModificacion': fechaActual}
                            persona_serializer = PersonaSerializer(data=campos_persona)
                            if persona_serializer.is_valid():
                                idPersona = persona_serializer.save()
                                idPersona = idPersona.id
                            campos_contacto ={"estado": "0","persona": idPersona ,"propietario": request.data["propietario"], 'fechaCreacion': fechaActual,
                        'fechaModificacion': fechaActual}
                            contacto_serializer = ContactoSerializer(data=campos_contacto)
                            if contacto_serializer.is_valid():
                                idContacto = contacto_serializer.save()
                                idContacto = idContacto.id
                            campos_correo = {"servicio": con['servicio'], "direccion": con['direccion'], "contacto": idContacto}
                            correo_serializer = CuentaCorreoSerializer(data=campos_correo)
                            if correo_serializer.is_valid():
                                correo_serializer.save()
                        contactoGuardadoBD = Contacto.objects.filter(id=idContacto).first()
                        campos_contacto_empresa = {"empresa": idEmpresa}
                        contacto_serializer = ContactoSerializer(contactoGuardadoBD, data=campos_contacto_empresa)
                        if contacto_serializer.is_valid():
                            contacto_serializer.save()
                    if telefonos !=[]:
                        Telefono.objects.bulk_create(telefonos)
                    if direcciones !=[]:
                        Direccion.objects.bulk_create(direcciones)
                    # if correos !=[]:
                    #     CuentaCorreo.objects.bulk_create(correos)
                    # if redes !=[]:
                    #     CuentaRedSocial.objects.bulk_create(redes)
                    #if empresasContacto !=[]:
                    #    ContactoXEmpresa.objects.bulk_create(empresasContacto)                
                campos_log = {'tipo': "0",
                                'fuente': "Sección Empresas",
                                'descripcion': "Carga de empresas",
                                'propietario': propietarioId,
                                'fechaHora': fechaActual
                                }
                log_serializer = LogSerializer(data = campos_log)
                if log_serializer.is_valid():
                    log_serializer.save()
                return Response(status=status.HTTP_200_OK,
                            data={
                                'message': 'Empresas cargadas correctamente',
                            },)	
            return Response(status=status.HTTP_200_OK,
                            data={
                                'message': 'Empresas no cargadas correctamente',
                            },)
        except Exception as e:
            #guardar error con propietarioId
            campos_log = {'tipo': "1",
                        'fuente': "Sección Empresas",
                        'codigo': "RER002",
                        'descripcion': "Error en carga de empresas",
                        'propietario': propietarioId,
                        'fechaHora': fechaActual
                        }
            log_serializer = LogSerializer(data = campos_log)
            if log_serializer.is_valid():
                log_serializer.save()
            return Response(status=status.HTTP_200_OK,
                            data={
                                'message': 'Error en carga de empresas',
                            },)		                    

class FiltrarListas(APIView):
    def post(self, request,id=0):
        cadena = request.data["cadena"]
        objeto = request.data["objeto"]
        tipo = request.data["tipo"]
        fechaCreacionIni = request.data["fechaCreacionIni"]
        fechaCreacionFin = request.data["fechaCreacionFin"]
        fechaModificacionIni = request.data["fechaModificacionIni"]
        fechaModificacionFin = request.data["fechaModificacionFin"]
        idPropietario = int(request.data["propietario"])
        query = Q()

        query.add(Q(propietario__id=idPropietario), Q.AND)

        if (cadena != ""):
            query.add(Q(nombre__contains=cadena), Q.OR)
        if(objeto != "" and objeto in ['0','1']):
            query.add(Q(objeto=objeto), Q.AND)
        if(tipo != "" and tipo in ['0','1']):
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
        
        listas = Lista.objects.filter(query).values('id', 'nombre', 'objeto', 'tipo', 'tamano', 'fechaCreacion', 'fechaModificacion')
        listaListas = list(listas)
        for lista in listaListas:
            lista['fechaCreacion'] = datetime.datetime.strftime(lista['fechaCreacion'], '%d-%m-%Y')
            lista['fechaModificacion'] = datetime.datetime.strftime(lista['fechaModificacion'], '%d-%m-%Y')
            if lista['objeto'] == '0':
                lista['objeto'] = 'Contacto'
            elif lista['objeto'] == '1':
                lista['objeto'] = 'Empresa'
            if lista['tipo'] == '0':
                lista['tipo'] = 'Estática'
            elif lista['tipo'] == '1':
                lista['tipo'] = 'Activa'
        return Response(listaListas, status = status.HTTP_200_OK)
    
class AplicarFiltrosLista(APIView):
    def post(self, request,id=0):
        elementos = []
        idPropietario = int(request.data["propietario"])
        if request.data["filtros"] != []:
            if request.data["objeto"] == "0":
                query = Q()
                query.add(Q(propietario__id=idPropietario), Q.AND)
                #contactos
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
                for contacto in elementos:
                    contacto['fechaCreacion'] = datetime.datetime.strftime(contacto['fechaCreacion'], '%d-%m-%Y')
                    contacto['fechaModificacion'] = datetime.datetime.strftime(contacto['fechaModificacion'], '%d-%m-%Y')
                    if contacto['estado'] == '0':
                        contacto['estado'] = 'Suscriptor'
                    elif contacto['estado'] == '1':
                        contacto['estado'] = 'Lead'
                    elif contacto['estado'] == '2':
                        contacto['estado'] = 'Oportunidad'
                    elif contacto['estado'] == '3':
                        contacto['estado'] = 'Cliente'
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
                    if contacto['empresa__nombre'] is None:
                        contacto['empresa'] = "-"
                    else:
                        contacto['empresa'] = contacto['empresa__nombre']
                    del contacto['empresa__nombre']
            elif request.data["objeto"] == "1":
                query = Q()
                query.add(Q(propietario__id=idPropietario), Q.AND)
                #empresas
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
                for empresa in elementos:
                    empresa['fechaCreacion'] = datetime.datetime.strftime(empresa['fechaCreacion'], '%d-%m-%Y')
                    empresa['fechaModificacion'] = datetime.datetime.strftime(empresa['fechaModificacion'], '%d-%m-%Y')            
                    if empresa['tipo'] == '0':
                        empresa['tipo'] = 'Cliente potencial'
                    elif empresa['tipo'] == '1':
                        empresa['tipo'] = 'Socio'
                    elif empresa['tipo'] == '2':
                        empresa['tipo'] = 'Revendedor'
                    elif empresa['tipo'] == '3':
                        empresa['tipo'] = 'Proveedor'
                    telefonosEmpresa = Telefono.objects.filter(empresa__id =empresa['id']).values()
                    if telefonosEmpresa.count()>0:
                        empresa['telefono'] = telefonosEmpresa[0]['numero']
                        for telefono in telefonosEmpresa:
                            if telefono['principal'] == True: #ver si esta bien el if
                                empresa['telefono'] = telefono['numero']
                    else:
                        empresa['telefono'] = '-'





        return Response(elementos, status = status.HTTP_200_OK)

class RegistrarLista(APIView):
    def post(self, request,id=0):
        propietarioId = request.data["propietario"]
        fechaActual = datetime.datetime.now()
        try:
            if request.data["idLista"] is not None and request.data["idLista"]>0:
                idLista = request.data["idLista"]
                ListaXContacto.objects.filter(Q(lista__id = idLista)).delete()
                ListaXEmpresa.objects.filter(Q(lista__id = idLista)).delete()
                Filtro.objects.filter(Q(lista__id = idLista)).delete()
                objeto = request.data["objeto"]
                if objeto == '0':
                    contactos = request.data["elementos"]
                    for contacto in contactos:
                        campos = {'contacto': contacto['id'],
                                'lista': idLista
                                }
                        contactoxlista_serializer = ListaXContactoSerializer(data = campos)
                        if contactoxlista_serializer.is_valid():
                            contactoxlista_serializer.save()
                elif objeto == '1':
                    empresas = request.data["elementos"]
                    for empresa in empresas:
                        campos = {'empresa': empresa['id'],
                                'lista': idLista
                                }
                        empresaxlista_serializer = ListaXEmpresaSerializer(data = campos)
                        if empresaxlista_serializer.is_valid():
                            empresaxlista_serializer.save()

                filtros = request.data["filtros"]
                for filtro in filtros:
                    campos = {'lista': idLista,
                            'propiedad': filtro['propiedad'], #cambiar esta parte
                            'evaluacion': filtro['evaluacion'],
                            'valorEvaluacion': str(filtro['valorEvaluacion']) ,
                            'nombre': filtro['nombre']
                            }
                    filtro_serializer = FiltroSerializer(data = campos)
                    if filtro_serializer.is_valid():
                        filtro_serializer.save()
                lista = Lista.objects.filter(id=idLista).first()
                campos_lista = {
                    'nombre': request.data["nombre"],
                    'descripcion': request.data["descripcion"],
                    'objeto': objeto,
                    'tipo': request.data["tipo"],
                    'tamano': request.data["tamano"],
                    'propietario': request.data["propietario"],
                        'fechaModificacion': fechaActual
                }
                lista_serializer = ListaSerializer(lista, data=campos_lista)
                if lista_serializer.is_valid():
                    lista_serializer.save()
                campos_log = {'tipo': "0",
                                'fuente': "Sección Listas",
                                'descripcion': "Modificación de lista: " + request.data["nombre"],
                                'propietario': propietarioId,
                                'fechaHora': fechaActual
                                }
                log_serializer = LogSerializer(data = campos_log)
                if log_serializer.is_valid():
                    log_serializer.save()
            else:
                objeto = request.data["objeto"]
                campos_lista = {
                    'nombre': request.data["nombre"],
                    'descripcion': request.data["descripcion"],
                    'objeto': objeto,
                    'tipo': request.data["tipo"],
                    'tamano': request.data["tamano"],
                    'propietario': request.data["propietario"],
                    'fechaCreacion': fechaActual,
                        'fechaModificacion': fechaActual
                }
                lista_serializer = ListaSerializer(data=campos_lista)
                if lista_serializer.is_valid():
                    idLista = lista_serializer.save()
                    idLista = idLista.id
                filtros = request.data["filtros"]
                for filtro in filtros:
                    campos = {'lista': idLista,
                            'propiedad': filtro['propiedad'], #cambiar esta parte
                            'evaluacion': filtro['evaluacion'],
                            'valorEvaluacion': str(filtro['valorEvaluacion']),
                            'nombre': filtro['nombre']
                            }
                    filtro_serializer = FiltroSerializer(data = campos)
                    if filtro_serializer.is_valid():
                        filtro_serializer.save()
                objeto = request.data["objeto"]
                if objeto == '0':
                    contactos = request.data["elementos"]
                    for contacto in contactos:
                        campos = {'contacto': contacto['id'],
                                'lista': idLista
                                }
                        contactoxlista_serializer = ListaXContactoSerializer(data = campos)
                        if contactoxlista_serializer.is_valid():
                            contactoxlista_serializer.save()
                elif objeto == '1':
                    empresas = request.data["elementos"]
                    for empresa in empresas:
                        campos = {'empresa': empresa['id'],
                                'lista': idLista
                                }
                        empresaxlista_serializer = ListaXEmpresaSerializer(data = campos)
                        if empresaxlista_serializer.is_valid():
                            empresaxlista_serializer.save()
                campos_log = {'tipo': "0",
                                'fuente': "Sección Listas",
                                'descripcion': "Creación de lista: " + request.data["nombre"],
                                'propietario': propietarioId,
                                'fechaHora': fechaActual
                                }
                log_serializer = LogSerializer(data = campos_log)
                if log_serializer.is_valid():
                    log_serializer.save()
            return Response(status=status.HTTP_200_OK,
                            data={
                                'message': 'Lista registrada correctamente',
                            },)	
        except Exception as e:
            #guardar error con propietarioId
            campos_log = {'tipo': "1",
                        'fuente': "Sección Listas",
                        'codigo': "RLR001",
                        'descripcion': "Error en registro de lista",
                        'propietario': propietarioId,
                        'fechaHora': fechaActual
                        }
            log_serializer = LogSerializer(data = campos_log)
            if log_serializer.is_valid():
                log_serializer.save()
            return Response(status=status.HTTP_200_OK,
                            data={
                                'message': 'Error en registro de lista',
                            },)	

class BuscarDetalleLista(APIView):
    def get(self, request,id):
        if id != "" and id > 0:
            lista = Lista.objects.filter(id=id).values('id','nombre','descripcion', 'objeto', 'tipo', 'propietario__id').first()
            if lista is not None:
                campos_lista = {
                    "idLista": lista['id'],
                    "objeto": lista['objeto'],
                    "tipo": lista['tipo'],
                    "nombre": lista['nombre'],
                    "descripcion": lista['descripcion'],
                    "propietario": lista['propietario__id'],
                    "filtros": [],
                    "elementos": [],
                }
                if lista['objeto'] == "0":
                    elementos = ListaXContacto.objects.filter(lista__id=lista['id']).values('contacto__id','contacto__estado','contacto__persona__nombreCompleto', 'contacto__empresa__nombre')
                    campos_lista["elementos"] = list(elementos)
                    for contacto in campos_lista["elementos"]:
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
                elif lista['objeto'] == "1":
                    elementos = ListaXEmpresa.objects.filter(lista__id=lista['id']).values('empresa__id','empresa__nombre','empresa__tipo')
                    campos_lista["elementos"] = list(elementos)
                    for empresa in campos_lista["elementos"]:
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
                
                filtros = Filtro.objects.filter(lista__id = lista['id']).values('propiedad','evaluacion','valorEvaluacion','nombre') #faltan values
                campos_lista['filtros'] = list(filtros)

                return Response(campos_lista, status = status.HTTP_200_OK)
            else:
                return Response('No se ha encontrado a la estrategia', status = status.HTTP_200_OK)
        return Response('No se ha encontrado a la estrategia', status = status.HTTP_200_OK)

class EliminarLista(APIView):
    def delete(self, request,id=0):
        if id != "" and id > 0:
            fechaActual = datetime.datetime.now()
            lista = Lista.objects.filter(id=id).values("nombre","propietario__id").first()
            if lista is not None:
                propietarioId = lista['propietario__id']
                nombre = lista['nombre']
                try:
                    Filtro.objects.filter(Q(lista__id = id)).delete()
                    ListaXContacto.objects.filter(Q(lista__id = id)).delete()
                    ListaXEmpresa.objects.filter(Q(lista__id = id)).delete()
                    Lista.objects.filter(id=id).delete()
                    campos_log = {'tipo': "0",
                                    'fuente': "Sección Listas",
                                    'descripcion': "Eliminación de lista: " + nombre,
                                    'propietario': propietarioId,
                                    'fechaHora': fechaActual
                                    }
                    log_serializer = LogSerializer(data = campos_log)
                    if log_serializer.is_valid():
                        log_serializer.save()
                    return Response('Lista eliminada',status=status.HTTP_200_OK)
                except Exception as e:
                    #guardar error con propietarioId
                    campos_log = {'tipo': "1",
                                'fuente': "Sección Listas",
                                'codigo': "RLE001",
                                'descripcion': "Error en eliminación de lista",
                                'propietario': propietarioId,
                                'fechaHora': fechaActual
                                }
                    log_serializer = LogSerializer(data = campos_log)
                    if log_serializer.is_valid():
                        log_serializer.save()
                    return Response(status=status.HTTP_200_OK,
                                    data={
                                        'message': 'Error en eliminación de lista',
                                    },)
        return Response('Lista no encontrada',status=status.HTTP_200_OK)
