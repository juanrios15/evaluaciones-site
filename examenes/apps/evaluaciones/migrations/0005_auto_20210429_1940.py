# Generated by Django 3.1.7 on 2021-04-30 00:40

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('evaluaciones', '0004_auto_20210429_1134'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='puntuardificultad',
            new_name='CalificarDificultad',
        ),
    ]
