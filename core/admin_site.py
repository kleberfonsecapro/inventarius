from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth import logout
from django.shortcuts import redirect
from .models import Setor, Servidor, Patrimonio, RegistroAuditoria
from .admin import SetorAdmin, ServidorAdmin, PatrimonioAdmin, RegistroAuditoriaAdmin

class CustomAdminSite(AdminSite):
    def logout(self, request, extra_context=None):
        # Apenas redireciona, não encerra sessão
        return redirect('/painel/login/')

    def has_permission(self, request):
        # Se sessão principal não existe, bloqueia acesso ao admin
        if not request.session.get('_auth_user_id'):
            return False
        return super().has_permission(request)

custom_admin_site = CustomAdminSite(name='custom_admin')

custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(Setor, SetorAdmin)
custom_admin_site.register(Servidor, ServidorAdmin)
custom_admin_site.register(Patrimonio, PatrimonioAdmin)
custom_admin_site.register(RegistroAuditoria, RegistroAuditoriaAdmin)
