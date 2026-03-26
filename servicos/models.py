from django.db import models
from clientes.models import Cliente
from decimal import Decimal



class TipoServico(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    valor_padrao = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome
    
class Funcionario(models.Model):
    nome = models.CharField(max_length=100)

    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    valor_dia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
    
class Veiculo(models.Model):

    COMBUSTIVEL = [
        ("gasolina", "Gasolina"),
        ("etanol", "Etanol"),
        ("diesel", "Diesel"),
        ("gnv", "GNV"),
        ("flex", "Flex"),
    ]

    nome = models.CharField(max_length=100)

    placa = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    combustivel = models.CharField(
        max_length=20,
        choices=COMBUSTIVEL,
        blank=True,
        null=True
    )

    consumo_km_litro = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Consumo (km/l)"
    )

    ativo = models.BooleanField(default=True)

    def __str__(self):
        if self.placa:
            return f"{self.nome} - {self.placa}"
        return self.nome

class OrdemServico(models.Model):

    STATUS = [
        ('agendado', 'Agendado'),
        ('executado', 'Executado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE
    )

    data = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='agendado'
    )

    observacao = models.TextField(
        blank=True,
        null=True
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    numero_funcionarios = models.IntegerField(
        default=1,
        verbose_name="Funcionários"
    )

    km_rodado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="KM rodado"
    )

    funcionarios = models.ManyToManyField(
        'Funcionario',
        blank=True
    )

    veiculo = models.ForeignKey(
        'Veiculo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    preco_combustivel = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        verbose_name="Preço do combustível (R$/L)"
    )

    def calcular_total(self):
        total = sum(i.valor for i in self.itens.all())
        self.total = total
    
        def atualizar_lancamento_receita(self):
            from financeiro.models import Lancamento

            if self.status == "executado" and self.total > 0:
                Lancamento.objects.update_or_create(
                    descricao=f"OS #{self.id}",
                    defaults={
                        "tipo": "R",
                        "valor": self.total,
                        "data": self.data,
                        "veiculo": self.veiculo,
                    }
                )
            else:
                Lancamento.objects.filter(
                    descricao=f"OS #{self.id}",
                    tipo="R"
                ).delete()

    def atualizar_lancamento_receita(self):
        from financeiro.models import Lancamento, Categoria

        categoria_receita = Categoria.objects.filter(tipo="R").first()

        if self.status == "executado" and self.total > 0:
            Lancamento.objects.update_or_create(
                ordem_servico=self,
                tipo="R",
                defaults={
                    "categoria": categoria_receita,
                    "descricao": f"Ordem de Serviço #{self.id}",
                    "valor": self.total,
                    "data": self.data,
                    "veiculo": self.veiculo,
                }
            )
        else:
            Lancamento.objects.filter(
                ordem_servico=self,
                tipo="R"
            ).delete()
    
    def save(self, *args, **kwargs):
        if self.pk:
            self.calcular_total()

        super().save(*args, **kwargs)

        self.atualizar_lancamento_receita()

    def __str__(self):
        return f"OS {self.id} - {self.cliente}"
    
class ItemServico(models.Model):

    ordem = models.ForeignKey(
        OrdemServico,
        on_delete=models.CASCADE,
        related_name="itens"
    )

    tipo_servico = models.ForeignKey(
        TipoServico,
        on_delete=models.CASCADE
    )

    quantidade = models.IntegerField(default=1)

    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def save(self, *args, **kwargs):

        if not self.valor_unitario:
            self.valor_unitario = self.tipo_servico.valor_padrao

        self.valor = self.quantidade * self.valor_unitario

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo_servico}"


class Servico(models.Model):

    STATUS = [
        ('agendado', 'Agendado'),
        ('executado', 'Executado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo_servico = models.ForeignKey(TipoServico, on_delete=models.CASCADE)
    descricao = models.TextField(blank=True, null=True)
    quantidade = models.IntegerField(default=1)
    valor_unitario = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
)

    valor = models.DecimalField(max_digits=10, decimal_places=2)

    data = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='agendado'
    )

    observacao = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        from financeiro.models import Lancamento
        
        # pegar valor padrão se não tiver
        if not self.valor_unitario or self.valor_unitario == Decimal("0.00"):
            if self.tipo_servico:
                self.valor_unitario = self.tipo_servico.valor_padrao

        # calcular total
        self.valor = self.quantidade * self.valor_unitario

        super().save(*args, **kwargs)

        # integração financeiro
        if self.status == 'executado' and self.valor > 0:

            Lancamento.objects.update_or_create(
                servico=self,
                defaults={
                    "tipo": "R",
                    "descricao": f"Serviço #{self.id}",
                    "valor": self.valor,
                    "data": self.data,
                }
            )
        else:
            Lancamento.objects.filter(servico=self).delete()

    def __str__(self):
        return f"{self.cliente} - {self.tipo_servico} - {self.data}"
