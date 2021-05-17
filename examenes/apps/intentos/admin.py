from django.contrib import admin

# Register your models here.
from apps.intentos.models import Intento, IntentoPregunta, PuntosObtenidos

class intentopanel(admin.ModelAdmin):
    
    readonly_fields = ("puntuacion","aprobado", "hora_inicio","hora_fin","id")

admin.site.register(Intento,intentopanel)
admin.site.register(IntentoPregunta)
admin.site.register(PuntosObtenidos)