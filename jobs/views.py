from django.shortcuts import render
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from django.core.mail import get_connection, send_mail, EmailMultiAlternatives
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from marketing.models import *
from marketing.serializers import RecursoSerializer
from relaciones.models import CuentaCorreo

# Create your views here.
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(publicarCorreos, 'interval', minutes=1)
    scheduler.start()


def publicarCorreos():
    recursos = Recurso.objects.filter(tipo="0").values('id', 'descripcion','fechaPublicacion','asuntoCorreo','remitenteCorreo','remitenteContrasena','contenidoHTML')
    listaRecursos = list(recursos)
    print(listaRecursos)
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
                    if host != "" and recurso['remitenteCorreo'] != "" and recurso['remitenteContrasena'] != "":
                        print("mandar al host")
                        #a
                        my_host = host
                        my_port = 587
                        my_username = recurso['remitenteCorreo']
                        my_password = recurso['remitenteContrasena']
                        my_use_tls = True
                        connection = get_connection(host=my_host, 
                                                     port=my_port, 
                                                     username=my_username, 
                                                     password=my_password, 
                                                    use_tls=my_use_tls,
                                                    fail_silently=False)
                        connection.open()
                        plain_message = None
                        if recurso['contenidoHTML'] is not None:
                            plain_message = strip_tags(recurso['contenidoHTML'])
                        message = EmailMultiAlternatives(subject=recurso['asuntoCorreo'], 
                                                         body=plain_message,
                                                         from_email=recurso['remitenteCorreo'], #ver si esta bien o poner none
                                                         bcc=correosEnviar, #ver si funciona bien o poner to=
                                                         connection=connection)
                        if recurso['contenidoHTML'] is not None:
                            message.attach_alternative(recurso['contenidoHTML'], "text/html")
                        message.send()
                        connection.close()
                        # send_mail('diditwork?', 'test message', 'from_email', ['to'], connection=connection)
                        # # or
                        # EmailMessage('diditwork?', 'test message', 'from_email', ['to'], connection=connection).send(fail_silently=False)
            #print("Fecha: {}".format(recurso['fechaPublicacion'].replace(tzinfo=None)))
    print("I love python {}".format(datetime.datetime.now().replace(second=0, microsecond=0)))

def publicarRedesSociales():
    recursos = Recurso.objects.filter(tipo="1").values('id','redSocial' ,'descripcion','fechaPublicacion','asuntoCorreo','remitenteCorreo','remitenteContrasena','contenidoHTML')
    listaRecursos = list(recursos)
    print(listaRecursos)
    fechaHoy = datetime.datetime.now().replace(second=0, microsecond=0)
    for recurso in listaRecursos:
        if recurso['fechaPublicacion'] is not None:
            fechaPub = recurso['fechaPublicacion'].replace(tzinfo=None)
            if fechaPub == fechaHoy:
                print("Se sube la publicacion")
                if recurso['servicioRedSocial'] == "0":
                    #publicacion facebook
                    #import requests
                    user_token = recurso['tokenUsuario']
                    id_pagina = recurso['idPagina']
                    multimedia = recurso['multimedia']
                    version = 'v13.0'
                    postId = 0
                    page_access_token = ""
                    #obtener el page_access_token con el user_token y id_pagina
                    urlUser = f"https://graph.facebook.com/{version}/{id_pagina}"
                    paramsUser = {
                        'access_token': user_token,
                    }
                    try:
                        response = requests.post(urlUser, params=paramsUser)
                        result = response.json()

                        if 'access_token' in result:
                            print(f"Page access token: {result['access_token']}")
                            page_access_token = result['access_token']
                        else:
                            print(f"Error access token: {result}")
                    except requests.exceptions.RequestException as e:
                        print(f"Request error: {e}")

                    if multimedia == True and page_access_token!="":
                        url = f"https://graph.facebook.com/{version}/{id_pagina}/photos"
                        params = {
                            'access_token': page_access_token,
                            'message': recurso['textoRedSocial'],
                            'url': photo_url,
                        }
                        try:
                            response = requests.post(url, params=params)
                            result = response.json()

                            if 'id' in result:
                                print(f"Photo posted successfully. Post ID: {result['id']}")
                                postId = result['id']
                            else:
                                print(f"Error posting photo: {result}")

                        except requests.exceptions.RequestException as e:
                            print(f"Request error: {e}")
                    else:
                        url = f'https://graph.facebook.com/{version}/{id_pagina}/feed'
                        payload = {
                            'message': recurso['textoRedSocial'],
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
                                print(f"Error posting photo: {result}")
                        except requests.exceptions.RequestException as e:
                            print(f"Request error: {e}")

                    #guardar el postid
                    if postId!=0:
                        #guardarpostid
                        recursoGuardado = Recurso.objects.filter(id=recurso['id']).first()
                        campos_recurso = {
                            'postId': postId
                        }
                        recurso_serializer = RecursoSerializer(recursoGuardado, data=campos_recurso)
                        if recurso_serializer.is_valid():
                            recurso_serializer.save()

                    #post_url = 'https://graph.facebook.com/{}/feed'.format(page_id_1)

                    #access_token = '<your_access_token>'
                    #user_id = '<user_id>'

                    #url = f'https://graph.facebook.com/{user_id}?access_token={access_token}'

                    #response = requests.get(url)

                    #print(response.json())