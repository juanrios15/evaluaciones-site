from django.contrib import admin
from django.urls import path

from . import views

app_name = "intentos_app"

urlpatterns = [
    path('iniciarintento/<exam>',views.IniciarIntento.as_view(),name="iniciarintento"),
    path('intentopregunta/<intento>',views.IntentoView.as_view(),name="intentopregunta"),
    path('resultadointento/<pk>',views.ResultadoIntento.as_view(),name="resultadointento"),

]