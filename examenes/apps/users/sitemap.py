from datetime import timedelta,datetime

from django.contrib.sitemaps import Sitemap

from apps.evaluaciones.models import Evaluacion
from django.urls import reverse_lazy

class EvaluacionesSitemap(Sitemap):
    
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'
    
    def items(self):
        return Evaluacion.objects.filter(publico=True)
    
    def lastmod(self,obj):
        return obj.created_at
    
class Sitemap(Sitemap):
    protocol = 'https'
    
    def __init__(self,names):
        self.names = names
        
    def items(self):
        return self.names
    
    def changefreq(self,obj):
        return "weekly"

    def lastmod(self,obj):
        return datetime.now()
    
    def location(self,obj):
        return reverse_lazy(obj)
   
    
