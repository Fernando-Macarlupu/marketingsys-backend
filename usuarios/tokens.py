from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_usuario(usuario) -> dict:
    refresh = RefreshToken()
    refresh["usuario_id"] = usuario.id
    refresh["id_cuenta"] = usuario.cuentaUsuario_id
    refresh["nombre_usuario"] = usuario.nombreUsuario
    refresh["es_administrador"] = usuario.esAdministrador
    refresh["rol"] = usuario.rol or ""

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
