from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from apps.users.models import SeguirUsuario, Notificacion
User = get_user_model()

# Register your models here.


class CustomUserAdmin(UserAdmin):
    readonly_fields = ["rango"]
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('foto','rango','pais','codigo_pais')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('foto','pais','codigo_pais')}),
    )
    
    
admin.site.register(User,CustomUserAdmin)
admin.site.register(SeguirUsuario)
admin.site.register(Notificacion)