from django.urls import include, path
from marketing.views import *

urlpatterns = [
    path('detalleIndicador/<int:id>', BuscarDetalleIndicador.as_view()),
    path('filtrarIndicadores', FiltrarIndicadores.as_view()),
    path('registrarIndicador', RegistrarIndicador.as_view()),
    path('eliminarIndicador/<int:id>', EliminarIndicador.as_view()),

    path('detallePlan/<int:id>', BuscarDetallePlan.as_view()),
    path('filtrarPlanes', FiltrarPlanes.as_view()),
    path('registrarPlan', RegistrarPlan.as_view()),
    path('eliminarPlan/<int:id>', EliminarPlan.as_view()),
    
    path('detalleEstrategia/<int:id>', BuscarDetalleEstrategia.as_view()),
    path('filtrarEstrategias', FiltrarEstrategias.as_view()),
    path('registrarEstrategia', RegistrarEstrategia.as_view()),
    path('eliminarEstrategia/<int:id>', EliminarEstrategia.as_view()),

    path('detalleCampana/<int:id>', BuscarDetalleCampana.as_view()),
    path('filtrarCampanas', FiltrarCampanas.as_view()),
    path('registrarCampana', RegistrarCampana.as_view()),
    path('eliminarCampana/<int:id>', EliminarCampana.as_view()),

    path('detalleRecurso/<int:id>', BuscarDetalleRecurso.as_view()),
    path('filtrarRecursos', FiltrarRecursos.as_view()),
    path('registrarRecurso', RegistrarRecurso.as_view()),
    path('eliminarRecurso/<int:id>', EliminarRecurso.as_view()),

    path('detalleOportunidad/<int:id>', BuscarDetalleOportunidad.as_view()),
    path('filtrarOportunidades', FiltrarOportunidades.as_view()),
    path('registrarOportunidad', RegistrarOportunidad.as_view()),
    path('eliminarOportunidad/<int:id>', EliminarOportunidad.as_view()),


    path('filtrarVariables', FiltrarVariables.as_view()),

    path('aplicarFiltrosReporte', AplicarFiltrosReporte.as_view()),
    path('detalleReporte/<int:id>', BuscarDetalleReporte.as_view()),
    path('filtrarReportes', FiltrarReportes.as_view()),
    path('registrarReporte', RegistrarReporte.as_view()),
    path('eliminarReporte/<int:id>', EliminarReporte.as_view()),

    path('crearComponenteInforme', CrearComponenteInforme.as_view()),
    path('detalleDashboard/<int:id>', BuscarDetalleDashboard.as_view()),
    path('filtrarDashboards', FiltrarDashboards.as_view()),
    path('registrarDashboard', RegistrarDashboard.as_view()),
    path('eliminarDashboard/<int:id>', EliminarDashboard.as_view()),

    path('detalleFlujo/<int:id>', BuscarDetalleFlujo.as_view()),
    path('filtrarFlujos', FiltrarFlujos.as_view()),
    path('registrarFlujo', RegistrarFlujo.as_view()),
    path('eliminarFlujo/<int:id>', EliminarFlujo.as_view()),

    path('detalleDashboardPrincipal/<int:id>', BuscarPrincipalDashboard.as_view()),



]