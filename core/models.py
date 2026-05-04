import qrcode
import io
import os
from django.db import models
from django.core.files.base import ContentFile
from django.urls import reverse


class Setor(models.Model):
    nome = models.CharField('Nome do Setor', max_length=200)
    localizacao = models.CharField('Localização', max_length=300)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Setor'
        verbose_name_plural = 'Setores'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} — {self.localizacao}'


class Servidor(models.Model):
    nome = models.CharField('Nome Completo', max_length=200)
    matricula = models.CharField('Matrícula', max_length=50, unique=True)
    setor = models.ForeignKey(
        Setor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='servidores', verbose_name='Setor'
    )
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Servidor'
        verbose_name_plural = 'Servidores'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} ({self.matricula})'


class Patrimonio(models.Model):
    nome = models.CharField('Nome do Item', max_length=300)
    descricao = models.TextField('Descrição', blank=True)
    foto = models.ImageField('Foto', upload_to='patrimonios/fotos/', blank=True, null=True)
    numero_patrimonio = models.CharField('Número de Patrimônio', max_length=100, unique=True)
    qrcode_img = models.ImageField('QR Code', upload_to='patrimonios/qrcodes/', blank=True, null=True)
    setor = models.ForeignKey(
        Setor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='patrimonios', verbose_name='Setor'
    )
    servidor_responsavel = models.ForeignKey(
        Servidor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='patrimonios', verbose_name='Servidor Responsável'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Patrimônio'
        verbose_name_plural = 'Patrimônios'
        ordering = ['numero_patrimonio']

    def __str__(self):
        return f'{self.numero_patrimonio} — {self.nome}'

    def get_absolute_url(self):
        return reverse('core:patrimonio_detalhe', kwargs={'pk': self.pk})

    def gerar_qrcode(self):
        """Gera o QR Code com a URL de verificação e salva no campo qrcode_img."""
        url = f'/verificar/{self.numero_patrimonio}/'
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        filename = f'qr_{self.numero_patrimonio}.png'
        self.qrcode_img.save(filename, ContentFile(buffer.read()), save=False)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_numero = None
        if not is_new:
            try:
                old_numero = Patrimonio.objects.get(pk=self.pk).numero_patrimonio
            except Patrimonio.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Gera/regenera QR Code se for novo ou se o número mudou
        if is_new or old_numero != self.numero_patrimonio:
            # Remove QR Code antigo se existir
            if self.qrcode_img:
                try:
                    if os.path.isfile(self.qrcode_img.path):
                        os.remove(self.qrcode_img.path)
                except Exception:
                    pass
            self.gerar_qrcode()
            # Save apenas os campos de imagem para evitar loop
            Patrimonio.objects.filter(pk=self.pk).update(qrcode_img=self.qrcode_img.name)


class RegistroAuditoria(models.Model):
    TIPO_CHOICES = [
        ('confirmacao', 'Confirmação de Local'),
        ('transferencia', 'Transferência'),
    ]
    patrimonio = models.ForeignKey(
        Patrimonio, on_delete=models.CASCADE,
        related_name='auditorias', verbose_name='Patrimônio'
    )
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    setor_origem = models.ForeignKey(
        Setor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='auditorias_origem', verbose_name='Setor de Origem'
    )
    setor_destino = models.ForeignKey(
        Setor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='auditorias_destino', verbose_name='Setor de Destino'
    )
    servidor_responsavel = models.ForeignKey(
        Servidor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='auditorias', verbose_name='Servidor'
    )
    observacao = models.TextField('Observação', blank=True)
    registrado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de Auditoria'
        verbose_name_plural = 'Registros de Auditoria'
        ordering = ['-registrado_em']

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.patrimonio} — {self.registrado_em:%d/%m/%Y %H:%M}'
