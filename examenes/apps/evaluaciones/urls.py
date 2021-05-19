from django.contrib import admin
from django.urls import path

from . import views

app_name = "exams_app"

urlpatterns = [
    path('crearevaluacion',views.CrearEvaluacionView.as_view(),name="crearevaluacion"),
    path('evaluaciones',views.EvaluacionesListView.as_view(),name="evaluaciones"),
    path('api/categorias/list',views.CategoriaListAPIView.as_view(),name="categoriasapi"),
    path('api/evaluaciones/list',views.EvaluacionesListAPIView.as_view(),name="evaluacionesapi"),
    path('detalleevaluacion/<slug>/',views.EvaluacionDetailView.as_view(),name="detalleeva"),
    path('calificar-dificultad/<pk>/',views.CalificarDificultadEva.as_view(),name="calificareva"),
    path('valorar-evaluacion/<pk>/',views.ValorarEvaView.as_view(),name="valorareva"),
    path('seguireva/<evaluacion>/',views.SeguirEvaluacionView.as_view(),name="seguireva"),
    path('editarevaluacion/<pk>/',views.EditarEvaluacionView.as_view(),name="editareva"),
    path('verpreguntasevaluacion/<pk>/',views.VerPreguntasEvaluacion.as_view(),name="verpreguntaseva"),
    path('borrarpregunta/<pk>/',views.BorrarPregunta.as_view(),name="borrarpregunta"),
    path('editarpregunta/<pk>/',views.EditarPregunta.as_view(),name="editarpregunta"),
    path('agregarpreguntas/<pk>/',views.AgregarPreguntas.as_view(),name="agregarpreguntas"),
    path('verinteracciones/<pk>/',views.VerInteracciones.as_view(),name="verinteracciones"),
    path('verintentosevaluacion/<pk>/<usuario>/',views.VerIntentosMiEvaluacion.as_view(),name="verintentos"),

]
