import datetime

from django.db import models
from django.conf import settings

from apps.evaluaciones.managers import OpcionManager
from apps.evaluaciones.validators import validate_minmax,cantidad_preguntasminmax,intentos_minmax,tiempominmax,dificultadminmax
from django.template.defaultfilters import slugify


class Categoria(models.Model):
    nombre = models.CharField(verbose_name="Categoria", max_length=100)
    descripcion = models.CharField(verbose_name="Descripcion", max_length=250)
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
    
    def __str__(self):
        return self.nombre
    
class SubCategoria(models.Model):
    nombre = models.CharField(verbose_name="Subcategoria", max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, verbose_name="Categoria",related_name="subcategoria")
    descripcion = models.CharField(verbose_name="Descripcion", max_length=250)
    
    class Meta:
        verbose_name = "SubCategoria"
        verbose_name_plural = "SubCategorias"
    
    def __str__(self):
        return self.nombre
    

# Create your models here.
class Evaluacion(models.Model):
    nombre = models.CharField(verbose_name="nombre", max_length=150)
    descripcion = models.TextField(default="")
    requisitos_minimos = models.TextField(default="")
    user =  models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Usuario", on_delete=models.CASCADE, editable=False,related_name="evaluaciones")
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE, verbose_name="SubCategorias")
    imagen = models.ImageField(upload_to="media", height_field=None, width_field=None, max_length=None,blank=True)
    publico = models.BooleanField(default=False)
    visitas = models.IntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at= models.DateTimeField(auto_now=True, verbose_name="Actualizado el")
    puntaje_minimo = models.IntegerField(verbose_name="Puntaje Minimo(60-100)",default=70,validators=[validate_minmax])
    cant_preguntas = models.IntegerField(verbose_name="# preguntas por intento", default=10,validators=[cantidad_preguntasminmax])
    intentos_permitidos = models.PositiveIntegerField(default=2,validators=[intentos_minmax])    
    tiempo_limite = models.IntegerField(verbose_name="Tiempo Limite (minutos)",default=20,validators=[tiempominmax])  
    dificultad = models.FloatField(default=5.0,validators=[dificultadminmax])
    dificultad_ponderada=models.FloatField()
    slug = models.SlugField(default="",editable=False,max_length=150)
    
    # TODO: modelo calificacion, donde los usuarios ponen su puntuacion a la evaluacion, solo para los que ya lo presentaron
    # TODO: modelo puntuardificultad, donde los clientes valoran la dificultad del examen, solo para los que ya lo presentaron
    # TODO: modelo favorito, para que los usuarios puedan guardar sus evaluaciones favoritas
    
    def save(self,*args, **kwargs):
        
        if not self.dificultad_ponderada:
            self.dificultad_ponderada = self.dificultad
        
        if not self.slug:
            now = datetime.datetime.now()
            total_time = datetime.timedelta(
                hours=now.hour,
                minutes=now.minute,
                seconds=now.second
            )
            seconds = int(total_time.total_seconds())
            slug_unique = '%s-%s-%s' % (self.nombre,self.subcategoria, str(seconds))
            self.slug = slugify(slug_unique)
            
        super(Evaluacion,self).save(*args, **kwargs)
        
    
    class Meta:
        verbose_name= "Evaluacion"
        verbose_name_plural = "Evaluaciones"
    
    def __str__(self):
        return self.nombre


class Pregunta(models.Model):
    descripcion = models.TextField(verbose_name="Descripción")
    evaluacion = models.ForeignKey(Evaluacion, verbose_name="Evaluación", on_delete=models.CASCADE, related_name="preguntas")
    
    class Meta:
        verbose_name= "Pregunta"
        verbose_name_plural = "Preguntas"
    
    def __str__(self):
        return "Pregunta  id #"+ str(self.id) + "de evaluacion: "+ str(self.evaluacion)


class Opcion(models.Model):
    pregunta = models.ForeignKey(Pregunta, verbose_name="Pregunta", on_delete=models.CASCADE, related_name="opciones")
    correcta = models.BooleanField(verbose_name="Es esta la respuesta correcta?",default=False)
    texto = models.CharField(verbose_name="Opcion", max_length=200)
    
    objects = OpcionManager()
    
    class Meta:
        verbose_name= "Opción"
        verbose_name_plural = "Opciones"
    
    def __str__(self):
        return self.texto

class CalificarDificultad(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, verbose_name="Evaluación", on_delete=models.CASCADE, related_name="puntuardificultad")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    dificultad = models.FloatField(validators=[dificultadminmax])
    
    
    class Meta:
        unique_together = ('evaluacion','usuario')
        verbose_name = 'Calificar Dificultad'
        verbose_name_plural = 'Calificar Dificultad'

    def __str__(self):
        return self.usuario.username


class ValorarEvaluacion(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, verbose_name="Evaluación", on_delete=models.CASCADE, related_name="valorar")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    valor = models.FloatField(validators=[dificultadminmax])
    
    class Meta:
        unique_together = ('evaluacion','usuario')
        verbose_name = 'Valorar Evaluación'
        verbose_name_plural = 'Valorar Evaluaciones'

    def __str__(self):
        return self.usuario.username

class SeguirEvaluacion(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, verbose_name="Evaluación", on_delete=models.CASCADE, related_name="seguir")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name="favoritos")
    
    class Meta:
        unique_together = ('evaluacion','usuario')
        verbose_name = 'Seguir Evaluación'
        verbose_name_plural = 'Seguir Evaluaciones'

    def __str__(self):
        return self.usuario.username
    