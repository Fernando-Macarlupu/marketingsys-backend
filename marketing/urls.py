from django.urls import include, path
from marketing.views import *

urlpatterns = [

    path('filtrarIndicadores', FiltrarIndicadores.as_view()),
    path('registrarIndicadores', RegistrarIndicador.as_view()),

    path('filtrarPlanes', FiltrarPlanes.as_view()),
    path('registrarPlan', RegistrarPlan.as_view()),
    
    path('filtrarEstrategias', FiltrarEstrategias.as_view()),
    path('registrarEstrategia', RegistrarEstrategia.as_view()),

    path('filtrarCampanas', FiltrarCampanas.as_view()),
    path('registrarCampana', RegistrarCampana.as_view()),

    path('filtrarRecursos', FiltrarRecursos.as_view()),
    path('registrarRecurso', RegistrarRecurso.as_view()),

    path('filtrarOportunidades', FiltrarOportunidades.as_view()),
    path('registrarOportunidad', RegistrarOportunidad.as_view()),


]