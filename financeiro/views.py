from django.shortcuts import render
from .models import Lancamento
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import date
from servicos.models import OrdemServico
import json
from decimal import Decimal



def dashboard_financeiro(request):

    total_receitas = (
        Lancamento.objects
        .filter(tipo='R')
        .aggregate(Sum('valor'))['valor__sum'] or 0
    )

    total_despesas = (
        Lancamento.objects
        .filter(tipo='D')
        .aggregate(Sum('valor'))['valor__sum'] or 0
    )

    lucro = total_receitas - total_despesas

    hoje = date.today()

    receitas_hoje = (
        Lancamento.objects
        .filter(tipo='R', data=hoje)
        .aggregate(Sum('valor'))['valor__sum'] or 0
    )

    despesas_hoje = (
        Lancamento.objects
        .filter(tipo='D', data=hoje)
        .aggregate(Sum('valor'))['valor__sum'] or 0
    )

    lucro_hoje = receitas_hoje - despesas_hoje

    servicos_hoje = OrdemServico.objects.filter(
        data=hoje,
        status='executado'
    ).count()

    dados_r = (
        Lancamento.objects
        .filter(tipo='R')
        .annotate(mes=TruncMonth('data'))
        .values('mes')
        .annotate(total=Sum('valor'))
        .order_by('mes')
    )

    dados_d = (
        Lancamento.objects
        .filter(tipo='D')
        .annotate(mes=TruncMonth('data'))
        .values('mes')
        .annotate(total=Sum('valor'))
        .order_by('mes')
    )

    dados_categoria = (
        Lancamento.objects
        .filter(tipo='D')
        .values('categoria__nome')
        .annotate(total=Sum('valor'))
    )

    resumo_categoria = (
        Lancamento.objects
        .filter(tipo="D")
        .values("categoria__nome")
        .annotate(total=Sum("valor"))
    )

    custos_por_dia = (
        Lancamento.objects
        .filter(tipo="D")
        .values("data")
        .annotate(total=Sum("valor"))
        .order_by("data")
    )

    gasto_combustivel = (
        Lancamento.objects
        .filter(
            tipo="D",
            categoria__nome="Combustível"
        )
        .aggregate(Sum("valor"))["valor__sum"] or 0
    )

    gasto_manutencao = (
        Lancamento.objects
        .filter(
            tipo="D",
            categoria__nome="Manutenção carro"
        )
        .aggregate(Sum("valor"))["valor__sum"] or 0
    )

    custos_veiculo = (
        Lancamento.objects
        .filter(tipo="D", veiculo__isnull=False)
        .values("veiculo__nome")
        .annotate(total=Sum("valor"))
    )

    # custo real por km de cada veículo
    custos = (
        Lancamento.objects
        .filter(tipo="D", veiculo__isnull=False)
        .values("veiculo")
        .annotate(total=Sum("valor"))
    )

    kms = (
        OrdemServico.objects
        .filter(veiculo__isnull=False, km_rodado__gt=0)
        .values("veiculo")
        .annotate(total_km=Sum("km_rodado"))
    )

    km_dict = {k["veiculo"]: k["total_km"] for k in kms}

    custo_km_veiculo = {}

    for c in custos:
        veiculo_id = c["veiculo"]
        total_custo = c["total"] or Decimal("0")
        km_total = km_dict.get(veiculo_id, Decimal("0"))

        if km_total > 0:
            custo_km_veiculo[veiculo_id] = total_custo / km_total
        else:
            custo_km_veiculo[veiculo_id] = Decimal("0")

    gasto_carro = gasto_combustivel + gasto_manutencao

    lucro_real = total_receitas - total_despesas

    meses = []
    receitas = []
    despesas = []
    categorias = []
    valores_categoria = []

    for d in dados_r:
        meses.append(d['mes'].strftime('%m/%Y'))
        receitas.append(float(d['total']))

    for d in dados_d:
        despesas.append(float(d['total']))

    for d in dados_categoria:
        categorias.append(d['categoria__nome'])
        valores_categoria.append(float(d['total']))

    total_servicos = OrdemServico.objects.filter(
        status='executado'
    ).count()

    total_os_valor = OrdemServico.objects.filter(
        status="executado"
    ).aggregate(
        Sum("total")
    )["total__sum"] or 0

    os_executadas = OrdemServico.objects.filter(
        status="executado"
    )

    lista_os = []

    for os in os_executadas:

        despesas_dia = (
            Lancamento.objects
            .filter(
                tipo="D",
                data=os.data
            )
            .aggregate(Sum("valor"))["valor__sum"] or 0
        )

        qtd_os_dia = OrdemServico.objects.filter(
            status="executado",
            data=os.data
        ).count()

        if qtd_os_dia == 0:
            qtd_os_dia = 1

        custo_por_os = despesas_dia / qtd_os_dia

        custo_func = sum(
            f.valor_dia for f in os.funcionarios.all()
        )

        km = Decimal(str(os.km_rodado or 0))

        if os.veiculo and os.veiculo.consumo_km_litro and os.preco_combustivel:
            consumo = Decimal(str(os.veiculo.consumo_km_litro))
            preco = Decimal(str(os.preco_combustivel))

            if consumo > 0:
                litros_gastos = km / consumo
                custo_km = litros_gastos * preco
            else:
                custo_km = Decimal("0.00")
        else:
            custo_km = Decimal("0.00")

        custo_por_os = Decimal(str(custo_por_os or 0))
        custo_func = Decimal(str(custo_func or 0))

        lucro_os = os.total - custo_por_os - custo_func - custo_km

        lista_os.append({
            "id": os.id,
            "cliente": os.cliente.nome,
            "data": os.data,
            "total": os.total,
            "despesas": custo_por_os,
            "funcionarios": os.funcionarios.count(),
            "custo_func": custo_func,
            "km_rodado": os.km_rodado,
            "custo_km": custo_km,
            "lucro": lucro_os,
        })

    dias = []
    valores_dia = []

    for c in custos_por_dia:
        if c["data"]:
            dias.append(c["data"].strftime("%d/%m"))
        else:
            dias.append("")

        valores_dia.append(float(c["total"]))

    context = {
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'lucro': lucro,
        'receitas_hoje': receitas_hoje,
        'despesas_hoje': despesas_hoje,
        'lucro_hoje': lucro_hoje,
        'servicos_hoje': servicos_hoje,
        'meses': json.dumps(meses),
        'receitas': json.dumps(receitas),
        'despesas': json.dumps(despesas),
        'total_servicos': total_servicos,
        'total_os_valor': total_os_valor,
        'lista_os': lista_os,
        'categorias': json.dumps(categorias),
        'valores_categoria': json.dumps(valores_categoria),
        'resumo_categoria': resumo_categoria,
        'dias': json.dumps(dias),
        'valores_dia': json.dumps(valores_dia),
        'gasto_combustivel': gasto_combustivel,
        'gasto_manutencao': gasto_manutencao,
        'gasto_carro': gasto_carro,
        'custos_veiculo': custos_veiculo,
        'lucro_real': lucro_real,
    }

    return render(
        request,
        "dashboard.html",
        context
    )


def lista_lancamentos(request):

    lancamentos = Lancamento.objects.all()

    return render(
        request,
        'financeiro/lista.html',
        {'lancamentos': lancamentos}
    )
