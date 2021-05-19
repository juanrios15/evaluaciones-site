from django.db import models


class OpcionManager(models.Manager):
    
    def aleatorios(self):
        return self.all().order_by('?')