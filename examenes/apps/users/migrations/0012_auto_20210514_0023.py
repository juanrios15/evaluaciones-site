# Generated by Django 3.1.7 on 2021-05-14 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_user_biografia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='biografia',
            field=models.TextField(blank=True, default='', max_length=250, null=True),
        ),
    ]