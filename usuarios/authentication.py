from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken

from usuarios.models import Usuario


class AuthenticatedUsuario:
    """Envoltorio de usuario autenticado compatible con DRF."""

    is_authenticated = True
    is_anonymous = False

    def __init__(self, usuario: Usuario):
        self.usuario = usuario
        self.pk = usuario.id
        self.id = usuario.id
        self.id_cuenta = usuario.cuentaUsuario_id
        self.nombre_usuario = usuario.nombreUsuario
        self.es_administrador = usuario.esAdministrador
        self.rol = usuario.rol

    def __str__(self):
        return self.nombre_usuario or f"Usuario {self.pk}"


class UsuarioJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        usuario_id = validated_token.get("usuario_id")
        if usuario_id is None:
            raise InvalidToken("El token no contiene usuario_id.")

        try:
            usuario = Usuario.objects.select_related("cuentaUsuario", "persona").get(
                id=usuario_id
            )
        except Usuario.DoesNotExist as exc:
            raise AuthenticationFailed("Usuario no encontrado.", code="user_not_found") from exc

        return AuthenticatedUsuario(usuario)
