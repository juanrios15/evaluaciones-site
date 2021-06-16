from django.db import models
from django.conf import settings

from django.contrib.auth.models import AbstractUser
from django.template.defaultfilters import slugify

from apps.evaluaciones.models import Evaluacion
from apps.intentos.models import Intento

# Create your models here.

class User(AbstractUser):
    
    GENDER_CHOICES = (
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('O', 'Otros'),
    )
    email = models.EmailField(unique=True)
    full_name = models.CharField('Nombres', max_length=100,default="")
    slug = models.SlugField()
    foto = models.ImageField(upload_to="media", height_field=None, width_field=None, max_length=None, blank=True)
    biografia = models.TextField(max_length=250,default="", blank=True, null=True)
    genero = models.CharField(max_length=1,choices=GENDER_CHOICES, blank=True)
    fecha_nacimiento = models.DateField('Fecha de nacimiento', blank=True, null=True)
    pais = models.CharField(max_length=50,default="",blank=True)
    codigo_pais = models.CharField(max_length=2,default="",blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el", blank=True)
    rango =models.CharField(max_length=50,default="Practicante",editable=False)
    
    def save(self,*args, **kwargs):
        
        if not self.slug:
            slug_unique = '%s' % (self.username)
            
            self.slug = slugify(slug_unique)
        
        if not self.rango:
            self.rango = "Practicante"

        super(User,self).save(*args, **kwargs)
        

class SeguirUsuario(models.Model):
    seguido = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Seguidores", on_delete=models.CASCADE, related_name="seguidos")
    seguidor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name="seguidores")
    
    class Meta:
        unique_together = ('seguido','seguidor')
        verbose_name = 'Seguir Usuario'
        verbose_name_plural = 'Seguir Usuarios'

    def __str__(self):
        return self.seguido.username
    

class Notificacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name="usuario")
    usuario_notificacion = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name="usuario_notificacion")
    mensaje = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el", blank=True)
    
    def __str__(self):
        return self.mensaje