# Generated by Django 3.1.7 on 2021-05-01 21:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evaluaciones', '0008_auto_20210501_1550'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evaluacion',
            name='categoria',
        ),
        migrations.AlterField(
            model_name='evaluacion',
            name='subcategoria',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluaciones.subcategoria', verbose_name='SubCategorias'),
        ),
    ]
