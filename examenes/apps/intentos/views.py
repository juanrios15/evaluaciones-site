import datetime
from django.utils import timezone

from django.shortcuts import render
from django.views.generic import View, TemplateView,DetailView
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Max, Sum
from django.contrib.auth.mixins import LoginRequiredMixin 

from apps.users.models import Notificacion 
from apps.evaluaciones.models import Evaluacion, Opcion, Pregunta
from apps.intentos.models import Intento, IntentoPregunta, PuntosObtenidos

def ranquear_usuario(puntos):

    rango = ""
    if puntos < 80:
        rango = "Practicante"
    elif puntos < 150:
        rango = "Principiante I"
    elif puntos < 200:
        rango = "Principiante II"
    elif puntos < 300:
        rango = "Intermedio I"
    elif puntos < 400:
        rango = "Intermedio II"
    elif puntos < 500:
        rango = "Avanzado I"
    elif puntos < 650:
        rango = "Avanzado II"
    elif puntos < 850:
        rango = "Master I"
    elif puntos < 950:
        rango = "Master II"
    elif puntos > 950:
        rango = "Master III"
        
    return rango
        

class IniciarIntento(LoginRequiredMixin,View):
    login_url = reverse_lazy('users_app:login')
    
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
        
        x= Intento.objects.create(
            evaluacion=evaluacion,
            usuario=self.request.user,
            aprobado=False,
            puntuacion=0,
        )
        x.hora_fin = x.hora_inicio + datetime.timedelta(minutes=evaluacion.tiempo_limite)
        x.save()
        preguntas_query = Pregunta.objects.values_list('id').filter(evaluacion__id=evaluacion.id).order_by('?')[:evaluacion.cant_preguntas]
        preguntas = list(preguntas_query)
        text_preguntas = f"preguntas-{x.id}"
        self.request.session[text_preguntas] = [int(x[0]) for x in preguntas]
        return HttpResponseRedirect(
            reverse(
                'intentos_app:intentopregunta',kwargs={'intento': x.id}
            )
        )     
   
class IntentoView(LoginRequiredMixin,TemplateView):
    template_name = "intentos/intento.html"
    login_url = reverse_lazy('users_app:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        intento = Intento.objects.get(id=self.kwargs["intento"])
        cant_preguntas = intento.evaluacion.cant_preguntas
        context["evaluacion"] = intento.evaluacion
        text_preguntas = f"preguntas-{intento.id}"
        
        try:
            context['preguntas'] = Pregunta.objects.filter(evaluacion__id=intento.evaluacion.id,id__in=self.request.session[text_preguntas])
        except:
            context["preguntas"] = 0
        context['intento'] = intento
        context['ahora'] = timezone.now()
        return context
    
    def post(self,request,*args,**kwargs):

        intento = Intento.objects.get(id=self.kwargs["intento"])
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
                intento=intento,
                pregunta = pregunta,
                opcion = opcion,
                correcto = correcto
            )
            all_intentos.append(intento_pregunta)
        
        IntentoPregunta.objects.bulk_create(all_intentos)

        dificultad = intento.evaluacion.dificultad_ponderada
        intento.puntuacion = (acierto/intento.evaluacion.cant_preguntas)*100 
        puntos_obtenidos=0
        obj, created = PuntosObtenidos.objects.get_or_create(
                evaluacion=intento.evaluacion,
                usuario=intento.usuario,
            )
        if intento.puntuacion >= intento.evaluacion.puntaje_minimo:
            intento.aprobado = True
            obj, created = PuntosObtenidos.objects.get_or_create(
                evaluacion=intento.evaluacion,
                usuario=intento.usuario,
            )
                
            if intento.puntuacion == 100:
                puntos_obtenidos =dificultad*0.2*intento.puntuacion
                obj.puntos = puntos_obtenidos
                obj.save()
                puntaje = PuntosObtenidos.objects.filter(
                    usuario__id=intento.usuario.id
                    ).aggregate(total=Sum('puntos'))

                rango = ranquear_usuario(puntaje["total"])

                intento.usuario.rango = rango
            else:
                puntos_obtenidos =dificultad*0.1*intento.puntuacion
                if puntos_obtenidos > obj.puntos:
                    obj.puntos = puntos_obtenidos
                    obj.save()
                    puntaje = PuntosObtenidos.objects.filter(
                        usuario__id=intento.usuario.id
                        ).aggregate(total=Sum('puntos'))
    
                    rango = ranquear_usuario(puntaje["total"])
                    intento.usuario.rango = rango
        intento.puntos = puntos_obtenidos
        intento.hora_fin = timezone.now()
        intento.save()
        intento.usuario.save()
        t = timezone.now().strftime('%d de %B de %Y %H:%M')
        
        #Creando la notificación:
        
        noti = Notificacion.objects.create(
            usuario = intento.evaluacion.user,
            usuario_notificacion = intento.usuario,
            mensaje = f"{intento.usuario.username} ha realizado un intento de la evaluacion {intento.evaluacion.nombre}, el {t}"
        )
        noti.save()
        
        return HttpResponseRedirect(
                reverse(
                    'intentos_app:resultadointento',kwargs={'pk': intento.id}
                )
            )

class ResultadoIntento(DetailView):
    model = Intento
    template_name = "intentos/resultadointento.html"
    context_object_name= "intento"

