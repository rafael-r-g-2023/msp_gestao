from django.db import models

# Create your models here.

class Cliente(models.Model):
    nome = models.CharField(max_length=100,blank=True)
    telefone = models.CharField(max_length=20,blank=True)
    email = models.EmailField(blank=True, null=True)
    endereco = models.CharField(max_length=200,blank=True)
    cpf = models.CharField(max_length=14,blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
    
class Lancamento(models.Model):
    TIPO_CHOICES = (
        ('R', 'Receita'),
        ('D', 'Despesa'),
    )

    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao}"
