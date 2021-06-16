from rest_framework import serializers
from apps.users.models import Notificacion
from django.contrib.auth import get_user_model
User = get_user_model()

class LoginSocialSerializer(serializers.Serializer):
    
    token_id = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id','foto','full_name','slug')
    
        
class NotificacionSerializer(serializers.ModelSerializer):
    
    usuario_notificacion = UserSerializer()
    class Meta:
        model = Notificacion
        fields = ('id','usuario','usuario_notificacion','mensaje')
    