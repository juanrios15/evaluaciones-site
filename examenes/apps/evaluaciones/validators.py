from django.core.exceptions import ValidationError

def validate_minmax(value):
    if value <60:
        raise ValidationError(
            'Puntaje minimo de 60 para aprobar')
    elif value>90:
        raise ValidationError(
            'Puntaje maximo de 90 para aprobar')
        
def intentos_minmax(value):
    if value <1:
        raise ValidationError(
            'Minimo un intento')
    elif value>10:
        raise ValidationError(
            'Maximo 10 intentos permitidos')

def cantidad_preguntasminmax(value):
    if value <5:
        raise ValidationError(
            'Minimo 5 preguntas por intento')
    elif value>50:
        raise ValidationError(
            'Maximo 50 preguntas por intento')
        
def tiempominmax(value):
    if value <2:
        raise ValidationError(
            'Minimo 2 minutos por intento')
    elif value>60:
        raise ValidationError(
            'Maximo 120 minutos por intento')
        
def dificultadminmax(value):
    if value <1:
        raise ValidationError(
            'Minimo dificultad 1')
    elif value>10:
        raise ValidationError(
            'Maximo dificultad 10')