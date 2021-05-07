from django.shortcuts import render
from django.views.generic import TemplateView,DetailView, CreateView, UpdateView, View, FormView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy
from rest_framework.views import APIView

#ORM
from django.db.models import Avg, Case, Count, F, FloatField, Max, Q, Value, When
# User
from django.contrib.messages.views import SuccessMessageMixin 
from django.contrib.auth.mixins import LoginRequiredMixin 
from apps.users.serializers import LoginSocialSerializer
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib import messages
User = get_user_model()

#third party
from rest_framework.response import Response
from rest_framework.reverse import reverse
from firebase_admin import auth

#propio
from apps.intentos.models import Intento
from apps.users.models import SeguirUsuario
from apps.evaluaciones.models import Evaluacion, SeguirEvaluacion, ValorarEvaluacion
from apps.users.forms import AuthenticationEmailForm, CreatePasswordForm, UpdateUserForm, UserRegistroForm
from django.http import HttpResponseRedirect


class Inicio(TemplateView):
    template_name = "home/inicio.html"

class RegistroView(CreateView):
    form_class = UserRegistroForm
    template_name = 'users/registro.html'
    
    def form_valid(self, form):
        #save the new user first
        form.save()
        #get the username and password
        username = self.request.POST['username']
        password = self.request.POST['password1']
        #authenticate user then login
        user = authenticate(username=username, password=password)   
        login(self.request, user)
        messages.success(self.request,"Usuario registrado con exito, bienvenido")
        
        return HttpResponseRedirect(
                reverse(
                    'users_app:inicio'
                )
            )

class LoginView(SuccessMessageMixin,LoginView):
    template_name = 'users/login.html'
    success_message = "Bienvenido!!!"
    authentication_form = AuthenticationEmailForm

class SocialLoginView(APIView):
    
    serializer_class = LoginSocialSerializer
    
    def post(self,request):

        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        token = serializer.data.get('token_id')
        decoded_token = auth.verify_id_token(token)
        email = decoded_token["email"]
        name = decoded_token["name"]
        username = str(email).split("@")[0]
        
        usuario, created = User.objects.get_or_create(
            email = email,
            defaults={
                'username': str(username),
                'full_name': name
            }
        )
        
        login(request,usuario)
        
        messages.success(request,"Login exitoso")
        return Response({ 'user': name, } )
    
class LogoutView(LoginRequiredMixin,LogoutView):
    login_url = reverse_lazy('users_app:login')
    next_page = reverse_lazy('users_app:inicio')
    
    def get_next_page(self):
        next_page = super(LogoutView, self).get_next_page()
        messages.success(self.request, 'Hasta Pronto')
        return next_page


class UserDetailView(DetailView):
    model = User
    template_name = "users/perfilusuario.html"
    context_object_name = 'usuario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        total_intentos = Intento.objects.filter(
                    usuario__slug=self.kwargs["slug"]
                ).aggregate(
                    total=Count('id'),
                    promedio=Avg('puntuacion'),
                    aprobados=Count('aprobado',filter=Q(aprobado=True)),
                    evaluaciones=Count('evaluacion',distinct=True),
                    perfectas=Count('aprobado',filter=Q(puntuacion=100)))

        evaluaciones = Evaluacion.objects.filter(intentos__usuario__slug=self.kwargs["slug"]
                ).annotate(max_p=Max('intentos__puntuacion',filter=Q(intentos__usuario__slug=self.kwargs["slug"])),
                    tot_intentos=Count('intentos__id',filter=Q(intentos__usuario__slug=self.kwargs["slug"])),
                    restantes=F('intentos_permitidos')- Count('intentos__id',filter=Q(intentos__usuario__slug=self.kwargs["slug"])))
        try:
            porcentaje_aprobados = total_intentos["aprobados"]/total_intentos["evaluaciones"]*100
        except:
            porcentaje_aprobados = None
            
        try:
            porcentaje_perfectas = total_intentos["perfectas"]/total_intentos["evaluaciones"]*100
        except:
            porcentaje_perfectas = None
        
        context["evaluaciones"] = evaluaciones
        context["total_intentos"] = total_intentos
        context["porcentaje_aprobados"] = porcentaje_aprobados
        context["porcentaje_perfectas"] = porcentaje_perfectas
        
        
        #evaluaciones propias
        Valoraciones_eva_propias = ValorarEvaluacion.objects.filter(evaluacion__user__slug=self.kwargs["slug"]).aggregate(cant=Count('id'),prom=Avg('valor'))
        seguidores_eva_propias = SeguirEvaluacion.objects.filter(evaluacion__user__slug=self.kwargs["slug"]).aggregate(cant=Count('id'))
        dificultad_evaluaciones = Evaluacion.objects.filter(user__slug=self.kwargs["slug"]).aggregate(prom=Avg('dificultad_ponderada'))
        total_intentos_eva_propias = Intento.objects.filter(evaluacion__user__slug=self.kwargs["slug"]).aggregate(cant=Count('id'))
        context["Valoraciones_eva_propias"] = Valoraciones_eva_propias
        context["seguidores_eva_propias"] = seguidores_eva_propias["cant"]
        context["dificultad_evaluaciones"] = dificultad_evaluaciones["prom"]
        context["total_intentos_eva_propias"] = total_intentos_eva_propias["cant"]
        
        #listar evaluaciones propias

        usuario = User.objects.get(slug=self.kwargs["slug"])
        
        if self.request.user == usuario:

            eva_propias = Evaluacion.objects.filter(
                user__slug=self.kwargs["slug"]
                ).annotate(tot_valoraciones=Count('valorar', distinct=True),
                        prom_valoraciones=Avg('valorar__valor'),
                        tot_seguidores=Count('seguir', distinct=True),
                        tot_intentos=Count('intentos', distinct=True),
                        prom_intentos=Avg('intentos__puntuacion'),
                        total_preguntas=Count('preguntas', distinct=True),
                        total_aprobados=Count('intentos__aprobado',filter=Q(intentos__aprobado=True)),
                        aprobados= Case(When(tot_intentos=0,then=0),default=Count('intentos__aprobado',filter=Q(intentos__aprobado=True))*100/Count('intentos'),output_field=FloatField())
                                                                                                     
                        # Count('intentos__aprobado'),filter=Q(intentos__aprobado=True))/Count('intentos')*100
                        )
        else:
            eva_propias = Evaluacion.objects.filter(
                user__slug=self.kwargs["slug"],publico=True
                ).annotate(tot_valoraciones=Count('valorar', distinct=True),
                        prom_valoraciones=Avg('valorar__valor'),
                        tot_seguidores=Count('seguir', distinct=True),
                        tot_intentos=Count('intentos', distinct=True),
                        prom_intentos=Avg('intentos__puntuacion'),
                        total_preguntas=Count('preguntas', distinct=True),
                        total_aprobados=Count('intentos__aprobado',filter=Q(intentos__aprobado=True)),
                        aprobados= Case(When(tot_intentos=0,then=0),default=Count('intentos__aprobado',filter=Q(intentos__aprobado=True))*100/Count('intentos'),output_field=FloatField())
                                                                                                     
                        # Count('intentos__aprobado'),filter=Q(intentos__aprobado=True))/Count('intentos')*100
                        )
            
            
        context["evaluaciones_propias"] = eva_propias
        
        #Seguidores
        
        seguidores = SeguirUsuario.objects.filter(seguido__slug=self.kwargs["slug"]).aggregate(total=Count('id'))
        #Seguidos
        seguidos = SeguirUsuario.objects.filter(seguidor__slug=self.kwargs["slug"]).aggregate(total=Count('id'))
         #Evaluaciones
        eva_seguidas = SeguirEvaluacion.objects.filter(usuario__slug=self.kwargs["slug"]).aggregate(total=Count('id'))
        context["seguidores"] = seguidores
        context["seguidos"] = seguidos
        context["eva_seguidas"] = eva_seguidas
        
        
        return context


class UserUpdateView(LoginRequiredMixin,UpdateView):
    model= User
    form_class= UpdateUserForm
    template_name = "users/updateuser.html"
    login_url = reverse_lazy('users_app:login')
    
    def get_success_url(self):
        
        messages.success(self.request,"Cambios realizados con exito")
        print(self.request.user)
        
        return reverse(
                'users_app:detalleusuario',kwargs={'slug': self.request.user.slug}
            )
        

class BorrarFoto(LoginRequiredMixin,View):
    
    def post(self,request,*args,**kwargs):
        user = self.request.user
        user.foto.delete()
        user.save()
        messages.success(self.request, 'Foto borrada')
        return HttpResponseRedirect(
            reverse(
                'users_app:updateusuario',kwargs={'slug': user.slug}
            )
        ) 

class UserDeleteView(LoginRequiredMixin,View):
    login_url = reverse_lazy('home_app:loginusuario')
    
    def post(self,request,*args,**kwargs):
        
        user = User.objects.get(id=self.request.user.id)
        user.delete()
        messages.success(self.request, 'Cuenta eliminada con exito')        
        
        return HttpResponseRedirect(
                reverse(
                    'users_app:inicio'
                )
            )

class CambiarPassword(LoginRequiredMixin,PasswordChangeView):
    template_name = "users/cambiarpassword.html"
    success_url = reverse_lazy('users_app:login')
    login_url = reverse_lazy('users_app:login')
    
    def form_valid(self, form):
        messages.success(self.request, "Contraseña modificada correctamente, por favor inicie sesión nuevamente")
        logout(self.request)
        return super().form_valid(form)


#solo para usuarios que se registraron por redes sociales:

class CrearPassword(LoginRequiredMixin, FormView):

    form_class= CreatePasswordForm
    template_name = "users/crearpassword.html"
    success_url = reverse_lazy('users_app:inicio')
    login_url = reverse_lazy('users_app:login')
    
    def get_form_kwargs(self):
        kwargs = super(CrearPassword, self).get_form_kwargs()

        kwargs['email'] = self.request.user.email

        return kwargs
    
    def form_valid(self, form):
        print("ya entra aca")
        password=form.cleaned_data["password1"]
        user = self.request.user
        
        user.set_password(password)
        user.save(update_fields=["password"])
        
        messages.success(self.request,"Password creada con exito, es necesario que inicies sesión nuevamente")
        logout(self.request)
        return super(CrearPassword, self).form_valid(form) 
        

class SeguirUsuarioView(LoginRequiredMixin,View):
    
    login_url = reverse_lazy('users_app:login')
    
    def post(self,request,*args,**kwargs):
        seguidor = self.request.user
        seguido = User.objects.get(id=self.kwargs['pk'])
        try:
            SeguirUsuario.objects.create(
                seguidor = seguidor,
                seguido = seguido,
            )
        except:
            SeguirUsuario.objects.get(
                seguidor = seguidor,
                seguido = seguido,
            ).delete()

        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))  
    

class SeguidoresPerfilView(LoginRequiredMixin,DetailView):
    
    model = User
    login_url = reverse_lazy('users_app:login')
    template_name = 'users/seguidores.html'
    context_object_name = 'usuario'
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)    
        context["boton_activo"] = True       
        
        return context
        
    
    
class SeguidosPerfilView(LoginRequiredMixin,DetailView):
    
    model = User
    login_url = reverse_lazy('users_app:login')
    template_name = 'users/seguidos.html'
    context_object_name = 'usuario'
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)    
        context["boton_activo"] = True       
        
        return context
    
class EvaluacionesFavoritasPerfilView(LoginRequiredMixin,DetailView):
    
    model = User
    login_url = reverse_lazy('users_app:login')
    template_name = 'users/evaluaciones_seguidas.html'
    context_object_name = 'usuario'
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)    
        context["boton_activo"] = True       
        
        return context