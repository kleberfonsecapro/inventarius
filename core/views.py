from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .models import Patrimonio, Setor, Servidor, RegistroAuditoria
from .forms import PatrimonioForm, PesquisaForm, AuditoriaForm, UsuarioForm, LoginForm


def is_admin(user):
    return user.is_staff or user.is_superuser


# ---------- Auth ----------

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user:
            if not user.is_active:
                form.add_error(None, 'Sua conta está desativada.')
            else:
                login(request, user)
                return redirect(request.GET.get('next', 'core:dashboard'))
        else:
            form.add_error(None, 'Usuário ou senha incorretos.')
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('core:login')


# ---------- Usuários (admin only) ----------

@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def usuario_lista(request):
    usuarios = User.objects.all().order_by('username')
    return render(request, 'core/usuario_lista.html', {'usuarios': usuarios})


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def usuario_novo(request):
    form = UsuarioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data.get('email', ''),
            is_staff=form.cleaned_data.get('is_staff', False),
        )
        messages.success(request, f'Usuário "{user.username}" criado com sucesso!')
        return redirect('core:usuario_lista')
    return render(request, 'core/usuario_form.html', {'form': form, 'titulo': 'Novo Usuário'})


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    form = UsuarioForm(request.POST or None, instance=usuario)
    if request.method == 'POST' and form.is_valid():
        usuario.username = form.cleaned_data['username']
        usuario.first_name = form.cleaned_data['first_name']
        usuario.last_name = form.cleaned_data['last_name']
        usuario.email = form.cleaned_data.get('email', '')
        usuario.is_staff = form.cleaned_data.get('is_staff', False)
        if form.cleaned_data.get('password'):
            usuario.set_password(form.cleaned_data['password'])
        usuario.save()
        messages.success(request, 'Usuário atualizado com sucesso!')
        return redirect('core:usuario_lista')
    return render(request, 'core/usuario_form.html', {
        'form': form, 'titulo': f'Editar — {usuario.username}', 'usuario': usuario
    })


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def usuario_toggle_ativo(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario != request.user:
        usuario.is_active = not usuario.is_active
        usuario.save()
        status = 'ativado' if usuario.is_active else 'desativado'
        messages.success(request, f'Usuário "{usuario.username}" {status}.')
    return redirect('core:usuario_lista')


# ---------- Dashboard ----------

@login_required(login_url='/login/')
def dashboard(request):
    total_patrimonios = Patrimonio.objects.count()
    total_setores = Setor.objects.count()
    total_servidores = Servidor.objects.filter(ativo=True).count()
    ultimas_auditorias = RegistroAuditoria.objects.select_related(
        'patrimonio', 'setor_destino'
    ).order_by('-registrado_em')[:10]
    context = {
        'total_patrimonios': total_patrimonios,
        'total_setores': total_setores,
        'total_servidores': total_servidores,
        'ultimas_auditorias': ultimas_auditorias,
    }
    return render(request, 'core/dashboard.html', context)


# ---------- Patrimônios ----------

@login_required(login_url='/login/')
def patrimonio_lista(request):
    form = PesquisaForm(request.GET)
    patrimonios = Patrimonio.objects.select_related('setor', 'servidor_responsavel').all()
    if form.is_valid():
        q = form.cleaned_data.get('q')
        setor = form.cleaned_data.get('setor')
        if q:
            patrimonios = patrimonios.filter(
                Q(numero_patrimonio__icontains=q) |
                Q(nome__icontains=q) |
                Q(setor__nome__icontains=q) |
                Q(servidor_responsavel__nome__icontains=q)
            )
        if setor:
            patrimonios = patrimonios.filter(setor=setor)
    return render(request, 'core/patrimonio_lista.html', {'patrimonios': patrimonios, 'form': form})


@login_required(login_url='/login/')
def patrimonio_detalhe(request, pk):
    patrimonio = get_object_or_404(Patrimonio, pk=pk)
    historico = patrimonio.auditorias.select_related(
        'setor_origem', 'setor_destino', 'servidor_responsavel'
    ).order_by('-registrado_em')[:20]
    return render(request, 'core/patrimonio_detalhe.html', {'patrimonio': patrimonio, 'historico': historico})


@login_required(login_url='/login/')
def patrimonio_novo(request):
    if request.method == 'POST':
        form = PatrimonioForm(request.POST, request.FILES)
        if form.is_valid():
            patrimonio = form.save()
            messages.success(request, f'Patrimônio {patrimonio.numero_patrimonio} cadastrado com sucesso!')
            return redirect('core:patrimonio_detalhe', pk=patrimonio.pk)
    else:
        form = PatrimonioForm()
    return render(request, 'core/patrimonio_form.html', {'form': form, 'titulo': 'Novo Patrimônio'})


@login_required(login_url='/login/')
def patrimonio_editar(request, pk):
    patrimonio = get_object_or_404(Patrimonio, pk=pk)
    if request.method == 'POST':
        form = PatrimonioForm(request.POST, request.FILES, instance=patrimonio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patrimônio atualizado com sucesso!')
            return redirect('core:patrimonio_detalhe', pk=patrimonio.pk)
    else:
        form = PatrimonioForm(instance=patrimonio)
    return render(request, 'core/patrimonio_form.html', {
        'form': form, 'titulo': f'Editar — {patrimonio.numero_patrimonio}', 'patrimonio': patrimonio
    })


@login_required(login_url='/login/')
def patrimonio_plaqueta(request, pk):
    patrimonio = get_object_or_404(Patrimonio, pk=pk)
    return render(request, 'core/plaqueta_print.html', {'patrimonio': patrimonio})


# ---------- QR Code ----------

@login_required(login_url='/login/')
def leitor_qrcode(request):
    return render(request, 'core/leitor_qrcode.html')


@login_required(login_url='/login/')
def verificar_patrimonio(request, numero):
    patrimonio = get_object_or_404(Patrimonio, numero_patrimonio=numero)
    form = AuditoriaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        acao = form.cleaned_data['acao']
        setor_destino = form.cleaned_data.get('setor_destino')
        servidor = form.cleaned_data.get('servidor_responsavel')
        observacao = form.cleaned_data.get('observacao', '')
        if acao == 'transferencia' and not setor_destino:
            form.add_error('setor_destino', 'Informe o novo setor para transferência.')
        else:
            setor_origem = patrimonio.setor
            RegistroAuditoria.objects.create(
                patrimonio=patrimonio,
                tipo=acao,
                setor_origem=setor_origem,
                setor_destino=setor_destino if acao == 'transferencia' else setor_origem,
                servidor_responsavel=servidor,
                observacao=observacao,
            )
            if acao == 'transferencia' and setor_destino:
                patrimonio.setor = setor_destino
                if servidor:
                    patrimonio.servidor_responsavel = servidor
                patrimonio.save()
                messages.success(request, f'Transferência registrada! Novo setor: {setor_destino.nome}')
            else:
                messages.success(request, 'Localização confirmada com sucesso!')
            return redirect('core:verificar_patrimonio', numero=numero)
    historico = patrimonio.auditorias.order_by('-registrado_em')[:5]
    return render(request, 'core/verificar_patrimonio.html', {
        'patrimonio': patrimonio, 'form': form, 'historico': historico
    })


@login_required(login_url='/login/')
def plaqueta_lote(request):
    patrimonios = Patrimonio.objects.select_related('setor').order_by('setor__nome', 'numero_patrimonio')
    setores = Setor.objects.all().order_by('nome')
    return render(request, 'core/plaqueta_lote.html', {
        'patrimonios': patrimonios,
        'setores': setores,
    })
