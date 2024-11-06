from django.urls import include, path
from relaciones.views import *

urlpatterns = [
    path('correosNoDisponibles', BuscarCorreosNoDisponibles.as_view()),
    path('nombresNoDisponibles', BuscarNombresNoDisponibles.as_view()),

    path('detalleContacto/<int:id>', BuscarDetalleContacto.as_view()),
    path('filtrarContactos', FiltrarContactos.as_view()),
    path('registrarContacto', RegistrarContacto.as_view()),
    path('eliminarContacto/<int:id>', EliminarContacto.as_view()),
    path('cargarContactos', CargarContactos.as_view()),
    
    path('detalleEmpresa/<int:id>', BuscarDetalleEmpresa.as_view()),
    path('filtrarEmpresas', FiltrarEmpresas.as_view()),
    path('registrarEmpresa', RegistrarEmpresa.as_view()),
    path('eliminarEmpresa/<int:id>', EliminarEmpresa.as_view()),
    path('cargarEmpresas', CargarEmpresas.as_view()),

    path('aplicarFiltrosLista', AplicarFiltrosLista.as_view()),

    path('filtrarListas', FiltrarListas.as_view()),
    path('registrarLista', RegistrarLista.as_view()),
]