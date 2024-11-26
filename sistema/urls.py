from django.urls import include, path
from sistema.views import *

urlpatterns = [
    path('filtrarLogs', FiltrarLogs.as_view()),
]