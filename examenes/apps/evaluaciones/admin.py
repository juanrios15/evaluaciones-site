from django.contrib import admin

# Register your models here.
from apps.evaluaciones.models import CalificarDificultad, Categoria, Evaluacion, Opcion, Pregunta, ValorarEvaluacion, SubCategoria
from django.forms import BaseInlineFormSet
from django.core.exceptions import ValidationError

class CustomFormSetOpciones(BaseInlineFormSet):
    def clean(self):
        super().clean()
        # example custom validation across forms in the formset
        correcta = 0
        for form in self.forms:
            # your custom formset validation
            if form.cleaned_data.get('correcta') == True:
                correcta += 1
            if correcta >1:
                raise ValidationError("Solo una respuesta correcta por favor") 
        if correcta == 0:
            raise ValidationError("Debe haber una respuesta correcta por favor") 


class PreguntasInline(admin.TabularInline):
    
    model =  Pregunta
    def get_min_num(self, request, obj=None, **kwargs):
        min_num = 5
        return min_num
    
class mipanel(admin.ModelAdmin):
    
    model = Evaluacion
    
    inlines = (PreguntasInline,)
    
    readonly_fields = ("user","created_at","updated_at", "visitas","dificultad_ponderada","slug")
    
    
    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user_id = request.user.id
        obj.save()
        
class OpcionesInline(admin.TabularInline):
    
    model =  Opcion
    formset = CustomFormSetOpciones
    def get_min_num(self, request, obj=None, **kwargs):
        min_num = 2
        return min_num
    
class preguntapanel(admin.ModelAdmin):
    
    model = Pregunta
    inlines =  (OpcionesInline,)
        
admin.site.register(Evaluacion, mipanel)
admin.site.register(Pregunta,preguntapanel)
admin.site.register(Categoria)
admin.site.register(SubCategoria)
admin.site.register(Opcion)
admin.site.register(CalificarDificultad)
admin.site.register(ValorarEvaluacion)
