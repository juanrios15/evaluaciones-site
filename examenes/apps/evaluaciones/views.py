from django.shortcuts import render
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView
from django.db.models import Avg, Count, Q
from apps.intentos.models import Intento
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.urls import reverse, reverse_lazy

#Thirdparty
from rest_framework.generics import ListAPIView
#modulos propios
from apps.evaluaciones.models import CalificarDificultad, Categoria, Evaluacion, Opcion, Pregunta, SeguirEvaluacion, SubCategoria, ValorarEvaluacion
from apps.evaluaciones.serializers import CategoriaSerializer
from django.core.files import File
import re

# Create your views here.
class CrearEvaluacionView(LoginRequiredMixin,CreateView):
    model = Evaluacion
    template_name = "evaluaciones/crear_eva.html"
    fields = ('nombre','descripcion','publico','subcategoria','imagen','puntaje_minimo','cant_preguntas','intentos_permitidos','tiempo_limite','dificultad','requisitos_minimos')
    
    def post(self, request, *args, **kwargs):
        
        

        evaluacion = Evaluacion.objects.create(
            nombre=request.POST.get("nombre"),
            descripcion = request.POST.get("descripcion"),
            requisitos_minimos = request.POST.get("requisitos_minimos"),
            user = self.request.user,
            subcategoria = SubCategoria.objects.get(nombre=request.POST.get("subcategoria")),
            publico = request.POST.get("publico"),
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
        ultima_pregunta = int(re.findall(r'^\D*(\d+)', ultimo_letras)[0])

        for pregunta in range(1,(ultima_pregunta+1)):
            texto_busqueda = f"pregunta-{pregunta}"
            res = dict(filter(lambda item: texto_busqueda in item[0], request.POST.items()))
            print(res)
            opcion_correcta_key = dict(filter(lambda x:"correcta" in x[0], res.items()))
            asd = list(opcion_correcta_key)[0] 
            res.pop(asd)
            opcion_correcta = int(re.findall(r'\d+', asd)[-1])
            registros = list(res.values())

            pregunta = Pregunta.objects.create(
                descripcion=registros[0],
                evaluacion=Evaluacion.objects.get(id=evaluacion.id)
            )
            pregunta.save()
            for i in range(1,len(registros[1:])+1):
                if opcion_correcta != i:
                    opcion = Opcion.objects.create(
                        texto = registros[i],
                        correcta = False,
                        pregunta = Pregunta.objects.get(id=pregunta.id)
                    )
                    opcion.save()
                else:
                    opcion = Opcion.objects.create(
                        texto = registros[i],
                        correcta = True,
                        pregunta = Pregunta.objects.get(id=pregunta.id)
                    )
                    opcion.save()
                    
            

        
        return super().post(request, *args, **kwargs)

class EvaluacionesListView(ListView):
    model = Evaluacion
    template_name = "evaluaciones/lista.html"
    context_object_name = "evaluaciones"
    
    def get_queryset(self):

        lista = Evaluacion.objects.all().annotate(preguntas_count=Count('preguntas'))
        return lista

class CategoriaListAPIView(ListAPIView):
    serializer_class = CategoriaSerializer

    def get_queryset(self):
        return Categoria.objects.all()

class EvaluacionDetailView(DetailView):
    model = Evaluacion
    template_name = "evaluaciones/detalle.html"
    context_object_name = 'evaluacion'
    
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
        user_name = Evaluacion.objects.get(slug =self.kwargs["slug"]).user.username
        evaluaciones_autor = Evaluacion.objects.filter(user__username=user_name).aggregate(evaluaciones=Count('id'))
        
        #confirmar si el usuario ha presentado o no la evaluacion
        user_id =self.request.user.id
        try:
            intento = Intento.objects.filter(evaluacion__slug=self.kwargs["slug"],usuario__id=user_id).exists()
        except:
            intento = None
        try:
            calificado = CalificarDificultad.objects.get(evaluacion__slug=self.kwargs["slug"],usuario__id=user_id)
        except:
            calificado = None
            
        try:
            aprobado =Intento.objects.get(evaluacion__slug=self.kwargs["slug"],usuario__id=user_id,aprobado=True)
        except:
            aprobado = None
        
        seguidores = SeguirEvaluacion.objects.filter(evaluacion__slug=self.kwargs["slug"]).aggregate(cantidad=Count("id"))
        
        try:
            valoracion = ValorarEvaluacion.objects.get(evaluacion__slug=self.kwargs["slug"],usuario__id=user_id).valor
        except:
            valoracion = 3.0
        
        promedio_valoracion = ValorarEvaluacion.objects.filter(evaluacion__slug=self.kwargs["slug"]).aggregate(promedio=Avg('valor'))
        if promedio_valoracion["promedio"]==None:
            promedio_valoracion["promedio"] = 0 
        
        context["aprobados"] = aprobados
        context["porcentaje_aprobados"] = porcentaje_aprobados
        context["autor"] = evaluaciones_autor
        context["presentada"] = intento
        context["calificado"] = calificado
        context["aprobado"] = aprobado
        context["seguidores"] = seguidores
        context["valoracion"] = float(valoracion)
        context["promedio_valoracion"] = promedio_valoracion["promedio"]
        
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
        
        messages.success(self.request,"Calificación guardada con exito")
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))
        

class SeguirEvaluacionView(LoginRequiredMixin,View):
    
    login_url = reverse_lazy('home_app:loginusuario')
    
    def post(self,request,*args,**kwargs):
        usuario = self.request.user
        evaluacion = Evaluacion.objects.get(id=self.kwargs['evaluacion'])
        try:
            SeguirEvaluacion.objects.create(
                usuario = usuario,
                evaluacion = evaluacion,
            )
        except:
            SeguirEvaluacion.objects.get(
                usuario = usuario,
                evaluacion = evaluacion,
            ).delete()

        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))   
    
class ValorarEvaView(LoginRequiredMixin,View):
    login_url = reverse_lazy('home_app:loginusuario')
    
    def post(self,request,*args,**kwargs):
        
        valoracion =  float(request.POST.get("rating"))
        print(valoracion)
        evaluacion = Evaluacion.objects.get(id=self.kwargs["pk"])
        print(evaluacion)
        usuario = self.request.user
        print(usuario)
        try:
            valoracion_eva =ValorarEvaluacion.objects.get(evaluacion=evaluacion,usuario=usuario)
            valoracion_eva.valor = valoracion
            valoracion_eva.save()
        except:
                  
            valoracion_eva  = ValorarEvaluacion.objects.create(evaluacion=evaluacion,usuario=usuario,valor=valoracion)
        
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
        form.save()
        
        return super().form_valid(form)
    
    def get_success_url(self):
        
        messages.success(self.request,"Cambios realizados con exito")
        print(self.request.user)
        
        return reverse(
                'users_app:detalleusuario',kwargs={'slug': self.request.user.slug}
            )


class VerPreguntasEvaluacion(LoginRequiredMixin,DetailView):
    
    model = Evaluacion
    template_name = "evaluaciones/ver_preguntas.html"
    context_object_name = "evaluacion"
    
#TODO: Probar que esto haya quedado bien cuando ya pueda agregar preguntas
class BorrarPregunta(LoginRequiredMixin,View):
    
    def post(self,request,*args,**kwargs):
        
        pregunta = Pregunta.objects.get(id=self.kwargs["pk"])
        evaluacion = pregunta.evaluacion.id
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