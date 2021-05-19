from rest_framework import serializers
from apps.evaluaciones.models import Categoria, Evaluacion, SubCategoria
        
class SubcategoriaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SubCategoria
        fields = ('id','nombre',)

class CategoriaSerializer(serializers.ModelSerializer):
    
    subcategoria = SubcategoriaSerializer(many=True, read_only=True)
    class Meta:
        model = Categoria
        fields = ('nombre','subcategoria')
class EvaluacionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Evaluacion
        fields = ('nombre',)
