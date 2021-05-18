# Generated by Django 3.1.7 on 2021-05-10 02:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evaluaciones', '0014_auto_20210507_2038'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('intentos', '0004_auto_20210508_1617'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='intento',
            name='puntos',
        ),
        migrations.CreateModel(
            name='PuntosObtenidos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntos', models.FloatField(default=0)),
                ('evaluacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='puntos', to='evaluaciones.evaluacion')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='puntos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Puntos',
                'verbose_name_plural': 'Puntos Evaluaciones',
            },
        ),
    ]