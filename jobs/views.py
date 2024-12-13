from django.shortcuts import render
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import requests
from django.core.mail import get_connection, send_mail, EmailMultiAlternatives
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from marketing.models import *
from marketing.serializers import RecursoSerializer
from relaciones.models import CuentaCorreo
from django.db.models import Q

# Create your views here.
def start():
    scheduler = BackgroundScheduler()
    #scheduler.add_job(publicarCorreos, 'interval', minutes=1)
    #scheduler.add_job(publicarRedesSociales, 'interval', minutes=1)
    #scheduler.add_job(calcularIndicadores, 'interval', minutes=1)
    scheduler.start()


def publicarCorreos():
    recursos = Recurso.objects.filter(tipo="0").values('id', 'descripcion','fechaPublicacion','asuntoCorreo','remitenteCorreo','remitenteContrasena','contenidoHTML')
    listaRecursos = list(recursos)
    #print(listaRecursos)
    fechaHoy = datetime.datetime.now().replace(second=0, microsecond=0)
    for recurso in listaRecursos:
        if recurso['fechaPublicacion'] is not None:
            fechaPub = recurso['fechaPublicacion'].replace(tzinfo=None)
            if fechaPub == fechaHoy:
                print("Se envía el correo")
                contactos = RecursoXContacto.objects.filter(recurso__id=recurso['id']).values('id')
                listaContactos = list(contactos)
                correosEnviar = []
                for contacto in listaContactos:
                    cuentaCorreo = CuentaCorreo.objects.filter(contacto__id=contacto['id']).values('direccion').first()
                    if cuentaCorreo is not None:
                        correosEnviar.append(cuentaCorreo['direccion'])
                if correosEnviar != []:
                    host = ""
                    if "@gmail" in recurso['remitenteCorreo']:
                        host = 'smtp.gmail.com'
                    elif "@hotmail" in recurso['remitenteCorreo'] or "@outlook" in recurso['remitenteCorreo']:
                        host = 'smtp-mail.outlook.com' #ver si es o cambio por 'smtp.outlook.com'
                    if host != "" and recurso['remitenteCorreo'] != "" and recurso['remitenteContrasena'] != "" and recurso['remitenteCorreo'] is not None and recurso['remitenteContrasena'] is not None:
                        print("mandar al host")
                        #a
                        my_host = host
                        my_port = 587
                        my_username = recurso['remitenteCorreo']
                        my_password = recurso['remitenteContrasena']
                        my_use_tls = True
                        try:
                            connection = get_connection(host=my_host, 
                                                        port=my_port, 
                                                        username=my_username, 
                                                        password=my_password, 
                                                        use_tls=my_use_tls,
                                                        fail_silently=False)
                            connection.open()
                            plain_message = ""
                            if recurso['contenidoHTML'] is not None and recurso['contenidoHTML'] != "":
                                plain_message = strip_tags(recurso['contenidoHTML'])
                            message = EmailMultiAlternatives(subject=recurso['asuntoCorreo'], 
                                                            body=plain_message,
                                                            from_email=recurso['remitenteCorreo'], #ver si esta bien o poner none
                                                            bcc=correosEnviar, #ver si funciona bien o poner to=
                                                            connection=connection)
                            if recurso['contenidoHTML'] is not None and recurso['contenidoHTML'] != "":
                                message.attach_alternative(recurso['contenidoHTML'], "text/html")
                            message.send()
                            print('Envío de correo correcto')
                            connection.close()
                        except Exception as e:
                            print('Error en envio de correo')	
    #print("I love python {}".format(datetime.datetime.now().replace(second=0, microsecond=0)))

def publicarRedesSociales():
    recursos = Recurso.objects.filter(tipo="1").values('id','servicioRedSocial' ,'descripcion','fechaPublicacion','contenido','tokenRedSocial','paginaIdRedSocial')
    listaRecursos = list(recursos)
    #print(listaRecursos)
    fechaHoy = datetime.datetime.now().replace(second=0, microsecond=0)
    for recurso in listaRecursos:
        if recurso['fechaPublicacion'] is not None:
            fechaPub = recurso['fechaPublicacion'].replace(tzinfo=None)
            if fechaPub == fechaHoy:
                print("Se sube la publicacion")
                if recurso['servicioRedSocial'] == "0" and recurso['tokenRedSocial'] != "" and recurso['tokenRedSocial'] is not None and recurso['paginaIdRedSocial'] != "" and recurso['paginaIdRedSocial'] is not None:
                    #publicacion facebook
                    #import requests
                    user_token = recurso['tokenRedSocial'] #"EAAPwzKF990kBO6HZCeV1m8qow4jIGztv49V2i7bgZA0pcM2bl5zRG2JMAWeBWbvWDvTVl1PECYRZCZAArjFf9O9ZCLN3FRvZAgcnQpBxJtSjSdjkFptJCPJTx8G4GpC2XWito8PiDYRvR3ZCuyiZCHFySZBSUBe2LIKgZAgWZBbRhxhH1pJFupoZAG0jvFHL"#recurso['tokenUsuario']
                    id_pagina = recurso['paginaIdRedSocial'] #"498026353391626" #recurso['idPagina']
                    #multimedia = recurso['multimedia']
                    version = 'v13.0'
                    postId = 0
                    page_access_token = ""
                    #obtener el page_access_token con el user_token y id_pagina
                    urlUser = f"https://graph.facebook.com/{id_pagina}?fields=access_token&access_token={user_token}"
                    #urlUser = f"https://graph.facebook.com/{version}/{id_pagina}"
                    #paramsUser = {
                    #    'access_token': user_token,
                    #}
                    try:
                        #response = requests.post(urlUser, params=paramsUser)
                        response = requests.get(urlUser)
                        result = response.json()
                        print(result)

                        if 'access_token' in result:
                            print(f"Page access token: {result['access_token']}")
                            page_access_token = result['access_token']
                        else:
                            print(f"Error access token: {result}")
                    except requests.exceptions.RequestException as e:
                        print(f"Request error: {e}")

                    # if multimedia == True and page_access_token!="":
                    #     url = f"https://graph.facebook.com/{version}/{id_pagina}/photos"
                    #     params = {
                    #         'access_token': page_access_token,
                    #         'message': recurso['textoRedSocial'],
                    #         'url': photo_url,
                    #     }
                    #     try:
                    #         response = requests.post(url, params=params)
                    #         result = response.json()

                    #         if 'id' in result:
                    #             print(f"Photo posted successfully. Post ID: {result['id']}")
                    #             postId = result['id']
                    #         else:
                    #             print(f"Error posting photo: {result}")

                    #     except requests.exceptions.RequestException as e:
                    #         print(f"Request error: {e}")
                    # else:
                    url = f'https://graph.facebook.com/{id_pagina}/feed'
                    payload = {
                        'message': recurso['contenido'],
                        'access_token': page_access_token
                    }
                    # Make Facebook post on your Page
                    try:
                        response = requests.post(url, data=payload)
                        result = response.json()

                        if 'id' in result:
                            print(f"text posted successfully. Post ID: {result['id']}")
                            postId = result['id']
                        else:
                            print(f"Error posting: {result}")
                    except requests.exceptions.RequestException as e:
                        print(f"Request error: {e}")
                    print(postId)

                    #guardar el postid
                    # if postId!=0:
                    #     #guardarpostid
                    #     recursoGuardado = Recurso.objects.filter(id=recurso['id']).first()
                    #     campos_recurso = {
                    #         'postId': postId
                    #     }
                    #     recurso_serializer = RecursoSerializer(recursoGuardado, data=campos_recurso)
                    #     if recurso_serializer.is_valid():
                    #         recurso_serializer.save()

                    #post_url = 'https://graph.facebook.com/{}/feed'.format(page_id_1)

                    #access_token = '<your_access_token>'
                    #user_id = '<user_id>'

                    #url = f'https://graph.facebook.com/{user_id}?access_token={access_token}'

                    #response = requests.get(url)

                    #print(response.json())


def calcularIndicadores():
    planes = Plan.objects.filter(id__gte=1).values('id','presupuesto','inicioVigencia', 'finVigencia')
    programas = Estrategia.objects.filter(Q(id__gte=1) & Q(tipo="0")).values('id','presupuesto','plan__id','inicioVigencia', 'finVigencia')
    campanasStandAlone = Campana.objects.filter(Q(id__gte=1) & Q(tipo="1")).values('id','presupuesto','plan__id','inicioVigencia', 'finVigencia')
    campanasPrograma = Campana.objects.filter(Q(id__gte=1) & Q(tipo="0")).values('id','presupuesto','estrategia__id','inicioVigencia', 'finVigencia')
    correos = Recurso.objects.filter(Q(id__gte=1) & Q(tipo="0")).values('id','presupuesto','campana__id','inicioVigencia', 'finVigencia')
    publicaciones = Recurso.objects.filter(Q(id__gte=1) & Q(tipo="1")).values('id','presupuesto','campana__id','inicioVigencia', 'finVigencia')
    paginas = Recurso.objects.filter(Q(id__gte=1) & Q(tipo="2")).values('id','presupuesto','campana__id','inicioVigencia', 'finVigencia')

    for plan in planes:
        #calcular todas sus variables
        indicadores = IndicadorAsignado.objects.filter(plan__id=plan['id']).values('id', 'indicador__calculoAutomatico','indicador__formula')
        print("Estos son los indicadores")
        if indicadores.count()>0:
            print("encontro indicadores")
            print(indicadores.count())
            PRES_PLAN = plan['presupuesto']
            TPRO_PLAN = 0
            PPRO_PLAN = 0
            programasDePlan = Estrategia.objects.filter(Q(plan__id=plan['id']) & Q(tipo="0")).values('presupuesto')
            if programasDePlan.count() > 0:
                TPRO_PLAN = programasDePlan.count()
                presupuestos = [programa['presupuesto'] for programa in programasDePlan]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PPRO_PLAN += presupuesto
            TCPS_PLAN = 0
            PCPS_PLAN = 0
            campanasSAPlan = Campana.objects.filter(Q(plan__id=plan['id']) & Q(tipo="1")).values('presupuesto')
            if campanasSAPlan.count() > 0:
                TCPS_PLAN = campanasSAPlan.count()
                presupuestos = [campana['presupuesto'] for campana in campanasSAPlan]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PCPS_PLAN += presupuesto
            TCPP_PLAN = 0
            PCPP_PLAN = 0
            campanasPPlan = Campana.objects.filter(Q(estrategia__plan__id=plan['id']) & Q(tipo="0")).values('presupuesto')
            if campanasPPlan.count() > 0:
                TCPP_PLAN = campanasPPlan.count()
                presupuestos = [campana['presupuesto'] for campana in campanasPPlan]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PCPP_PLAN += presupuesto

            TCOR_PLAN = 0
            PCOR_PLAN = 0
            correosPlan = Recurso.objects.filter((Q(campana__estrategia__plan__id=plan['id']) | Q(campana__plan__id = plan['id'])) & Q(tipo="0")).values('presupuesto')
            if correosPlan.count() > 0:
                TCOR_PLAN = correosPlan.count()
                presupuestos = [recurso['presupuesto'] for recurso in correosPlan]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PCOR_PLAN += presupuesto

            TPUB_PLAN = 0
            PPUB_PLAN = 0
            publicacionesPlan = Recurso.objects.filter((Q(campana__estrategia__plan__id=plan['id']) | Q(campana__plan__id = plan['id'])) & Q(tipo="1")).values('presupuesto')
            if publicacionesPlan.count() > 0:
                TPUB_PLAN = publicacionesPlan.count()
                presupuestos = [recurso['presupuesto'] for recurso in publicacionesPlan]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PPUB_PLAN += presupuesto

            TPAG_PLAN = 0
            PPAG_PLAN = 0
            paginasPlan = Recurso.objects.filter((Q(campana__estrategia__plan__id=plan['id']) | Q(campana__plan__id = plan['id'])) & Q(tipo="2")).values('presupuesto')
            if paginasPlan.count() > 0:
                TPAG_PLAN = paginasPlan.count()
                presupuestos = [recurso['presupuesto'] for recurso in paginasPlan]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PPAG_PLAN += presupuesto

            NCON_PLAN = 0
            CCON_PLAN = 0
            if plan['inicioVigencia'] is not None and plan['finVigencia'] is not None:
                contactosCreados = Contacto.objects.filter(Q(fechaCreacion__gte=plan['inicioVigencia']) & Q(fechaCreacion__lte=plan['finVigencia'])).values('id')
                contactosConvertidos = Contacto.objects.filter(Q(fechaConversion__gte=plan['inicioVigencia']) & Q(fechaConversion__lte=plan['finVigencia'])).values('id')
                NCON_PLAN = contactosCreados.count()
                CCON_PLAN = contactosConvertidos.count()
            
            for indicador in indicadores:
                if indicador['indicador__calculoAutomatico'] == True:
                    #calcular indicador con las variables
                    valor = 0
                    print(indicador['indicador__formula'])
                    # print(PRES_PLAN)
                    # print(TPRO_PLAN)
                    # print(PPRO_PLAN)
                    try:
                        valor = eval(indicador['indicador__formula'])
                        IndicadorAsignado.objects.filter(id=indicador['id']).update(valor = valor)
                        print("Se asigno el valor")
                    except Exception as e:
                        print("Error al calcular eval")
                    
    
    for programa in programas:
        indicadores = IndicadorAsignado.objects.filter(estrategia__id=programa['id']).values('id', 'indicador__calculoAutomatico','indicador__formula')
        if indicadores.count()>0:
        #calcular todas sus variables
            PRES_PROG = programa['presupuesto']
            PPLA_PROG = 0
            if programa['plan__id'] is not None and programa['plan__id']>0:
                plan = Plan.objects.filter(id=programa['plan__id']).values('presupuesto').first()
                if plan['presupuesto'] is not None:
                    PPLA_PROG = plan['presupuesto']

            TCPP_PROG = 0
            PCPP_PROG = 0
            campanasPPrograma = Campana.objects.filter(Q(estrategia__id=programa['id']) & Q(tipo="0")).values('presupuesto')
            if campanasPPrograma.count() > 0:
                TCPP_PROG = campanasPPrograma.count()
                presupuestos = [campana['presupuesto'] for campana in campanasPPrograma]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PCPP_PROG += presupuesto

            TCOR_PROG = 0
            PCOR_PROG = 0
            correosPrograma = Recurso.objects.filter(Q(campana__estrategia__id=programa['id']) & Q(tipo="0")).values('presupuesto')
            if correosPrograma.count() > 0:
                TCOR_PROG = correosPrograma.count()
                presupuestos = [recurso['presupuesto'] for recurso in correosPrograma]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PCOR_PROG += presupuesto

            TPUB_PROG = 0
            PPUB_PROG = 0
            publicacionesPrograma = Recurso.objects.filter(Q(campana__estrategia__id=programa['id']) & Q(tipo="1")).values('presupuesto')
            if publicacionesPrograma.count() > 0:
                TPUB_PROG = publicacionesPrograma.count()
                presupuestos = [recurso['presupuesto'] for recurso in publicacionesPrograma]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PPUB_PROG += presupuesto

            TPAG_PROG = 0
            PPAG_PROG = 0
            paginasPrograma = Recurso.objects.filter(Q(campana__estrategia__id=programa['id']) & Q(tipo="2")).values('presupuesto')
            if paginasPrograma.count() > 0:
                TPAG_PROG = paginasPrograma.count()
                presupuestos = [recurso['presupuesto'] for recurso in paginasPrograma]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PPAG_PROG += presupuesto

            NCON_PROG = 0
            CCON_PROG = 0
            if programa['inicioVigencia'] is not None and programa['finVigencia'] is not None:
                contactosCreados = Contacto.objects.filter(Q(fechaCreacion__gte=programa['inicioVigencia']) & Q(fechaCreacion__lte=programa['finVigencia'])).values('id')
                contactosConvertidos = Contacto.objects.filter(Q(fechaConversion__gte=programa['inicioVigencia']) & Q(fechaConversion__lte=programa['finVigencia'])).values('id')
                NCON_PROG = contactosCreados.count()
                CCON_PROG = contactosConvertidos.count()

            for indicador in indicadores:
                if indicador['indicador__calculoAutomatico'] == True:
                    #calcular indicador con las variables
                    valor = 0
                    try:
                        valor = eval(indicador['indicador__formula'])
                        IndicadorAsignado.objects.filter(id=indicador['id']).update(valor = valor)
                        print("Se asigno el valor")
                    except Exception as e:
                        print("Error al calcular eval")

    for campana in campanasStandAlone:
        indicadores = IndicadorAsignado.objects.filter(campana__id=campana['id']).values('id', 'indicador__calculoAutomatico','indicador__formula')
        if indicadores.count()>0:
            #calcular todas sus variables
            PRES_CAMS = campana['presupuesto']
            PPLA_CAMS = 0
            if campana['plan__id'] is not None and campana['plan__id']>0:
                plan = Plan.objects.filter(id=campana['plan__id']).values('presupuesto').first()
                if plan['presupuesto'] is not None:
                    PPLA_CAMS = plan['presupuesto']

            TCOR_CAMS = 0
            PCOR_CAMS = 0
            correosCampanaSA = Recurso.objects.filter(Q(campana__id=campana['id']) & Q(tipo="0")).values('presupuesto')
            if correosCampanaSA.count() > 0:
                TCOR_CAMS = correosCampanaSA.count()
                presupuestos = [recurso['presupuesto'] for recurso in correosCampanaSA]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PCOR_CAMS += presupuesto

            TCEN_CAMS = 5
            TCAB_CAMS = 6
            TCRE_CAMS = 7
            TCSP_CAMS = 8

            TPUB_CAMS = 0
            PPUB_CAMS = 0
            publicacionesCampanaSA = Recurso.objects.filter(Q(campana__id=campana['id']) & Q(tipo="1")).values('presupuesto')
            if publicacionesCampanaSA.count() > 0:
                TPUB_CAMS = publicacionesCampanaSA.count()
                presupuestos = [recurso['presupuesto'] for recurso in publicacionesCampanaSA]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PPUB_CAMS += presupuesto

            
            TPAG_CAMS = 0
            PPAG_CAMS = 0
            paginasCampanaSA = Recurso.objects.filter(Q(campana__id=campana['id']) & Q(tipo="2")).values('presupuesto')
            if paginasCampanaSA.count() > 0:
                TPAG_CAMS = paginasCampanaSA.count()
                presupuestos = [recurso['presupuesto'] for recurso in paginasCampanaSA]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PPAG_CAMS += presupuesto
            
            NCON_CAMS = 0
            CCON_CAMS = 0
            if campana['inicioVigencia'] is not None and campana['finVigencia'] is not None:
                contactosCreados = Contacto.objects.filter(Q(fechaCreacion__gte=campana['inicioVigencia']) & Q(fechaCreacion__lte=campana['finVigencia'])).values('id')
                contactosConvertidos = Contacto.objects.filter(Q(fechaConversion__gte=campana['inicioVigencia']) & Q(fechaConversion__lte=campana['finVigencia'])).values('id')
                NCON_CAMS = contactosCreados.count()
                CCON_CAMS = contactosConvertidos.count()

            for indicador in indicadores:
                if indicador['indicador__calculoAutomatico'] == True:
                    #calcular indicador con las variables
                    valor = 0
                    try:
                        valor = eval(indicador['indicador__formula'])
                        IndicadorAsignado.objects.filter(id=indicador['id']).update(valor = valor)
                        print("Se asigno el valor")
                    except Exception as e:
                        print("Error al calcular eval")
                    
    for campana in campanasPrograma:
        indicadores = IndicadorAsignado.objects.filter(campana__id=campana['id']).values('id', 'indicador__calculoAutomatico','indicador__formula')
        if indicadores.count()>0:
            #calcular todas sus variables
            PRES_CAMP = campana['presupuesto']
            PPRO_CAMP = 0
            if campana['estrategia__id'] is not None and campana['estrategia__id']>0:
                programa = Estrategia.objects.filter(id=campana['estrategia__id']).values('presupuesto').first()
                if programa['presupuesto'] is not None:
                    PPRO_CAMP = programa['presupuesto']

            TCOR_CAMP = 0
            PCOR_CAMP = 0
            correosCampanaP = Recurso.objects.filter(Q(campana__id=campana['id']) & Q(tipo="0")).values('presupuesto')
            if correosCampanaP.count() > 0:
                TCOR_CAMP = correosCampanaP.count()
                presupuestos = [recurso['presupuesto'] for recurso in correosCampanaP]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PCOR_CAMP += presupuesto

            TCEN_CAMP = 5
            TCAB_CAMP = 6
            TCRE_CAMP = 7
            TCSP_CAMP = 8

            TPUB_CAMP = 0
            PPUB_CAMP = 0
            publicacionesCampanaP = Recurso.objects.filter(Q(campana__id=campana['id']) & Q(tipo="1")).values('presupuesto')
            if publicacionesCampanaP.count() > 0:
                TPUB_CAMP = publicacionesCampanaP.count()
                presupuestos = [recurso['presupuesto'] for recurso in publicacionesCampanaP]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PPUB_CAMP += presupuesto

            TPAG_CAMP = 0
            PPAG_CAMP = 0
            paginasCampanaP = Recurso.objects.filter(Q(campana__id=campana['id']) & Q(tipo="2")).values('presupuesto')
            if paginasCampanaP.count() > 0:
                TPAG_CAMP = paginasCampanaP.count()
                presupuestos = [recurso['presupuesto'] for recurso in paginasCampanaP]
                for presupuesto in presupuestos:
                    if presupuesto is not None:
                        PPAG_CAMP += presupuesto

            NCON_CAMP = 0
            CCON_CAMP = 0
            if campana['inicioVigencia'] is not None and campana['finVigencia'] is not None:
                contactosCreados = Contacto.objects.filter(Q(fechaCreacion__gte=campana['inicioVigencia']) & Q(fechaCreacion__lte=campana['finVigencia'])).values('id')
                contactosConvertidos = Contacto.objects.filter(Q(fechaConversion__gte=campana['inicioVigencia']) & Q(fechaConversion__lte=campana['finVigencia'])).values('id')
                NCON_CAMP = contactosCreados.count()
                CCON_CAMP = contactosConvertidos.count()

            for indicador in indicadores:
                if indicador['indicador__calculoAutomatico'] == True:
                    #calcular indicador con las variables
                    valor = 0
                    try:
                        valor = eval(indicador['indicador__formula'])
                        IndicadorAsignado.objects.filter(id=indicador['id']).update(valor = valor)
                        print("Se asigno el valor")
                    except Exception as e:
                        print("Error al calcular eval")
                    
    for correo in correos:
        indicadores = IndicadorAsignado.objects.filter(recurso__id=correo['id']).values('id', 'indicador__calculoAutomatico','indicador__formula')
        if indicadores.count()>0:
            #calcular todas sus variables
            PRES_CORR = correo['presupuesto']
            PCAM_CORR = 0
            if correo['campana__id'] is not None and correo['campana__id']>0:
                campana = Campana.objects.filter(id=correo['campana__id']).values('presupuesto').first()
                if campana['presupuesto'] is not None:
                    PCAM_CORR = campana['presupuesto']
            IMPR_CORR = 3
            CLIC_CORR = 4
            ACEJ_CORR = 5
            ACCO_CORR = 6
            TCON_CORR = 7

            NCON_CORR = 0
            CCON_CORR = 0
            if correo['inicioVigencia'] is not None and correo['finVigencia'] is not None:
                contactosCreados = Contacto.objects.filter(Q(fechaCreacion__gte=correo['inicioVigencia']) & Q(fechaCreacion__lte=correo['finVigencia'])).values('id')
                contactosConvertidos = Contacto.objects.filter(Q(fechaConversion__gte=correo['inicioVigencia']) & Q(fechaConversion__lte=correo['finVigencia'])).values('id')
                NCON_CORR = contactosCreados.count()
                CCON_CORR = contactosConvertidos.count()

            for indicador in indicadores:
                if indicador['indicador__calculoAutomatico'] == True:
                    #calcular indicador con las variables
                    valor = 0
                    try:
                        valor = eval(indicador['indicador__formula'])
                        IndicadorAsignado.objects.filter(id=indicador['id']).update(valor = valor)
                        print("Se asigno el valor")
                    except Exception as e:
                        print("Error al calcular eval")
                    
    for publicacion in publicaciones:
        indicadores = IndicadorAsignado.objects.filter(recurso__id=publicacion['id']).values('id', 'indicador__calculoAutomatico','indicador__formula')
        if indicadores.count()>0:
            #calcular todas sus variables
            PRES_PUBL = publicacion['presupuesto']
            PCAM_PUBL = 0
            if publicacion['campana__id'] is not None and publicacion['campana__id']>0:
                campana = Campana.objects.filter(id=publicacion['campana__id']).values('presupuesto').first()
                if campana['presupuesto'] is not None:
                    PCAM_PUBL = campana['presupuesto']
            IMPR_PUBL = 3
            CLIC_PUBL = 4
            ACEJ_PUBL = 5
            ACCO_PUBL = 6
            INTE_PUBL = 7

            NCON_PUBL = 0
            CCON_PUBL = 0
            if publicacion['inicioVigencia'] is not None and publicacion['finVigencia'] is not None:
                contactosCreados = Contacto.objects.filter(Q(fechaCreacion__gte=publicacion['inicioVigencia']) & Q(fechaCreacion__lte=publicacion['finVigencia'])).values('id')
                contactosConvertidos = Contacto.objects.filter(Q(fechaConversion__gte=publicacion['inicioVigencia']) & Q(fechaConversion__lte=publicacion['finVigencia'])).values('id')
                NCON_PUBL = contactosCreados.count()
                CCON_PUBL = contactosConvertidos.count()
            
            for indicador in indicadores:
                if indicador['indicador__calculoAutomatico'] == True:
                    #calcular indicador con las variables
                    valor = 0
                    try:
                        valor = eval(indicador['indicador__formula'])
                        IndicadorAsignado.objects.filter(id=indicador['id']).update(valor = valor)
                        print("Se asigno el valor")
                    except Exception as e:
                        print("Error al calcular eval")
                
    for pagina in paginas:
        indicadores = IndicadorAsignado.objects.filter(recurso__id=pagina['id']).values('id', 'indicador__calculoAutomatico','indicador__formula')
        if indicadores.count()>0:
            #calcular todas sus variables
            PRES_PAGI = pagina['presupuesto']
            PCAM_PAGI = 0
            if pagina['campana__id'] is not None and pagina['campana__id']>0:
                campana = Campana.objects.filter(id=pagina['campana__id']).values('presupuesto').first()
                if campana['presupuesto'] is not None:
                    PCAM_PAGI = campana['presupuesto']
            CLIC_PAGI = 3
            ACEJ_PAGI = 4
            ACCO_PAGI = 5
            VISI_PAGI = 6
            TVIS_PAGI = 7

            NCON_PAGI = 0
            CCON_PAGI = 0
            if pagina['inicioVigencia'] is not None and pagina['finVigencia'] is not None:
                contactosCreados = Contacto.objects.filter(Q(fechaCreacion__gte=pagina['inicioVigencia']) & Q(fechaCreacion__lte=pagina['finVigencia'])).values('id')
                contactosConvertidos = Contacto.objects.filter(Q(fechaConversion__gte=pagina['inicioVigencia']) & Q(fechaConversion__lte=pagina['finVigencia'])).values('id')
                NCON_PAGI = contactosCreados.count()
                CCON_PAGI = contactosConvertidos.count()
            for indicador in indicadores:
                if indicador['indicador__calculoAutomatico'] == True:
                    #calcular indicador con las variables
                    valor = 0
                    try:
                        valor = eval(indicador['indicador__formula'])
                        IndicadorAsignado.objects.filter(id=indicador['id']).update(valor = valor)
                        print("Se asigno el valor")
                    except Exception as e:
                        print("Error al calcular eval")
                