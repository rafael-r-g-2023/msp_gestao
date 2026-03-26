from django import forms
from .models import Servico, OrdemServico, ItemServico


class ServicoForm(forms.ModelForm):

    class Meta:
        model = Servico

        fields = [
            'cliente',
            'tipo_servico',
            'quantidade',
            'valor_unitario',
            'data',
            'status',
            'observacao',
        ]
    
class OrdemServicoForm(forms.ModelForm):
    class Meta:
        model = OrdemServico
        fields = [
            'cliente',
            'data',
            'veiculo',
            'preco_combustivel',
            'status',
            'observacao',
            'km_rodado',
            'funcionarios',
        ]
        widgets = {
            'funcionarios': forms.SelectMultiple()
        }

class ItemServicoForm(forms.ModelForm):

    class Meta:
        model = ItemServico

        fields = [
            'tipo_servico',
            'quantidade',
            'valor_unitario',
        ]

    def clean(self):

        cleaned_data = super().clean()

        tipo = cleaned_data.get("tipo_servico")
        valor_unitario = cleaned_data.get("valor_unitario")

        if tipo and (not valor_unitario or valor_unitario == 0):
            cleaned_data["valor_unitario"] = tipo.valor_padrao

        return cleaned_data