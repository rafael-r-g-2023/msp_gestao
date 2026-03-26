from django.contrib import admin
from django.utils.html import format_html
from .models import TipoServico, Servico, OrdemServico, Funcionario, Veiculo


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_servico', 'valor', 'data', 'status')
    list_filter = ('status', 'data')
    search_fields = ('cliente__nome',)


@admin.register(TipoServico)
class TipoServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'valor_padrao')


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'data', 'status', 'total')
    list_filter = ('status', 'data')
    search_fields = ('cliente__nome',)

    readonly_fields = (
        'id',
        'cliente',
        'data',
        'status',
        'observacao',
        'total',
        'numero_funcionarios',
        'km_rodado',
        'veiculo',
        'preco_combustivel',
        'mostrar_funcionarios',
        'mostrar_itens',
    )

    fields = (
        'id',
        'cliente',
        'data',
        'status',
        'observacao',
        'total',
        'numero_funcionarios',
        'km_rodado',
        'veiculo',
        'preco_combustivel',
        'mostrar_funcionarios',
        'mostrar_itens',
    )

    def mostrar_funcionarios(self, obj):
        funcionarios = obj.funcionarios.all()
        if not funcionarios:
            return "Nenhum funcionário vinculado"
        return ", ".join(f.nome for f in funcionarios)

    mostrar_funcionarios.short_description = "Funcionários"

    def mostrar_itens(self, obj):
        itens = obj.itens.all()
        if not itens:
            return "Nenhum item vinculado"

        linhas = [
            "{} | Qtd: {} | Unit: R$ {} | Total: R$ {}".format(
                item.tipo_servico.nome,
                item.quantidade,
                item.valor_unitario,
                item.valor
            )
            for item in itens
        ]

        return format_html("<br>".join(linhas))

    mostrar_itens.short_description = "Itens da OS"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ("nome", "valor_dia", "ativo")


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ("nome", "placa", "combustivel", "consumo_km_litro", "ativo")

