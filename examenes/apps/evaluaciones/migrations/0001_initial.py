# Generated by Django 3.1.7 on 2021-04-28 21:15

import apps.evaluaciones.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Evaluacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150, verbose_name='nombre')),
                ('descripcion', models.TextField(default='')),
                ('publico', models.BooleanField(default=False)),
                ('visitas', models.IntegerField(default=0, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creado el')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Actualizado el')),
                ('puntaje_minimo', models.IntegerField(default=70, validators=[apps.evaluaciones.validators.validate_minmax], verbose_name='Puntaje Minimo(60-100)')),
                ('cant_preguntas', models.IntegerField(default=10, validators=[apps.evaluaciones.validators.cantidad_preguntasminmax], verbose_name='# preguntas por intento')),
                ('intentos_permitidos', models.PositiveIntegerField(default=2, validators=[apps.evaluaciones.validators.intentos_minmax])),
                ('tiempo_limite', models.IntegerField(default=20, validators=[apps.evaluaciones.validators.tiempominmax], verbose_name='Tiempo Limite (minutos)')),
                ('dificultad', models.FloatField(default=5.0, validators=[apps.evaluaciones.validators.dificultadminmax])),
                ('dificultad_ponderada', models.FloatField(default=5.0)),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Evaluacion',
                'verbose_name_plural': 'Evaluaciones',
            },
        ),
        migrations.CreateModel(
            name='puntuardificultad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dificultad', models.FloatField(validators=[apps.evaluaciones.validators.dificultadminmax])),
                ('evaluacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='puntuardificultad', to='evaluaciones.evaluacion', verbose_name='Evaluación')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pregunta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField(verbose_name='Descripción')),
                ('evaluacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preguntas', to='evaluaciones.evaluacion', verbose_name='Evaluación')),
            ],
            options={
                'verbose_name': 'Pregunta',
                'verbose_name_plural': 'Preguntas',
            },
        ),
        migrations.CreateModel(
            name='Opcion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('correcta', models.BooleanField(default=False, verbose_name='Es esta la respuesta correcta?')),
                ('texto', models.CharField(max_length=300, verbose_name='Opcion')),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opciones', to='evaluaciones.pregunta', verbose_name='Pregunta')),
            ],
            options={
                'verbose_name': 'Opción',
                'verbose_name_plural': 'Opciones',
            },
        ),
    ]
