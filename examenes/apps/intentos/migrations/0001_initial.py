# Generated by Django 3.1.7 on 2021-04-28 21:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('evaluaciones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntentoPregunta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('correcto', models.BooleanField()),
                ('opcion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluaciones.opcion')),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluaciones.pregunta')),
            ],
            options={
                'verbose_name': 'Intento_pregunta',
                'verbose_name_plural': 'Intento_preguntas',
            },
        ),
        migrations.CreateModel(
            name='Intento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntuacion', models.FloatField(blank=True, editable=False)),
                ('aprobado', models.BooleanField(blank=True, editable=False)),
                ('hora_inicio', models.DateTimeField(auto_now_add=True, verbose_name='Hora Inicio')),
                ('hora_fin', models.DateTimeField(blank=True, editable=False, null=True)),
                ('abierto', models.BooleanField(blank=True, default=True, editable=False)),
                ('puntos', models.FloatField(default=0)),
                ('evaluacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='intentos', to='evaluaciones.evaluacion')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Intento',
                'verbose_name_plural': 'Intentos',
            },
        ),
    ]
