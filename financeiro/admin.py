from django.contrib import admin
from .models import Lancamento, Categoria


admin.site.register(Categoria)
@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'categoria', 'veiculo', 'descricao', 'valor', 'data')
    list_filter = ('tipo', 'categoria', 'veiculo', 'data')
    search_fields = ('descricao',)



