from django.shortcuts import render
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView
from django.db.models import Avg, Count, F, Max, Prefetch, Q, Value
from apps.intentos.models import Intento
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.urls import reverse, reverse_lazy

#Thirdparty
from rest_framework.generics import ListAPIView
#modulos propios
from apps.evaluaciones.models import CalificarDificultad, Categoria, Evaluacion, Opcion, Pregunta, SeguirEvaluacion, SubCategoria, ValorarEvaluacion
from apps.evaluaciones.serializers import CategoriaSerializer, EvaluacionSerializer
from django.core.files import File
import re

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models.functions import Coalesce
from django.utils import timezone
from apps.users.models import Notificacion
User = get_user_model()


def establecer_orden(orden):
    if orden == "populares":
        order="-favoritos"
    elif orden == "valorados":
        order="-valoracion"
    elif orden == "faciles":
        order="dificultad_ponderada"
    elif orden == "dificiles":
        order="-dificultad_ponderada"
    else:
        order = "-created_at"
    return order


# Create your views here.
class CrearEvaluacionView(LoginRequiredMixin,CreateView):
    model = Evaluacion
    template_name = "evaluaciones/crear_eva.html"
    fields = ('nombre','descripcion','publico','subcategoria','imagen','puntaje_minimo','cant_preguntas','intentos_permitidos','tiempo_limite','dificultad','requisitos_minimos')
    
    def post(self, request, *args, **kwargs):
        
        
        if request.POST.get("publico") == "on":
            publico = True
        else:
            publico = False
        evaluacion = Evaluacion.objects.create(
            nombre=request.POST.get("nombre"),
            descripcion = request.POST.get("descripcion"),
            requisitos_minimos = request.POST.get("requisitos_minimos"),
            user = self.request.user,
            subcategoria = SubCategoria.objects.get(nombre=request.POST.get("subcategoria")),
            publico = publico,
            puntaje_minimo= request.POST.get("puntaje_minimo"),
            cant_preguntas= request.POST.get("cant_preguntas"),
            intentos_permitidos= request.POST.get("intentos_permitidos"),
            tiempo_limite= request.POST.get("tiempo_limite"),
            dificultad= request.POST.get("dificultad")
             
        )
        try:
            evaluacion.imagen = request.FILES["imagen"]
        except:
            pass
        evaluacion.save()
        ultimo_letras = str(list(request.POST.keys())[-1])
        print("ultima_pregunta",ultimo_letras)
        ultima_pregunta = int(re.search(r'(\d+)', ultimo_letras).group(1))
        print(ultima_pregunta)
        print("numero ultima pregunta", ultima_pregunta)

        for pregunta in range(1,(ultima_pregunta+1)):
            texto_busqueda = f"pregunta-{pregunta}-"
       
            res = dict(filter(lambda item: texto_busqueda in item[0], request.POST.items()))
            print("el resultado por pregunta", res)
            opcion_correcta_key = dict(filter(lambda x:"correcta" in x[0], res.items()))
            print("la llave de la opcion correcta", opcion_correcta_key)
            asd = list(opcion_correcta_key)[0] 
            print("asd", asd)
            res.pop(asd)
            opcion_correcta = int(re.findall(r'\d+', asd)[-1])
            print("opcion correcta", opcion_correcta)
            registros = list(res.values())
            print("el registro", registros)
            pregunta = Pregunta.objects.create(
                descripcion=request.POST[f"pregunta-{pregunta}"],
                evaluacion=Evaluacion.objects.get(id=evaluacion.id)
            )
            pregunta.save()
            for i in range(1,len(registros)+1):
                if opcion_correcta != i:
                    opcion = Opcion.objects.create(
                        texto = registros[i-1],
                        correcta = False,
                        pregunta = Pregunta.objects.get(id=pregunta.id)
                    )
                    opcion.save()
                else:
                    opcion = Opcion.objects.create(
                        texto = registros[i-1],
                        correcta = True,
                        pregunta = Pregunta.objects.get(id=pregunta.id)
                    )
                    opcion.save()
                    
        messages.success(self.request,"Evaluación creada con exito")
        return HttpResponseRedirect(
            reverse(
                'users_app:detalleusuario',kwargs={'slug': self.request.user.slug}
            )
        )

class EvaluacionesListView(ListView):
    model = Evaluacion
    template_name = "evaluaciones/lista.html"
    context_object_name = "evaluaciones"
    paginate_by = 10
    
    def get_queryset(self):
        kword = self.request.GET.get("kword",'')
        categoria = self.request.GET.get("categoria",'')
        if categoria == "todos":
            categoria = ""
                    
        orden = self.request.GET.get("orden",'')
        orden = establecer_orden(orden)
        
        
        lista = Evaluacion.objects.filter(publico=True,subcategoria__categoria__nombre__contains=categoria,nombre__icontains = kword).annotate(
            favoritos=Count('seguir',distinct=True),
            valoracion=Coalesce(Avg('valorar__valor',distinct=True),Value(0))).select_related('subcategoria','subcategoria__categoria').order_by(orden)
        
        return lista

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            cat_sel= self.request.GET["categoria"]
            context["cat_sel"] = cat_sel
            self.request.session["cat"] = cat_sel
        except:
            context["cat_sel"] = ""
            self.request.session["cat"] = ""
        try:
            ord_sel= self.request.GET["orden"]
            context["ord_sel"] = ord_sel
        except:
            context["ord_sel"] = ""
        try:
            kword = self.request.GET["kword"]
            context["kword"] = kword
        except:
            context["kword"] = ""
        path = self.request.get_full_path().replace(self.request.path,"")
        try:
            index = path.index("&pa")
            path = path[:index]
        except:
            pass
        context["path_query"] = path
        context["categorias"] = Categoria.objects.all()
        
        return context


class EvaluacionesListAPIView(ListAPIView):
    serializer_class = EvaluacionSerializer
    
    def get_queryset(self):
        
        return Evaluacion.objects.all()
    

class CategoriaListAPIView(ListAPIView):
    serializer_class = CategoriaSerializer

    def get_queryset(self):
        
        return Categoria.objects.all()

class EvaluacionDetailView(DetailView):
    model = Evaluacion
    template_name = "evaluaciones/detalle.html"
    context_object_name = 'evaluacion'
    
    def get_queryset(self):
        
        return Evaluacion.objects.filter(slug=self.kwargs["slug"]).annotate(
            favoritos=Count('seguir',distinct=True),
            valoracion=Avg('valorar__valor',distinct=True)).select_related("user","subcategoria","subcategoria__categoria")
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        #Datos de resumen de la evaluacion...
        aprobados = Intento.objects.filter(
            evaluacion__slug=self.kwargs["slug"]
            ).aggregate(
                aprobados=Count('usuario',filter=Q(aprobado=True),distinct=True),
                total=Count('id'),promedio=Avg('puntuacion')
                )
            
        if aprobados["promedio"] == None:
            aprobados["promedio"] = 0
            
        try:
            porcentaje_aprobados = (aprobados["aprobados"]/aprobados["total"])*100
        except:
            porcentaje_aprobados = 0
        
        #datos del autor de la evaluacion
        user_name = context["evaluacion"].user.username

        
        #confirmar si el usuario ha presentado o no la evaluacion
        user_id =self.request.user.id
        try:
            intento = Intento.objects.filter(evaluacion__id=context["evaluacion"].id,usuario__id=user_id).exists()
        except:
            intento = None
        try:
            calificado = CalificarDificultad.objects.get(evaluacion__id=context["evaluacion"].id,usuario__id=user_id)
        except:
            calificado = None
            
        try:
            aprobado =Intento.objects.get(evaluacion__id=context["evaluacion"].id,usuario__id=user_id,aprobado=True)
        except:
            aprobado = None
        try:
            valoracion =ValorarEvaluacion.objects.get(evaluacion__id=context["evaluacion"].id,usuario__id=user_id)
            valoracion = str(valoracion.valor).replace(",",".")
        except:
            valoracion = None
        
        context["aprobados"] = aprobados
        context["porcentaje_aprobados"] = porcentaje_aprobados
        context["presentada"] = intento
        context["calificado"] = calificado
        context["aprobado"] = aprobado
        context["valoracion"] = valoracion
        
        intentos_usuario = Intento.objects.filter(usuario__id=self.request.user.id,evaluacion__slug=self.kwargs["slug"]).aggregate(total=Count('id'),max=Max('puntuacion'))
        context["intentos_restantes"] = context["evaluacion"].intentos_permitidos - intentos_usuario["total"] 
        if intentos_usuario["max"] == None:
            intentos_usuario["max"] = 0
        context["maxima_puntuacion"] = intentos_usuario["max"] 
        
        seguidos = SeguirEvaluacion.objects.filter(usuario__id = self.request.user.id).values_list('evaluacion__id',flat=True)
    
        context["evaluaciones_seguidas"] = seguidos
        return context

class CalificarDificultadEva(LoginRequiredMixin,View):
    
    def post(self,request,*args,**kwargs):
        
        puntaje =  float(request.POST.get("rango"))
        evaluacion = Evaluacion.objects.get(id=self.kwargs["pk"])
        usuario = self.request.user
        
        calificacion = CalificarDificultad.objects.create(evaluacion=evaluacion,usuario=usuario,dificultad=puntaje)
        calificacion.save()
        
        #actualizando la dificultad ponderada de la evaluación
        promedio_usuarios = CalificarDificultad.objects.filter(evaluacion__id=self.kwargs["pk"]).aggregate(promedio=Avg("dificultad"))
        
        evaluacion.dificultad_ponderada = (evaluacion.dificultad*0.3)+(promedio_usuarios["promedio"]*0.7)
        evaluacion.save(update_fields=["dificultad_ponderada"])
        
        t = timezone.now().strftime('%d %B %Y %H:%M')
            
        noti = Notificacion.objects.create(
            usuario = evaluacion.user,
            usuario_notificacion = usuario,
            mensaje = f"{usuario} ha calificado la dificultad de tu evaluación: {evaluacion.nombre}. El {t}"
            )
        noti.save()
        
        messages.success(self.request,"Calificación guardada con exito")
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))
        

class SeguirEvaluacionView(LoginRequiredMixin,View):
    
    login_url = reverse_lazy('users_app:login')
    
    def post(self,request,*args,**kwargs):
        usuario = self.request.user
        evaluacion = Evaluacion.objects.get(id=self.kwargs['evaluacion'])
        try:
            SeguirEvaluacion.objects.create(
                usuario = usuario,
                evaluacion = evaluacion,
            )
            t = timezone.now().strftime('%d %B %Y %H:%M')
            
            noti = Notificacion.objects.create(
                usuario = evaluacion.user,
                usuario_notificacion = usuario,
                mensaje = f"{usuario} ha comenzado a seguir tu evaluación: {evaluacion.nombre}. El {t}"
                )
            noti.save()
        except:
            SeguirEvaluacion.objects.get(
                usuario = usuario,
                evaluacion = evaluacion,
            ).delete()

        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))   
    
class ValorarEvaView(LoginRequiredMixin,View):
    login_url = reverse_lazy('users_app:login')
    
    def post(self,request,*args,**kwargs):
        
        valoracion =  float(request.POST.get("rating"))
        evaluacion = Evaluacion.objects.get(id=self.kwargs["pk"])
        usuario = self.request.user
        try:
            valoracion_eva =ValorarEvaluacion.objects.get(evaluacion=evaluacion,usuario=usuario)
            valoracion_eva.valor = valoracion
            valoracion_eva.save()
            
        except:
                  
            valoracion_eva  = ValorarEvaluacion.objects.create(evaluacion=evaluacion,usuario=usuario,valor=valoracion)
            t = timezone.now().strftime('%d %B %Y %H:%M')
            
            noti = Notificacion.objects.create(
                usuario = evaluacion.user,
                usuario_notificacion = usuario,
                mensaje = f"{usuario} ha valorado tu evaluación: {evaluacion.nombre}. El {t}"
                )
            noti.save()
        
        messages.success(self.request,"Valoración guardada con exito")
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

class EditarEvaluacionView(LoginRequiredMixin,UpdateView):
    model= Evaluacion
    fields = ('nombre','descripcion','subcategoria','publico','imagen','puntaje_minimo','cant_preguntas','intentos_permitidos','tiempo_limite','dificultad','requisitos_minimos')
    template_name = "evaluaciones/editarevaluacion.html"
    login_url = reverse_lazy('users_app:login')
    
    def form_valid(self, form):
        
        subcategoria = SubCategoria.objects.get(nombre=form.cleaned_data["subcategoria"])
        form.subcategoria = subcategoria
        promedio_usuarios = CalificarDificultad.objects.filter(evaluacion__id=self.kwargs["pk"]).aggregate(promedio=Avg("dificultad"))
        if promedio_usuarios["promedio"] == None:
            dificultad_ponderada = form.cleaned_data["dificultad"]
        else:
            dificultad_ponderada = (form.cleaned_data["dificultad"]*0.3)+(promedio_usuarios["promedio"]*0.7)
        x = form.save()
        x.dificultad_ponderada = dificultad_ponderada
        x.save()
        
        return super().form_valid(form)
    
    def get_success_url(self):
        
        messages.success(self.request,"Cambios realizados con exito")
        
        return reverse(
                'users_app:detalleusuario',kwargs={'slug': self.request.user.slug}
            )


class VerPreguntasEvaluacion(LoginRequiredMixin,DetailView):
    
    model = Evaluacion
    template_name = "evaluaciones/ver_preguntas.html"
    context_object_name = "evaluacion"
    
    def get_queryset(self):
        
        lista = Evaluacion.objects.filter(id=self.kwargs["pk"]).select_related("user")
        return lista
    
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        
        context["preguntas"] = Pregunta.objects.filter(evaluacion__id=self.kwargs["pk"]).prefetch_related(Prefetch('opciones'))

        return context
        
#TODO: Probar que esto haya quedado bien cuando ya pueda agregar preguntas
class BorrarPregunta(LoginRequiredMixin,View):
    
    def post(self,request,*args,**kwargs):
                
        pregunta = Pregunta.objects.get(id=self.kwargs["pk"])
        evaluacion = pregunta.evaluacion.id
        
        cant_preguntas = pregunta.evaluacion.cant_preguntas
        total_preguntas = Pregunta.objects.filter(evaluacion__id= evaluacion).count()

        if cant_preguntas > total_preguntas-1:
            messages.error(request,"NO tienes suficientes preguntas")
            return HttpResponseRedirect(
                reverse(
                    'exams_app:verpreguntaseva',kwargs={'pk': evaluacion}
                )
            )
        
        
        if self.request.user == pregunta.evaluacion.user:
            pregunta.delete()

        return HttpResponseRedirect(
            reverse(
                'exams_app:verpreguntaseva',kwargs={'pk': evaluacion}
            )
        )

class EditarPregunta(LoginRequiredMixin,UpdateView):
    model= Pregunta
    fields = ('descripcion',)
    template_name = "evaluaciones/editarpregunta.html"
    login_url = reverse_lazy('users_app:login')
    
    def form_valid(self, form):
         
        lista = list(self.request.POST.items())
        opcion_correcta_key = list(filter(lambda x:"correcta" in x[0], lista))
        indice_correcta = lista.index(opcion_correcta_key[0])
        lista.pop(indice_correcta)
        opcion_correcta = int(re.findall(r'\d+', opcion_correcta_key[0][0])[-1])+1


        opciones = Opcion.objects.filter(pregunta__id=self.kwargs["pk"]).delete()
        for i in range(2,len(lista)):

            if opcion_correcta != i:
                opcion = Opcion.objects.create(
                    texto = lista[i][1],
                    correcta = False,
                    pregunta = Pregunta.objects.get(id=self.kwargs["pk"])
                )
                opcion.save()
            else:
                opcion = Opcion.objects.create(
                    texto = lista[i][1],
                    correcta = True,
                    pregunta = Pregunta.objects.get(id=self.kwargs["pk"])
                )
                opcion.save()   
        
        
        return super().form_valid(form)
            
    def get_success_url(self):
        
        messages.success(self.request,"Cambios realizados con exito")
        evaluacion = Evaluacion.objects.get(preguntas__id=self.kwargs["pk"])
        
        return reverse(
                'exams_app:verpreguntaseva',kwargs={'pk': evaluacion.id}
            )
        
class AgregarPreguntas(LoginRequiredMixin,DetailView):
    model = Evaluacion
    template_name = "evaluaciones/agregar_pregunta.html"
    login_url = reverse_lazy('users_app:login')

    def post(self,request,*args,**kwargs):
        
        lista = list(self.request.POST.items())
        opcion_correcta_key = list(filter(lambda x:"correcta" in x[0], lista))
        indice_correcta = lista.index(opcion_correcta_key[0])
        print(lista)
        pregunta = Pregunta.objects.create(
            descripcion = lista[1][1],
            evaluacion = Evaluacion.objects.get(id=self.kwargs["pk"])
        )
        pregunta.save()
        lista.pop(indice_correcta)
        opcion_correcta = int(re.findall(r'\d+', opcion_correcta_key[0][0])[-1])+1


        opciones = Opcion.objects.filter(pregunta__id=self.kwargs["pk"]).delete()
        for i in range(2,len(lista)):

            if opcion_correcta != i:
                opcion = Opcion.objects.create(
                    texto = lista[i][1],
                    correcta = False,
                    pregunta = Pregunta.objects.get(id=pregunta.id)
                )
                opcion.save()
            else:
                opcion = Opcion.objects.create(
                    texto = lista[i][1],
                    correcta = True,
                    pregunta = Pregunta.objects.get(id=pregunta.id)
                )
                opcion.save()   
        
        messages.success(request,"Pregunta guardada y agregada con exito")
        return HttpResponseRedirect(
            reverse(
                'users_app:detalleusuario',kwargs={'slug': self.request.user.slug}
            )
        )

class VerInteracciones(LoginRequiredMixin,DetailView):
    model = Evaluacion
    template_name = "evaluaciones/ver_interacciones.html"
    login_url = reverse_lazy('users_app:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        usuarios = User.objects.filter(Q
            (intentos__evaluacion__id=self.kwargs["pk"]) | Q(valorar__evaluacion__id=self.kwargs["pk"]) | Q(favoritos__evaluacion__id=self.kwargs["pk"]) | Q(dificultad__evaluacion__id=self.kwargs["pk"])
            ).annotate(
                max_puntaje=Max('intentos__puntuacion',filter=Q(intentos__evaluacion__id=self.kwargs["pk"])),
                total_intentos=Count('intentos',filter=Q(intentos__evaluacion__id=self.kwargs["pk"]),distinct=True),
                valoracion=Avg('valorar__valor',filter=Q(valorar__evaluacion__id=self.kwargs["pk"])),
                seguido=Count("favoritos",filter=Q(favoritos__evaluacion__id=self.kwargs["pk"]),distinct=True),
                dificul = Avg("dificultad__dificultad",filter=Q(dificultad__evaluacion__id=self.kwargs["pk"]))
            )
        context["usuarios"] = usuarios
        return context
    

class VerIntentosMiEvaluacion(LoginRequiredMixin,DetailView):
    model = Evaluacion
    template_name = "evaluaciones/ver_intentos.html"
    login_url = reverse_lazy('users_app:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        usuario = User.objects.get(id=self.kwargs["usuario"])
        
        intentos = Intento.objects.filter(
            usuario__id=self.kwargs["usuario"],evaluacion__id=self.kwargs["pk"]
            ).annotate(correctas=Count('preguntas',filter=Q(preguntas__correcto=True)))
        
        context["usuario"] = usuario
        context["intentos"] = intentos
        
        return context
    