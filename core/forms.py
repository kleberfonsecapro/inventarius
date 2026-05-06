from django import forms
from django.contrib.auth.models import User
from .models import Patrimonio, Setor, Servidor, RegistroAuditoria


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nome de usuário', 'autofocus': True})
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '••••••••'})
    )


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label='Senha',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Deixe em branco para não alterar'}),
        help_text='Obrigatório apenas ao criar. Deixe em branco para não alterar ao editar.'
    )
    is_staff = forms.BooleanField(
        label='Administrador (acesso total)',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff']
        labels = {
            'username': 'Login (nome de usuário)',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }

    def clean(self):
        cleaned = super().clean()
        # Senha obrigatória apenas na criação (sem instance/pk)
        if not self.instance.pk and not cleaned.get('password'):
            self.add_error('password', 'A senha é obrigatória para novos usuários.')
        return cleaned


class PatrimonioForm(forms.ModelForm):
    class Meta:
        model = Patrimonio
        fields = ['nome', 'descricao', 'foto', 'numero_patrimonio', 'setor', 'servidor_responsavel']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nome do item'}),
            'descricao': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Descrição opcional'}),
            'numero_patrimonio': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 2024-001'}),
            'setor': forms.Select(attrs={'class': 'form-input'}),
            'servidor_responsavel': forms.Select(attrs={'class': 'form-input'}),
        }


class PesquisaForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Buscar por número, nome ou setor...',
            'autocomplete': 'off',
        })
    )
    setor = forms.ModelChoiceField(
        queryset=Setor.objects.all(),
        required=False,
        empty_label='Todos os setores',
        widget=forms.Select(attrs={'class': 'form-input'})
    )


class AuditoriaForm(forms.Form):
    ACAO_CHOICES = [
        ('confirmacao', '✅ Confirmar — item está no local correto'),
        ('transferencia', '🔀 Transferir — registrar novo local'),
        ('descarte', '🗑️ Descarte — item sem condições de uso'),
    ]
    acao = forms.ChoiceField(choices=ACAO_CHOICES, widget=forms.RadioSelect)
    setor_destino = forms.ModelChoiceField(
        queryset=Setor.objects.all(),
        required=False,
        empty_label='Selecione o novo setor...',
        label='Novo Setor (obrigatório para transferência)',
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    servidor_responsavel = forms.ModelChoiceField(
        queryset=Servidor.objects.filter(ativo=True),
        required=False,
        empty_label='Servidor responsável...',
        label='Servidor',
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    observacao = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Observação (opcional)'}),
        label='Observação'
    )
