from apps.evaluaciones.models import SeguirEvaluacion
from apps.users.models import SeguirUsuario

def seguidos(request):
    seguidos = SeguirEvaluacion.objects.filter(usuario__id = request.user.id).values_list('evaluacion__id',flat=True)
    
    return { 'evaluaciones_seguidas':seguidos}

def usuarios_seguidos(request):
    usuarios_seguidos = SeguirUsuario.objects.filter(seguidor__id = request.user.id).values_list('seguido__id',flat=True)
    
    return { 'usuarios_seguidos':usuarios_seguidos}