from django.conf import settings
from django.db import models
from apps.evaluaciones.models import Evaluacion, Opcion, Pregunta
from django.contrib.auth.models import User

# Create your models here.
class Intento(models.Model):
    
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name="intentos")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,related_name="intentos")
    puntuacion = models.FloatField(blank=True, editable=False)
    aprobado = models.BooleanField(blank=True, editable=False)
    hora_inicio = models.DateTimeField(auto_now_add=True, verbose_name="Hora Inicio")
    hora_fin = models.DateTimeField(auto_now=False, auto_now_add=False,blank=True,editable=False,null=True)
    puntos = models.FloatField(default=0) 
    
    class Meta:
        verbose_name= "Intento"
        verbose_name_plural = "Intentos"
    
    def __str__(self):
        return str(self.puntuacion)+" " + str(self.usuario.username)

    
    def duracion(self):
        duracion = int((self.hora_fin - self.hora_inicio).total_seconds())
        minutos = duracion//60
        segundos = duracion%60
        if minutos == 0:
            return f"{segundos} segundos"
        return f"{minutos} minutos, {segundos} segundos"
    
class IntentoPregunta(models.Model):
    
    intento = models.ForeignKey(Intento, on_delete=models.CASCADE,related_name="preguntas",default=1)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE) 
    opcion = models.ForeignKey(Opcion, on_delete=models.CASCADE,blank=True,null=True)
    correcto = models.BooleanField(default=False)
    
    class Meta:
        verbose_name= "Intento_pregunta"
        verbose_name_plural = "Intento_preguntas"
    
    def __str__(self):
        return str(self.correcto)


class PuntosObtenidos(models.Model):
    
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name="evaluacion_puntos")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name="usuario_puntos")
    puntos = models.FloatField(default=0)
    
    class Meta:
        verbose_name= "Puntos"
        verbose_name_plural = "Puntos Evaluaciones"
    
    def __str__(self):
        return str(self.puntos)
