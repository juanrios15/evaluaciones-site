from django.contrib import admin
from django.urls import path

from . import views

app_name = "users_app"

urlpatterns = [
   path('',views.Inicio.as_view(),name="inicio"),
   path('registro/',views.RegistroView.as_view(),name="registro"),
   path('login/',views.LoginView.as_view(),name="login"),
   path('api/sociallogin/',views.SocialLoginView.as_view()),
   path('api/notificaciones/usuario', views.NotificacionListView.as_view(),name='notificaciones'),
   path('api/eliminarnoti/<pk>/', views.DeleteNotificacionAPIView.as_view(),name='eliminarnoti'),
   path('logout/',views.LogoutView.as_view(),name="logout"),
   path('detalleusuario/<slug>/',views.UserDetailView.as_view(),name="detalleusuario"),
   path('updateusuario/<slug>/',views.UserUpdateView.as_view(),name="updateusuario"),
   path('borrarfotoactual',views.BorrarFoto.as_view(),name="borrarfoto"),
   path('eliminarusuario/',views.UserDeleteView.as_view(),name="eliminarcuenta"),
   path('cambiarpassword/',views.CambiarPassword.as_view(),name="cambiarpassword"),
   path('crearpassword/',views.CrearPassword.as_view(),name="crearpassword"),
   
   #seguir usuario
   path('seguirusuario/<pk>/',views.SeguirUsuarioView.as_view(),name="seguirusuario"),
   
   path('intentosusuario/<pk>/',views.IntentosUsuario.as_view(),name="intentosperfilusuario"),
   path('evaluacionessusuario/<pk>/',views.EvaluacionesUsuario.as_view(),name="evaluacionesperfilusuario"),
   path('seguidoresusuario/<pk>/',views.SeguidoresPerfilView.as_view(),name="seguidoresusuario"),
   path('seguidosusuario/<pk>/',views.SeguidosPerfilView.as_view(),name="seguidosusuario"),
   path('favoritosusuario/<pk>/',views.EvaluacionesFavoritasPerfilView.as_view(),name="evaluacionesfavoritasusuario"),
   path('verintentoseva/<pk>/',views.VerIntentos.as_view(),name="verintentoseva"),
   
   #Rankings
   
   path('rankings/',views.RankingsListView.as_view(),name="rankings"),
   path('politica-de-privacidad/',views.PoliticaPrivacidad.as_view(),name="politica"),
   # path('actualizar-rango-usuarios/',views.ActualizarRangos.as_view(),name="actualizar"),

]