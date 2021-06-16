from apps.evaluaciones.models import SeguirEvaluacion
from apps.users.models import Notificacion, SeguirUsuario


def usuarios_seguidos(request):
    usuarios_seguidos = SeguirUsuario.objects.filter(seguidor__id = request.user.id).values_list('seguido__id',flat=True)
    
    return { 'usuarios_seguidos':usuarios_seguidos}

def path_actual(request):
    path =  request.path.split("/")[1]
    
    return { 'path_actual':path}

def notificaciones(request):
    cant_notificaciones = Notificacion.objects.filter(usuario__id=request.user.id).count()
    return { 'cant_notificaciones':cant_notificaciones}