# Generated by Django 3.1.7 on 2021-06-24 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_notificacion_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='puntos_totales',
            field=models.IntegerField(default=0, editable=False, null=True),
        ),
    ]