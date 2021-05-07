import datetime
from django.utils import timezone

from django.shortcuts import render
from apps.intentos.models import Intento, IntentoPregunta
from django.views.generic import View, TemplateView,DetailView
from apps.evaluaciones.models import Evaluacion, Opcion, Pregunta
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Max

class IniciarIntento(View):
    
    def post(self,request,*args,**kwargs):
        evaluacion_id = self.kwargs["exam"]
        intentos_usuario = Intento.objects.filter(usuario__id=self.request.user.id,evaluacion__id=evaluacion_id).count()
        
        evaluacion = Evaluacion.objects.get(id=evaluacion_id)
        
        if intentos_usuario >evaluacion.intentos_permitidos:
            messages.info(self.request,"Lo sentimos ya has presentado demasiadas veces este examen")
            return HttpResponseRedirect(
            reverse(
                'exams_app:evaluaciones'
            )
        ) 
        print(timezone.now() + datetime.timedelta(minutes=evaluacion.tiempo_limite))
        
        x= Intento(
            evaluacion=evaluacion,
            usuario=self.request.user,
            abierto=True,
            aprobado=False,
            puntuacion=0,
            hora_fin= timezone.now() + datetime.timedelta(minutes=evaluacion.tiempo_limite)
        )
        x.save()
    
        return HttpResponseRedirect(
            reverse(
                'intentos_app:intentopregunta',kwargs={'intento': x.id}
            )
        )     
   
class IntentoView(TemplateView):
    template_name = "intentos/intento.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        intento = Intento.objects.get(id=self.kwargs["intento"])
        evaluacion = Evaluacion.objects.get(id=intento.evaluacion.id)
        cant_preguntas = evaluacion.cant_preguntas
        context["evaluacion"] = evaluacion
        
        context['preguntas'] = Pregunta.objects.filter(evaluacion__id=evaluacion.id).order_by('?')[:cant_preguntas]
        context['intento'] = intento
        context['ahora'] = timezone.now()
        return context
    
    def post(self,request,*args,**kwargs):
        evaluacion= self.get_context_data()["evaluacion"]
        items = request.POST.dict()
        del items["csrfmiddlewaretoken"]
        all_intentos = []
        acierto = 0
        for x in items:
            pregunta = Pregunta.objects.get(id=x)
            opcion = Opcion.objects.get(id=items[x])
            correcto = opcion.correcta
            
            if correcto == True:
                acierto +=1
            
            intento_pregunta = IntentoPregunta(
                pregunta = pregunta,
                opcion = opcion,
                correcto = correcto
            )
            all_intentos.append(intento_pregunta)
        
        IntentoPregunta.objects.bulk_create(all_intentos)
        
        dificultad = evaluacion.dificultad_ponderada
        
        intento = Intento.objects.get(id=self.kwargs["intento"]) 
        intento.puntuacion = (acierto/evaluacion.cant_preguntas)*100 
        puntos_obtenidos=0
        if intento.puntuacion >= evaluacion.puntaje_minimo:
            intento.aprobado = True
            
            max_previo = Intento.objects.filter(
                    usuario__id=intento.usuario.id,
                    evaluacion__id=evaluacion.id
                    ).exclude(
                        id=intento.id
                    ).aggregate(max_puntaje=Max('puntuacion'),max_puntos=Max('puntos'))
            print(max_previo["max_puntos"])
            if max_previo["max_puntaje"]==None:
                max_previo["max_puntaje"] = 0
            if max_previo["max_puntos"]==None:
                max_previo["max_puntos"] = 0
                
            if intento.puntuacion > max_previo["max_puntaje"]:
                if intento.puntuacion == 100:
                    puntos_obtenidos =dificultad*0.2*intento.puntuacion
                    agregar_puntos = puntos_obtenidos - max_previo["max_puntos"]
                    print("puntos_obtenidos",puntos_obtenidos)
                    print("agregar_puntos",agregar_puntos)
                    intento.usuario.puntaje_total += agregar_puntos
                else:
                    puntos_obtenidos =dificultad*0.1*intento.puntuacion
                    agregar_puntos = puntos_obtenidos - max_previo["max_puntos"]
                    intento.usuario.puntaje_total += agregar_puntos
        intento.puntos = puntos_obtenidos
        intento.abierto = False
        intento.hora_fin = timezone.now()
        intento.save()
        intento.usuario.save()
        
        return HttpResponseRedirect(
                reverse(
                    'intentos_app:resultadointento',kwargs={'pk': intento.id}
                )
            )

class ResultadoIntento(DetailView):
    model = Intento
    template_name = "intentos/resultadointento.html"
    context_object_name= "intento"

