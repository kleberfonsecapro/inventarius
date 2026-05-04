from django.contrib import admin
from django.utils.html import format_html
from .models import Setor, Servidor, Patrimonio, RegistroAuditoria


@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'localizacao', 'criado_em')
    search_fields = ('nome', 'localizacao')


@admin.register(Servidor)
class ServidorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'matricula', 'setor', 'ativo')
    list_filter = ('setor', 'ativo')
    search_fields = ('nome', 'matricula')


@admin.register(Patrimonio)
class PatrimonioAdmin(admin.ModelAdmin):
    list_display = ('numero_patrimonio', 'nome', 'setor', 'servidor_responsavel', 'preview_qr')
    list_filter = ('setor',)
    search_fields = ('numero_patrimonio', 'nome')
    readonly_fields = ('qrcode_img', 'preview_qr')

    def preview_qr(self, obj):
        if obj.qrcode_img:
            return format_html('<img src="{}" width="60" />', obj.qrcode_img.url)
        return '—'
    preview_qr.short_description = 'QR Code'


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('patrimonio', 'tipo', 'setor_origem', 'setor_destino', 'registrado_em')
    list_filter = ('tipo', 'setor_destino')
    readonly_fields = ('registrado_em',)
