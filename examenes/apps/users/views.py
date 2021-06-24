from django.shortcuts import render
from django.views.generic import TemplateView,DetailView, CreateView, UpdateView, View, FormView, ListView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy


#ORM
from django.db.models import Avg, Case, Count, F, FloatField, Max, Q, Sum, Value, When, Window
# User
from django.contrib.messages.views import SuccessMessageMixin 
from django.contrib.auth.mixins import LoginRequiredMixin 
from apps.users.serializers import LoginSocialSerializer, NotificacionSerializer


from django.contrib.auth import authenticate, get_user_model, login, logout
User = get_user_model()

from django.contrib import messages

#third party
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, DestroyAPIView
from firebase_admin import auth
#propio
from apps.intentos.models import Intento, PuntosObtenidos
from apps.users.models import Notificacion, SeguirUsuario
from apps.evaluaciones.models import Categoria, Evaluacion, SeguirEvaluacion, ValorarEvaluacion
from apps.users.forms import AuthenticationEmailForm, CreatePasswordForm, UpdateUserForm, UserRegistroForm
from django.http import HttpResponseRedirect
from django.db.models.functions import Coalesce, RowNumber
from django.core.paginator import Paginator
from django.utils import timezone

from apps.intentos.views import ranquear_usuario

def establecer_orden(orden):
    if orden == "Intentos restantes":
        order="-restantes"
    elif orden == "Puntuación más alta":
        order="-max_p"
    elif orden == "Puntuación más baja":
        order="max_p"
    elif orden == "Dificiles":
        order="-dificultad_ponderada"
    elif orden == "Faciles":
        order="-dificultad_ponderada"
    else:
        order = "-ultimo_intento"
    return order


def establecer_orden_eva(orden):
    if orden ==  "Valoraciones":
        order="-tot_valoraciones"
    elif orden == "Dificiles":
        order="-dificultad_ponderada"
    elif orden == "Faciles":
        order="-dificultad_ponderada"
    elif orden == "Más seguidos":
        order="-tot_seguidores"
    else:
        order = "-created_at"
    return order


class Inicio(TemplateView):
    template_name = "home/inicio.html"
    
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        
        context["categorias"] = Categoria.objects.all()
        
        top3 = User.objects.annotate(
            puntos_total=Coalesce(Sum("usuario_puntos__puntos",distinct=True),Value(0))
            ).order_by("-puntos_total",'username')[:3]
        context["top"] = top3
        
        return context

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
    
    def get_success_url(self):
        
        return reverse(
                'users_app:inicio'
            )
        
    
class LogoutView(LoginRequiredMixin,LogoutView):
    login_url = reverse_lazy('users_app:login')
    next_page = reverse_lazy('users_app:inicio')
    
    def get_next_page(self):
        next_page = super(LogoutView, self).get_next_page()
        messages.success(self.request, 'Hasta Pronto')
        return next_page

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
    


class UserDetailView(DetailView):
    model = User
    template_name = "users/perfilusuario.html"
    context_object_name = 'usuario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        total_intentos = Intento.objects.filter(
                    usuario__slug=self.kwargs["slug"]
                ).aggregate(
                    total=Count('id',distinct=True),
                    promedio=Avg('puntuacion'),
                    aprobados=Count('id',filter=Q(aprobado=True),distinct=True),
                    evaluaciones=Count('evaluacion',distinct=True),
                    perfectas=Count('aprobado',filter=Q(puntuacion=100)))

        try:
            porcentaje_aprobados = total_intentos["aprobados"]/total_intentos["evaluaciones"]*100
        except:
            porcentaje_aprobados = None
        try:
            porcentaje_perfectas = total_intentos["perfectas"]/total_intentos["evaluaciones"]*100
        except:
            porcentaje_perfectas = None
        
        context["total_intentos_usuario"] = total_intentos["total"]
        context["total_intentos"] = total_intentos
        context["porcentaje_aprobados"] = porcentaje_aprobados
        context["porcentaje_perfectas"] = porcentaje_perfectas
        
        #evaluaciones propias
        Valoraciones_eva_propias = ValorarEvaluacion.objects.filter(evaluacion__user__id=context["usuario"].id).aggregate(cant=Count('id'),prom=Avg('valor'))
        seguidores_eva_propias = SeguirEvaluacion.objects.filter(evaluacion__user__id=context["usuario"].id).aggregate(cant=Count('id'))
        dificultad_evaluaciones = Evaluacion.objects.filter(user__id=context["usuario"].id).aggregate(prom=Avg('dificultad_ponderada'),count=Count('id'))
        total_intentos_eva_propias = Intento.objects.filter(evaluacion__user__id=context["usuario"].id).aggregate(cant=Count('id'))
        
        context["Valoraciones_eva_propias"] = Valoraciones_eva_propias
        context["seguidores_eva_propias"] = seguidores_eva_propias["cant"]
        context["dificultad_evaluaciones"] = dificultad_evaluaciones["prom"]
        context["total_evaluaciones"] = dificultad_evaluaciones["count"]
        context["total_intentos_eva_propias"] = total_intentos_eva_propias["cant"]
        
        #Seguidores
        
        context["seguidores"] =SeguirUsuario.objects.filter(seguido__id=context["usuario"].id).count()
        context["seguidos"] =SeguirUsuario.objects.filter(seguidor__id=context["usuario"].id).count()
        context["favoritos"] =SeguirEvaluacion.objects.filter(usuario__id=context["usuario"].id).count()
        
        total_puntos = PuntosObtenidos.objects.filter(
                            usuario__id=context["usuario"].id
                        ).aggregate(total=Sum('puntos'))
        if total_puntos["total"] == None:
            total_puntos["total"] = 0
        context["total_puntos"] = total_puntos["total"]
        
        return context


class UserUpdateView(LoginRequiredMixin,UpdateView):
    model= User
    form_class= UpdateUserForm
    template_name = "users/updateuser.html"
    login_url = reverse_lazy('users_app:login')
    
    def get_success_url(self):
        
        messages.success(self.request,"Cambios realizados con exito")
        
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
            t = timezone.now().strftime('%d %B %Y %H:%M')
            noti = Notificacion.objects.create(
                usuario = seguido,
                usuario_notificacion = seguidor,
                mensaje = f"{seguidor} ha comenzado a seguirte. Fecha: {t}"
                )
            noti.save()
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
        total_puntos = PuntosObtenidos.objects.filter(
                            usuario__id=context["usuario"].id
                        ).aggregate(total=Sum('puntos'))
        if total_puntos["total"] == None:
            total_puntos["total"] = 0
        context["total_puntos"] = total_puntos["total"]
        context["seguidores_list"] =SeguirUsuario.objects.filter(seguido__id=context["usuario"].id).select_related("seguido","seguidor")
        
        context["seguidores"] =context["seguidores_list"].count()
        
        context["seguidos"] =SeguirUsuario.objects.filter(seguidor__id=context["usuario"].id).count()
        context["favoritos"] =SeguirEvaluacion.objects.filter(usuario__id=context["usuario"].id).count()
        context["total_evaluaciones"] = Evaluacion.objects.filter(user__id=context["usuario"].id).count()
        context["total_intentos_usuario"] = Intento.objects.filter(usuario__id=context["usuario"].id).count()
        return context
    
class SeguidosPerfilView(LoginRequiredMixin,DetailView):
    
    model = User
    login_url = reverse_lazy('users_app:login')
    template_name = 'users/seguidos.html'
    context_object_name = 'usuario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_puntos = PuntosObtenidos.objects.filter(
                            usuario__id=context["usuario"].id
                        ).aggregate(total=Sum('puntos'))
        if total_puntos["total"] == None:
            total_puntos["total"] = 0
        context["total_puntos"] = total_puntos["total"]
        context["seguidos_list"] =SeguirUsuario.objects.filter(seguidor__id=context["usuario"].id).select_related("seguido","seguidor")
        context["seguidos"] =context["seguidos_list"].count()
        context["favoritos"] =SeguirEvaluacion.objects.filter(usuario__id=context["usuario"].id).count()
        context["seguidores"] =SeguirUsuario.objects.filter(seguido__id=context["usuario"].id).count()
        context["total_evaluaciones"] = Evaluacion.objects.filter(user__id=context["usuario"].id).count()
        context["total_intentos_usuario"] = Intento.objects.filter(usuario__id=context["usuario"].id).count()
        return context
    
    
class EvaluacionesFavoritasPerfilView(LoginRequiredMixin,DetailView):
    
    model = User
    login_url = reverse_lazy('users_app:login')
    template_name = 'users/evaluaciones_seguidas.html'
    context_object_name = 'usuario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_puntos = PuntosObtenidos.objects.filter(
                            usuario__id=context["usuario"].id
                        ).aggregate(total=Sum('puntos'))
        if total_puntos["total"] == None:
            total_puntos["total"] = 0
        context["total_puntos"] = total_puntos["total"]
        context["total_puntos"] = total_puntos["total"]
        context["seguidores"] =SeguirUsuario.objects.filter(seguido__id=context["usuario"].id).count()
        context["seguidos"] =SeguirUsuario.objects.filter(seguidor__id=context["usuario"].id).count()
        context["favoritos_list"] =SeguirEvaluacion.objects.filter(usuario__id=context["usuario"].id).select_related("evaluacion","usuario","evaluacion__subcategoria","evaluacion__subcategoria__categoria")
        context["favoritos"] =context["favoritos_list"].count()
        context["total_evaluaciones"] = Evaluacion.objects.filter(user__id=context["usuario"].id).count()
        context["total_intentos_usuario"] = Intento.objects.filter(usuario__id=context["usuario"].id).count()
        return context

class VerIntentos(LoginRequiredMixin,DetailView):
    model = Evaluacion
    template_name = "users/ver_intentos.html"
    login_url = reverse_lazy('users_app:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        intentos = Intento.objects.filter(
            usuario__id=self.request.user.id,evaluacion__id=self.kwargs["pk"]
            ).annotate(correctas=Count('preguntas',filter=Q(preguntas__correcto=True))).order_by('-hora_inicio')
        
        context["usuario"] = self.request.user
        context["intentos"] = intentos
        
 
        return context


class RankingsListView(ListView):
    model = User
    template_name = "rankings/rangos.html"
    context_object_name = "ranking_user"
    
    
    def get_queryset(self):
        
        queryset = super(RankingsListView, self).get_queryset()
        try:
            categoria = self.request.GET["categoria"]
            if categoria == "Global":
                raise Exception
            queryset = User.objects.filter(intentos__evaluacion__subcategoria__categoria__nombre__contains=categoria
                ).annotate(
            total_evas=Count('intentos__evaluacion',distinct=True),
            aprobadas=Count('intentos__evaluacion',distinct=True,filter=Q(intentos__aprobado=True)),
            perfectas=Count('intentos__evaluacion',distinct=True,filter=Q(intentos__puntuacion=100)),
            puntos_total=Coalesce(
                Sum("usuario_puntos__puntos"),
                Value(0))
            ).order_by("-puntos_total")

            contador = 1
            for x in queryset:

                if self.request.user.username == x.username:

                    self.request.session["rango"] = contador
                    break
                else:
                    self.request.session["rango"] = "-"
                
                contador += 1

        except:
            queryset = User.objects.annotate(
            total_evas=Count('intentos__evaluacion',distinct=True),
            aprobadas=Count('intentos__evaluacion',distinct=True,filter=Q(intentos__aprobado=True)),
            perfectas=Count('intentos__evaluacion',distinct=True,filter=Q(intentos__puntuacion=100)),
            puntos_total=Coalesce(Sum("usuario_puntos__puntos"),Value(0))
            ).order_by("-puntos_total",'username')
            contador = 1
            for x in queryset:
                if self.request.user.username == x.username:
                    self.request.session["rango"] = contador
                
                contador += 1
        
        return queryset[:20]
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:

            categoria = self.request.GET["categoria"]
            if categoria == "Global":
                raise Exception
            context["cat_actual"] = categoria
            qs = User.objects.filter(
                id=self.request.user.id,intentos__evaluacion__subcategoria__categoria__nombre=categoria
                ).annotate(
                    total_evas=Count('intentos__evaluacion',distinct=True),
                    aprobadas=Count('intentos__evaluacion',distinct=True,filter=Q(intentos__aprobado=True)),
                    perfectas=Count('intentos__evaluacion',distinct=True,filter=Q(intentos__puntuacion=100)),
                    puntos_total=Coalesce(
                            Sum("usuario_puntos__puntos"), Value(0))
                ).first()

        except:
            context["cat_actual"] = "Global"
            qs = User.objects.filter(
                id=self.request.user.id
                ).annotate(
                    total_evas=Count('intentos__evaluacion',distinct=True),
                    aprobadas=Count('intentos__evaluacion',distinct=True,filter=Q(intentos__aprobado=True)),
                    perfectas=Count('intentos__evaluacion',distinct=True,filter=Q(intentos__puntuacion=100)),
                    puntos_total=Coalesce(Sum("usuario_puntos__puntos"),Value(0))
                ).first()
        
                
        context["usuario_actual"] = qs
        try:
            context["rango"] = self.request.session["rango"]
        except:
            context["rango"] = ""
        
        context["categorias"] = Categoria.objects.all()
        
        
        return context


class IntentosUsuario(DetailView):
    model = User
    template_name = "users/intentos_usuario.html"
    context_object_name = 'usuario'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        busqueda = self.request.GET.get("kword",'')
        categoria = self.request.GET.get("categoria",'')
        orden = self.request.GET.get("orden",'')
        
        orden = establecer_orden(orden)
        
        evaluaciones = Evaluacion.objects.filter(intentos__usuario__id=self.kwargs["pk"],
                                                 subcategoria__categoria__nombre__contains=categoria,
                                                 nombre__icontains = busqueda
            ).annotate(max_p=Max('intentos__puntuacion',filter=Q(intentos__usuario__id=self.kwargs["pk"])),
                tot_intentos=Count('intentos__id',filter=Q(intentos__usuario__id=self.kwargs["pk"])),
                restantes=F('intentos_permitidos')- Count('intentos__id',filter=Q(intentos__usuario__id=self.kwargs["pk"])),
                ultimo_intento = Max('intentos__hora_inicio')
                ).select_related('subcategoria','subcategoria__categoria').order_by(orden)
        
        context["total_intentos_usuario"] = Intento.objects.filter(usuario__id=context["usuario"].id).count()
        p = Paginator(evaluaciones,5) 
        page_number = self.request.GET.get('page')
        page_obj = p.get_page(page_number)

        context["page_obj"] = page_obj
        total_puntos = PuntosObtenidos.objects.filter(
                            usuario__id=context["usuario"].id
                        ).aggregate(total=Sum('puntos'))
        if total_puntos["total"] == None:
            total_puntos["total"] = 0
        context["total_puntos"] = total_puntos["total"]
        
        context["seguidores"] =SeguirUsuario.objects.filter(seguido__id=context["usuario"].id).count()
        context["seguidos"] =SeguirUsuario.objects.filter(seguidor__id=context["usuario"].id).count()
        context["favoritos"] =SeguirEvaluacion.objects.filter(usuario__id=context["usuario"].id).count()
        context["total_evaluaciones"] = Evaluacion.objects.filter(user__id=context["usuario"].id).count()
        categorias = Categoria.objects.all().values('nombre')
        context["categorias"] = categorias
        context["kword"] = busqueda
        context["orden"] = orden
        context["cat_sel"] = categoria
        path = self.request.get_full_path().replace(self.request.path,"")
        try:
            index = path.index("&pa")
            path = path[:index]
        except:
            pass
        context["path_query"] = path
                
        return context
    
class EvaluacionesUsuario(DetailView):
    model = User
    template_name = "users/evaluaciones_usuario.html"
    context_object_name = 'usuario'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        kword = self.request.GET.get("kword","")
        ord_sel= self.request.GET.get("orden","")
        cat_sel= self.request.GET.get("categoria","")

        orden = establecer_orden_eva(ord_sel)
        if self.request.user.id == context["usuario"].id:

            eva_propias = Evaluacion.objects.filter(
                user__id=context["usuario"].id,subcategoria__categoria__nombre__contains=cat_sel,nombre__icontains = kword
                ).annotate(tot_valoraciones=Count('valorar', distinct=True),
                        prom_valoraciones=Avg('valorar__valor'),
                        tot_seguidores=Count('seguir', distinct=True),
                        tot_intentos=Count('intentos', distinct=True),
                        prom_intentos=Avg('intentos__puntuacion'),
                        total_preguntas=Count('preguntas', distinct=True),
                        total_aprobados=Count('intentos__id',filter=Q(intentos__aprobado=True), distinct=True),
                        aprobados= Case(When(tot_intentos=0,then=0),default=Count('intentos__id',filter=Q(intentos__aprobado=True))*100/Count('intentos'),output_field=FloatField(),distinct=True)
                                                                                                     
                        ).order_by(orden).select_related("user","subcategoria","subcategoria__categoria").defer("descripcion","requisitos_minimos")
        else:
            eva_propias = Evaluacion.objects.filter(
                user__id=context["usuario"].id,publico=True,subcategoria__categoria__nombre__contains=cat_sel,nombre__icontains = kword
                ).annotate(tot_valoraciones=Count('valorar', distinct=True),
                        prom_valoraciones=Avg('valorar__valor'),
                        tot_seguidores=Count('seguir', distinct=True),
                        tot_intentos=Count('intentos', distinct=True),
                        prom_intentos=Avg('intentos__puntuacion'),
                        total_preguntas=Count('preguntas', distinct=True),
                        total_aprobados=Count('intentos__id',filter=Q(intentos__aprobado=True), distinct=True),
                        aprobados= Case(When(
                            tot_intentos=0,
                            then=0),
                            default=Count('intentos__id',
                            filter=Q(intentos__aprobado=True))*100/Count('intentos'),
                            output_field=FloatField(), 
                            distinct=True)

                        ).order_by(orden).select_related("user","subcategoria","subcategoria__categoria").defer("descripcion","requisitos_minimos")
        
        p = Paginator(eva_propias,10) 
        page_number = self.request.GET.get('page')
        page_obj = p.get_page(page_number)

        context["page_obj"] = page_obj
        
        total_puntos = PuntosObtenidos.objects.filter(
                            usuario__id=context["usuario"].id
                        ).aggregate(total=Sum('puntos'))
        if total_puntos["total"] == None:
            total_puntos["total"] = 0
        context["total_puntos"] = total_puntos["total"]  
        
        categorias = Categoria.objects.all().values('nombre')
        context["categorias"] = categorias
        
        context["kword"] = kword
        context["orden"] = ord_sel
        context["cat_sel"] = cat_sel
        path = self.request.get_full_path().replace(self.request.path,"")
        try:
            index = path.index("&pa")
            path = path[:index]
        except:
            pass
        context["path_query"] = path
        
        context["seguidores"] =SeguirUsuario.objects.filter(seguido__id=context["usuario"].id).count()
        context["seguidos"] =SeguirUsuario.objects.filter(seguidor__id=context["usuario"].id).count()
        context["favoritos"] =SeguirEvaluacion.objects.filter(usuario__id=context["usuario"].id).count()
        context["total_evaluaciones"] = Evaluacion.objects.filter(user__id=context["usuario"].id).count()
        context["total_intentos_usuario"] = Intento.objects.filter(usuario__id=context["usuario"].id).count()
               
        
        return context
        

class PoliticaPrivacidad(TemplateView):
    
    template_name = "home/politica.html"

ListAPIView

class NotificacionListView(ListAPIView):
    
    serializer_class = NotificacionSerializer

    def get_queryset(self):
        return Notificacion.objects.filter(usuario__id=self.request.user.id).order_by('-created_at')

class DeleteNotificacionAPIView(DestroyAPIView):

    serializer_class = NotificacionSerializer
    queryset = Notificacion.objects.all()


# class ActualizarRangos(TemplateView):
#     template_name = "home/act_rangos.html"
    
#     def post(self, request, *args, **kwargs):

#         usuarios = User.objects.all()
#         lista_usuarios = []
#         for x in usuarios:
#             puntaje = PuntosObtenidos.objects.filter(
#                         usuario__id=x.id
#                         ).aggregate(total=Sum('puntos'))
#             if puntaje["total"] == None:
#                 puntaje["total"] = 0
#             rango = ranquear_usuario(puntaje["total"])
#             x.rango = rango
#             lista_usuarios.append(x)
        
#         User.objects.bulk_update(lista_usuarios,['rango'])
            
#         return HttpResponseRedirect(
#             reverse(
#                 'users_app:inicio'
#             )
#         ) 
    