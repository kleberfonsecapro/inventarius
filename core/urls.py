from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Usuários
    path('usuarios/', views.usuario_lista, name='usuario_lista'),
    path('usuarios/novo/', views.usuario_novo, name='usuario_novo'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('usuarios/<int:pk>/toggle/', views.usuario_toggle_ativo, name='usuario_toggle'),
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    # Patrimônios
    path('patrimonios/', views.patrimonio_lista, name='patrimonio_lista'),
    path('patrimonios/novo/', views.patrimonio_novo, name='patrimonio_novo'),
    path('patrimonios/<int:pk>/', views.patrimonio_detalhe, name='patrimonio_detalhe'),
    path('patrimonios/<int:pk>/editar/', views.patrimonio_editar, name='patrimonio_editar'),
    path('patrimonios/<int:pk>/plaqueta/', views.patrimonio_plaqueta, name='plaqueta'),
    # QR
    path('plaquetas/lote/', views.plaqueta_lote, name='plaqueta_lote'),
    path('leitor/', views.leitor_qrcode, name='leitor_qrcode'),
    path('verificar/<str:numero>/', views.verificar_patrimonio, name='verificar_patrimonio'),
]
