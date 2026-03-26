from django.db import models
from servicos.models import Veiculo, OrdemServico


class Categoria(models.Model):

    nome = models.CharField(
        max_length=100
    )

    tipo = models.CharField(
        max_length=1,
        choices=[
            ("R", "Receita"),
            ("D", "Despesa"),
        ]
    )

    def __str__(self):
        return self.nome
    
class Lancamento(models.Model):

    TIPOS = [
        ("R", "Receita"),
        ("D", "Despesa"),
    ]

    tipo = models.CharField(
        max_length=1,
        choices=TIPOS
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    ordem_servico = models.ForeignKey(
    OrdemServico,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name="lancamentos"
    )

    servico = models.ForeignKey(
    'servicos.Servico',
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name="lancamentos"
    )

    descricao = models.CharField(
        max_length=200
    )

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    data = models.DateField()

    veiculo = models.ForeignKey(
    Veiculo,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    def __str__(self):
        return self.descricao

