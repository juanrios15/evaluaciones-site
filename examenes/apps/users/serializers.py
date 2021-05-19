from rest_framework import serializers

class LoginSocialSerializer(serializers.Serializer):
    
    token_id = serializers.CharField(required=True)