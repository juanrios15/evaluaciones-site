# Generated by Django 3.1.7 on 2021-05-05 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20210504_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='codigo_pais',
            field=models.CharField(blank=True, default='', max_length=2),
        ),
    ]
