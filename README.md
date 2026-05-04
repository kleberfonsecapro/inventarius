# Inventarius — Sistema de Gestão de Patrimônio

## Stack
- Django 5.1 + Python 3.12
- PostgreSQL 16
- Tailwind CSS (CDN)
- html5-qrcode (câmera mobile)
- qrcode (geração Python)

## Subir o projeto

```bash
# 1. Clonar / extrair os arquivos na pasta do projeto

# 2. Subir os containers
docker compose up -d --build

# 3. Criar superusuário admin
docker compose exec web python manage.py createsuperuser

# 4. Acessar
# Sistema:  http://localhost:8000
# Admin:    http://localhost:8000/admin
```

## Estrutura de URLs

| URL | Descrição |
|-----|-----------|
| `/` | Dashboard |
| `/patrimonios/` | Lista + pesquisa avançada |
| `/patrimonios/novo/` | Cadastrar patrimônio |
| `/patrimonios/<id>/` | Detalhe do item |
| `/patrimonios/<id>/plaqueta/` | Plaqueta para impressão |
| `/leitor/` | Leitor QR Code (câmera) |
| `/verificar/<numero>/` | Verificação / auditoria |
| `/admin/` | Painel Django Admin |

## Fluxo de auditoria

1. Acesse `/leitor/` no celular
2. Aponte para o QR Code da plaqueta
3. O sistema redireciona para `/verificar/<numero>/`
4. Confirme o local ou registre transferência
5. Histórico fica salvo em `RegistroAuditoria`

## Notas

- QR Code é gerado automaticamente ao cadastrar/salvar um patrimônio
- A URL embutida no QR aponta para `/verificar/<numero>/`
- A plaqueta usa `@media print` — basta abrir e Ctrl+P
- Timezone configurado para `America/Cuiaba`
