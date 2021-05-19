
from apps.intentos.models import IntentoPregunta
from django import forms
from apps.evaluaciones.models import Opcion, Pregunta


class IntentoPreguntaForm(forms.Form):
    """Form definition for IntentoPregunta."""
    opcion = forms.CharField(max_length=400, required=False)

    class Meta:
        """Meta definition for IntentoPreguntaform."""

        fields = ('opcion',)
        

