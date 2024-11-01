import logging
import uuid
import datetime

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import (check_password, is_password_usable,
                                         make_password)
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db.models import Q
from django.shortcuts import render
from usuarios.models import *
from usuarios.serializers import *
from relaciones.models import *
from relaciones.serializers import *
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
#from zappa.asynchronous import task

class RegistrarUsuario(APIView):
    def post(self, request,id=0):
        if request.data["idUsuario"] is not None and request.data["idUsuario"]>0:
            idUsuario = request.data["idUsuario"]
            persona = Usuario.objects.filter(id=idUsuario).values("persona__id").first()
            idPersona = persona['persona__id']
            CuentaCorreo.objects.filter(Q(usuario__id = idUsuario)).delete()
            CuentaRedSocial.objects.filter(Q(usuario__id = idUsuario)).delete()
            correos = request.data["correos"]
            for correo in correos:
                campos = {'servicio': correo['servicio'],
                          'direccion': correo['direccion'],
                        'usuario': idUsuario
                        }
                correo_serializer = CuentaCorreoSerializer(data = campos)
                if correo_serializer.is_valid():
                    correo_serializer.save()
            redes = request.data["redes"]
            for red in redes:
                campos = {'redSocial': red['redSocial'],
                          'nombreUsuario': red['nombreUsuario'],
                        'usuario': idUsuario
                        }
                red_serializer = CuentaRedSocialSerializer(data = campos)
                if red_serializer.is_valid():
                    red_serializer.save()
            usuario = Usuario.objects.filter(id=idUsuario).first()
            campos_usuario = {
                'nombreUsuario': request.data["nombreUsuario"],
                'contrasena': request.data["contrasena"],
                'foto': request.data["foto"],
                'rol': request.data["rol"],
                'esAdministrador': request.data["esAdministrador"],
            }
            usuario_serializer =UsuarioSerializer(usuario, data=campos_usuario)
            if usuario_serializer.is_valid():
                usuario_serializer.save()

            idCuenta = request.data["cuentaUsuario"]['id']
            cuenta = CuentaUsuario.objects.filter(id=idCuenta).first()
            expiracionCuenta = request.data["cuentaUsuario"]['expiracionCuenta']
            expiracionCuenta = datetime.datetime.strptime(expiracionCuenta, '%d-%m-%Y').date()
            campos_cuenta = {
                'nombre': request.data["cuentaUsuario"]['nombre'],
                'expiracionCuenta': datetime.datetime(expiracionCuenta.year,expiracionCuenta.month,expiracionCuenta.day, 0,0,0),
                'diasExpiracioncuenta': request.data["cuentaUsuario"]['diasExpiracioncuenta']
            }
            cuenta_serializer =CuentaUsuarioSerializer(cuenta, data=campos_cuenta)
            if cuenta_serializer.is_valid():
                cuenta_serializer.save()

            persona = Persona.objects.filter(id=idPersona).first()
            campos_persona = {
                 'nombreCompleto': request.data["nombreCompleto"],
            }
            persona_serializer = PersonaSerializer(persona, data=campos_persona)
            if persona_serializer.is_valid():
                persona_serializer.save()
        else:
            campos_persona = {
                 'nombreCompleto': request.data["nombreCompleto"],
            }
            persona_serializer = PersonaSerializer(data=campos_persona)
            idPersona = 0
            if persona_serializer.is_valid():
                idPersona = persona_serializer.save()
                idPersona = idPersona.id
            expiracionCuenta = request.data["cuentaUsuario"]['expiracionCuenta']
            expiracionCuenta = datetime.datetime.strptime(expiracionCuenta, '%d-%m-%Y').date()
            campos_cuenta = {
                'nombre': request.data["cuentaUsuario"]['nombre'],
                'expiracionCuenta': datetime.datetime(expiracionCuenta.year,expiracionCuenta.month,expiracionCuenta.day, 0,0,0),
                'diasExpiracioncuenta': request.data["cuentaUsuario"]['diasExpiracioncuenta']
            }
            cuenta_serializer = CuentaUsuarioSerializer(data=campos_cuenta)
            idCuenta = 0
            if cuenta_serializer.is_valid():
                idCuenta = cuenta_serializer.save()
                idCuenta = idCuenta.id
            campos_usuario = {
                'persona': idPersona,
                'nombreUsuario': request.data["nombreUsuario"],
                'contrasena': request.data["contrasena"],
                'esAdministrador': request.data["esAdministrador"],
                'rol': request.data["rol"],
                'cuentaUsuario': idCuenta
            }
            print(campos_usuario)
            usuario_serializer =UsuarioSerializer(data=campos_usuario)
            idUsuario = 0
            if usuario_serializer.is_valid():
                idUsuario = usuario_serializer.save()
                idUsuario = idUsuario.id
            correos = request.data["correos"]
            for correo in correos:
                campos = {'servicio': correo['servicio'],
                          'direccion': correo['direccion'],
                        'usuario': idUsuario
                        }
                correo_serializer = CuentaCorreoSerializer(data = campos)
                if correo_serializer.is_valid():
                    correo_serializer.save()
            redes = request.data["redes"]
            for red in redes:
                campos = {'redSocial': red['redSocial'],
                          'nombreUsuario': red['nombreUsuario'],
                        'usuario': idUsuario
                        }
                red_serializer = CuentaRedSocialSerializer(data = campos)
                if red_serializer.is_valid():
                    red_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'Usuario registrado correctamente',
                        },)	

class BuscarDetalleUsuario(APIView):
    def get(self, request,id):
        if id is not None and id > 0:
            usuario = Usuario.objects.filter(id=id).values('id', 'cuentaUsuario__id','nombreUsuario','contrasena', 'persona__nombreCompleto','rol','foto','esAdministrador').first()
            if usuario is not None:
                campos_usuario = {
                "idUsuario": usuario['id'],
                "nombreUsuario": usuario['nombreUsuario'],
                "contrasena": usuario['contrasena'],
                "nombreCompleto": usuario['persona__nombreCompleto'],
                "rol": usuario['rol'],
                "foto": usuario['foto'],
                "esAdministrador": usuario['esAdministrador'],
                "correos": [],
                "redes": [],
                "cuentaUsuario": {},
                "politicas": [],
                "correosNoDisponibles": [],
                #"notificaciones": []
                }
                correos = CuentaCorreo.objects.filter(Q(usuario__id = usuario['id'])).values('servicio','direccion')
                campos_usuario['correos'] = list(correos)
                redes = CuentaRedSocial.objects.filter(Q(usuario__id = usuario['id'])).values('redSocial','nombreUsuario')
                campos_usuario['redes'] = list(redes)
                cuentaUsuario = CuentaUsuario.objects.filter(Q(usuario__id = usuario['cuentaUsuario__id'])).values('id','nombre','expiracionCuenta','diasExpiracioncuenta').first()
                if cuentaUsuario is not None:
                    campos_usuario['cuentaUsuario'] = {"id": cuentaUsuario['id'], "nombre": cuentaUsuario['nombre'], "expiracionCuenta": cuentaUsuario['expiracionCuenta'],"diasExpiracioncuenta": cuentaUsuario['diasExpiracioncuenta']}
                politicas = UsuarioXPoliticaContrasena.objects.filter(Q(usuario__id = usuario['id'])).values('politicaContrasena__id','politicaContrasena__nombre' ,'estado')
                campos_usuario['politicas'] = list(politicas)
                for politica in campos_usuario['politicas']:
                    politica['id'] = politica['politicaContrasena__id']
                    politica['nombre'] = politica['politicaContrasena__nombre']
                    del politica['politicaContrasena__id']
                    del politica['politicaContrasena__nombre']
                correosNoDisponibles = CuentaCorreo.objects.filter(usuario__id__gte = 1).values('direccion')
                campos_usuario['correosNoDisponibles'] = [d['direccion'] for d in correosNoDisponibles]
                for correo in campos_usuario['correos']:
                    if correo['direccion'] in campos_usuario['correosNoDisponibles']: campos_usuario['correosNoDisponibles'].remove(correo['direccion'])
                return Response(campos_usuario, status = status.HTTP_200_OK)
            else:
                return Response('No se ha encontrado al usuario', status = status.HTTP_200_OK)
        return Response('No se ha encontrado al usuario', status = status.HTTP_200_OK)

class Login(APIView):
    def post(self, request,id=0):
        if request.data["nombreUsuario"] != "" and request.data["contrasena"] != "":
            response = {}
            nombreUsuario = request.data["nombreUsuario"]
            contrasena = request.data["contrasena"]
            usuario = Usuario.objects.filter(nombreUsuario=nombreUsuario, contrasena=contrasena).values('id', 'cuentaUsuario__id','nombreUsuario','contrasena', 'persona__nombreCompleto','rol','esAdministrador').first()
            if usuario is not None:
                response = {"mensaje": "Usuario encontrado",
                            "datos": {
                                "idUsuario": usuario['id'],
                                "idCuenta": usuario['cuentaUsuario__id'],
                                "nombreUsuario": usuario['nombreUsuario'],
                                "contrasena": usuario['contrasena'],
                                "nombreCompleto": usuario['persona__nombreCompleto'],
                                "rol": usuario['rol'],
                                "esAdministrador": usuario['esAdministrador']
                            }
                }
            else:
                response = {"mensaje": "Usuario no encontrado",
                            "datos": {}
                }
            return Response(response, status = status.HTTP_200_OK)
        return Response({
                            "mensaje": "No se ha ingresado usuario o contrasena",
                            "datos": {}
                        }, status = status.HTTP_200_OK)
        

class UsuarioAPIView(APIView):
    def get(self, request):
        usuarios = Usuario.objects.all()
        usuario_serializer = UsuarioSerializer(usuarios, many=True)

        return Response(usuario_serializer.data, status = status.HTTP_200_OK)

    def post(self, request):
        usuario_serializer = UsuarioSerializer(data = request.data, context = request.data)

        if usuario_serializer.is_valid():

            usuario = usuario_serializer.save()

            return Response({'id': usuario.id,
                            'message': 'Usuario creado correctamente'}, status=status.HTTP_200_OK)

        return Response(usuario_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Create your views here.
"""
class UserView(generics.ListCreateAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializerRead


class RoleView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializerRead


class EmployeeView(APIView):
    def get(self, request):

        query = Q()

        palabra_clave = request.GET.get("palabra_clave")
        puesto_id = request.GET.get("puesto")
        area_id = request.GET.get("area")
        estado = request.GET.get("estado")

        if(palabra_clave is not None):
            query.add(Q(user__username__contains=palabra_clave), Q.AND)
            ##query.add(Q(area__name__contains = palabra_clave),Q.OR)
            ##query.add(Q(area__name__contains = palabra_clave),Q.OR)
        if(puesto_id is not None):
            query.add(Q(position=puesto_id), Q.AND)
        if(area_id is not None):
            query.add(Q(area=area_id), Q.AND)
        if(estado is not None):
            query.add(Q(isActive=estado), Q.AND)

        employee = Employee.objects.filter(query)

        employee_serializado = EmployeeSerializerRead(employee, many=True)
        return Response(employee_serializado.data, status=status.HTTP_200_OK)

    def post(self, request):

        employee_serializado = EmployeeSerializerWrite(data=request.data)

        if employee_serializado.is_valid():
            employee_serializado.save()
            return Response(employee_serializado.data, status=status.HTTP_200_OK)

        return Response(employee_serializado.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        print(request.user)
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'message': 'invalid user', },)

        user_serialized = UserSerializerRead(user)

        pwd_valid = check_password(password, user.password)
        print(pwd_valid)
        if not pwd_valid:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'message': 'invalid password', },)

        token, _ = Token.objects.get_or_create(user=user)
        print(token.key)

        a_s = {}
        try:
            applicant = Applicant.objects.get(user=user)
            a_s = ApplicantSerializerRead(applicant, many=False).data
        except Exception as e:
            print(e)

        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'login correcto',
                            'token': token.key,
                            'user': user_serialized.data,
                            'applicant': a_s
                        },)


class Logout(APIView):
    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class WhoIAmView(APIView):
    def get(self, request):

        user = request.user
        roles_list = ""
        for role in user.roles.all():
            roles_list += f" {role.name},"

        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': f'eres el usuario {user} con roles:{roles_list}',
                        },)


class PasswordRecovery(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):

        email = request.data['email']
        recovery_code = str(uuid.uuid4())[0:8]
        subject = "Recuperación de contraseña"
        message = "Tu clave de recuperación de contraseña es:\n" \
            + f"{recovery_code}"

        try:
            user = User.objects.get(email=email)
        except Exception:
            logging.info("User doesn't exists")
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={
                                'message': 'El usuario no existe',
                            },)

        user.recovery_code = recovery_code
        user.save()

        print(recovery_code)

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': f'Se enviará un código de recuperación al correo {email}',
                        },)


class PasswordRecoveryCodeCheck(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):

        email = request.data['email']
        recovery_code = request.data['recovery_code']

        try:
            user = User.objects.get(email=email)
        except Exception:
            logging.info("User doesn't exists")
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={
                                'message': 'user doesnt exists',
                            },)

        if(user.recovery_code == recovery_code):
            return Response(status=status.HTTP_200_OK,
                            data={
                                f'message': 'code is valid',
                            },)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={
                                'message': 'wrong code',
                            },)


class PasswordChangeWithoutLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):

        email = request.data['email']
        new_password = request.data['new_password']
        recovery_code = request.data['recovery_code']

        try:
            user = User.objects.get(email=email)
        except Exception:
            logging.info("User doesn't exists")
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={
                                'message': 'user doesnt exists',
                            },)

        if(user.recovery_code != recovery_code):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={
                                'message': 'wrong code',
                            },)

        if(len(new_password) < 8):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={
                                f'message': 'new password is too short',
                            },)

        else:
            encoded_password = make_password(new_password)
            user.password = encoded_password
            user.save()

            print(check_password(new_password, user.password))

            return Response(status=status.HTTP_200_OK,
                            data={
                                f'message': 'password changed',
                            },)


class PasswordChangeWithLogin(APIView):

    def post(self, request, format=None):

        user = request.user

        old_password = request.data['old_password']
        new_password = request.data['new_password']

        pwd_valid = check_password(old_password, user.password)

        if not pwd_valid:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'message': 'invalid password', },)

        if(len(new_password) < 8):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={
                                f'message': 'new password is too short',
                            },)

        else:
            user.password = make_password(new_password)
            user.save()

            return Response(status=status.HTTP_200_OK,
                            data={
                                f'message': 'password changed',
                            },)


class RegisterApplicant(APIView):

    permission_classes = [AllowAny]

    def post(self, request, format=None):
        '''
        This method requires 5 fields:
        email, username, first_name, last_name, password
        method asumes a "Postulante" role exists
        '''

        try:
            email = request.data['email']
            user = User.objects.filter(email=email)

            if user:
                logging.info(f"User {user} already exists")
                print(f"User {user} already exists")
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={
                                    'message': 'email already exists',
                                },)

            username = request.data['username']
            user = User.objects.filter(username=username)

            if user:
                logging.info(f"User {user} already exists")
                print(f"User {user} already exists")
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={
                                    'message': 'username already exists',
                                },)

            first_name = request.data['first_name']
            last_name = request.data['last_name']
            password = request.data['password']

        except Exception as e:
            logging.info(f"Exception: {e}")
            print(f"Exception: {e}")
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={
                                'message': f'Exception: {e}',
                            },)

        role = Role.objects.get(name="Postulante")
        print(role)

        user, created = User.objects.get_or_create(
            email=email,
            username=username,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
            }
        )

        encoded_password = make_password(password)
        user.password = encoded_password
        user.roles.add(role)
        user.save()

        # creating Applicant
        applicant, _ = Applicant.objects.get_or_create(
            user=user
        )

        if created:
            return Response(status=status.HTTP_200_OK,
                            data={
                                f'message': 'user created successfully',
                            },)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={
                                'message': f'Error: user already exists',
                            },)
"""