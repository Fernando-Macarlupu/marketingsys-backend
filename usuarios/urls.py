from django.urls import path
from usuarios.views import *

urlpatterns = [

    path('detalleUsuario/<int:id>', BuscarDetalleUsuario.as_view()),
    path('usuario/', UsuarioAPIView.as_view()),
    path('registrarUsuario', RegistrarUsuario.as_view()),
    path('login', Login.as_view()),
]

"""
    path('users', UserView.as_view()),
    path('roles', RoleView.as_view()),
    path('employee', EmployeeView.as_view()),
    path('login', LoginView.as_view()),
    path('whoiam', WhoIAmView.as_view()),
    path('logout', Logout.as_view()),
    path('password_recovery', PasswordRecovery.as_view()),
    path('password_recovery_code_check', PasswordRecoveryCodeCheck.as_view()),
    path('password_change_without_login', PasswordChangeWithoutLogin.as_view()),
    path('password_change_with_login', PasswordChangeWithLogin.as_view()),
    path('register_applicant', RegisterApplicant.as_view()),
"""