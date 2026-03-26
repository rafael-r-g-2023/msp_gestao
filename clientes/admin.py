from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'cpf', 'data_cadastro')
    search_fields = ('nome', 'telefone', 'email', 'cpf')