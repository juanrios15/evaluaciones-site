# Generated by Django 3.1.7 on 2021-05-01 20:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evaluaciones', '0007_auto_20210501_1404'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categoria',
            name='dificultad',
        ),
        migrations.RemoveField(
            model_name='subcategoria',
            name='dificultad',
        ),
    ]
