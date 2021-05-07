# Generated by Django 3.1.7 on 2021-05-06 18:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('evaluaciones', '0011_auto_20210504_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluacion',
            name='slug',
            field=models.SlugField(default='', editable=False),
        ),
        migrations.AlterField(
            model_name='seguirevaluacion',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoritos', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='subcategoria',
            name='categoria',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategoria', to='evaluaciones.categoria', verbose_name='Categoria'),
        ),
    ]
