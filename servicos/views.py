from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages

from django.db.models import Sum
from datetime import datetime, date
from decimal import Decimal

import os

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Image,
    HRFlowable,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from PIL import Image as PILImage

from financeiro.models import Lancamento
from .models import Servico, OrdemServico, ItemServico
from .forms import ServicoForm, OrdemServicoForm, ItemServicoForm


def formatar_os(numero):

    return str(numero).zfill(4)

def formatar_data(data):

    if not data:
        return ""

    return data.strftime("%d/%m/%Y")

def formatar_real(valor):

    if valor is None:
        return "R$ 0,00"

    valor = Decimal(valor)

    return "R$ {:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")


def lista_servicos(request):

    status = request.GET.get('status')

    if status:
        servicos = Servico.objects.filter(status=status)
    else:
        servicos = Servico.objects.all()

    return render(
        request,
        'servicos/lista_servicos.html',
        {'servicos': servicos}
    )


def novo_servico(request):

    form = ServicoForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('/servicos/')

    return render(
        request,
        'servicos/novo_servico.html',
        {'form': form}
    )

def editar_servico(request, id):

    servico = Servico.objects.get(id=id)

    form = ServicoForm(
        request.POST or None,
        instance=servico
    )

    if form.is_valid():
        form.save()
        return redirect('/servicos/')

    return render(
        request,
        'servicos/novo_servico.html',
        {'form': form}
    )

def excluir_servico(request, id):

    servico = Servico.objects.get(id=id)

    servico.delete()

    return redirect('/servicos/')


def servicos_hoje(request):

    hoje = date.today()

    servicos = Servico.objects.filter(data=hoje)

    return render(
        request,
        'servicos/lista_servicos.html',
        {'servicos': servicos}
    )


def servicos_por_data(request):

    data = request.GET.get("data")

    servicos = OrdemServico.objects.all()

    if data:
        servicos = OrdemServico.objects.filter(data=data)

    total_dia = servicos.aggregate(
        Sum("total")
    )["total__sum"] or 0

    quantidade = servicos.count()

    return render(
        request,
        "servicos/por_data.html",
        {
            "servicos": servicos,
            "data": data,
            "total_dia": total_dia,
            "quantidade": quantidade,
        }
    )

def gerar_os_pdf(request, id):

    servico = Servico.objects.get(id=id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="os.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)

    elementos = []

    styles = getSampleStyleSheet()


    # =====================
    # LOGO + CABEÇALHO
    # =====================


    logo_path = os.path.join(
        settings.BASE_DIR,
        'servicos/static/logo.png'
    )

    logo = ""

    if os.path.exists(logo_path):

        img = PILImage.open(logo_path)
        largura, altura = img.size

        nova_largura = 80
        nova_altura = (altura / largura) * nova_largura

        logo = Image(
            logo_path,
            width=nova_largura,
            height=nova_altura
        )

    titulo = Paragraph(
    f"<b>MULTISERVICE PRIME MANUTENÇÃO</b><br/>"
    f"Telefone: 48 99122-4325 / 99171-2631<br/>"
    f"<b>OS Nº {formatar_os(servico.id)}</b>",
    styles["Normal"]
    )

    cabecalho = Table(
        [[logo, titulo]],
        colWidths=[100, 400]
    )

    elementos.append(cabecalho)

    elementos.append(
    Paragraph(
        f"<b>OS Nº {formatar_os(servico.id)}</b>",
        styles["Normal"]
        )
    )   

    elementos.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color="black"
        )
    )

    elementos.append(
        Paragraph(
            f"Cliente: {servico.cliente}",
            styles["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            f"Data: {formatar_data(servico.data)}",
            styles["Normal"]
        )
    )

    elementos.append(Paragraph("<br/>", styles["Normal"]))


    # =====================
    # TABELA
    # =====================

    dados = [
        ["Serviço", "Qtd", "Valor Unitário", "Total"]
    ]

    dados.append([
        str(servico.tipo_servico),
        servico.quantidade,
        formatar_real(servico.valor_unitario),
        formatar_real(servico.valor),
    ])

    dados.append([
        "",
        "",
        "TOTAL",
        formatar_real(servico.valor),
    ])

    tabela = Table(
        dados,
        colWidths=[200, 60, 120, 120]
    )

    tabela.setStyle(TableStyle([

        ('GRID', (0,0), (-1,-1), 1, colors.black),

        ('BACKGROUND', (0,0), (-1,0), colors.grey),

        ('TEXTCOLOR', (0,0), (-1,0), colors.white),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

        ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),

        ('ALIGN', (1,1), (-1,-1), 'CENTER'),

    ]))

    elementos.append(tabela)

    elementos.append(Paragraph("<br/><br/>", styles["Normal"]))


    # =====================
    # OBS
    # =====================

    if servico.observacao:
        elementos.append(
            Paragraph(
                f"Obs: {servico.observacao}",
                styles["Normal"]
            )
        )

    elementos.append(Paragraph("<br/><br/>", styles["Normal"]))


    # =====================
    # ASSINATURA
    # =====================

    elementos.append(
        Paragraph(
            "Assinatura: ____________________________",
            styles["Normal"]
        )
    )

    doc.build(elementos)

    return response



def nova_os(request):

    form = OrdemServicoForm(request.POST or None)

    if form.is_valid():

        os = form.save()

        return redirect(
            "editar_os",
            id=os.id
        )

    return render(
        request,
        "servicos/nova_os.html",
        {
            "form": form
        }
    )


def editar_os(request, id):
    os = get_object_or_404(OrdemServico, id=id)

    form_os = OrdemServicoForm(instance=os)
    form_item = ItemServicoForm()

    if request.method == "POST":

        if "salvar_os" in request.POST:
            form_os = OrdemServicoForm(request.POST, instance=os)

            if form_os.is_valid():
                os = form_os.save(commit=False)
                os.save()
                form_os.save_m2m()

                return redirect("editar_os", id=os.id)

        elif "adicionar_item" in request.POST:
            form_item = ItemServicoForm(request.POST)

            if form_item.is_valid():
                item = form_item.save(commit=False)
                item.ordem = os
                item.save()

                os.calcular_total()
                os.save()

                return redirect("editar_os", id=os.id)
        
    itens = ItemServico.objects.filter(ordem=os)

    return render(
        request,
        "servicos/editar_os.html",
        {
            "form_os": form_os,
            "form_item": form_item,
            "os": os,
            "itens": itens,
        }
    )



def gerar_os_pdf_os(request, id):

    os_obj = OrdemServico.objects.get(id=id)

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = 'inline; filename="os.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=letter
    )

    elementos = []

    styles = getSampleStyleSheet()


    # =====================
    # LOGO + CABEÇALHO
    # =====================


    logo_path = os.path.join(
        settings.BASE_DIR,
        'servicos/static/logo.png'
    )

    logo = ""

    if os.path.exists(logo_path):

        img = PILImage.open(logo_path)
        largura, altura = img.size

        nova_largura = 80
        nova_altura = (altura / largura) * nova_largura

        logo = Image(
            logo_path,
            width=nova_largura,
            height=nova_altura
        )

    titulo = Paragraph(
        f"<b>MULTISERVICE PRIME MANUTENÇÃO</b><br/>"
        f"Telefone: 48 99122-4325 / 99171-2631<br/>"
        f"<b>OS Nº {formatar_os(os_obj.id)}</b>",
        styles["Normal"]
    )

    cabecalho = Table(
        [[logo, titulo]],
        colWidths=[100, 400]
    )

    elementos.append(cabecalho)

    elementos.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color="black"
        )
    )


    elementos.append(
        Paragraph(
            f"Cliente: {os_obj.cliente}",
            styles["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            f"Data: {formatar_data(os_obj.data)}",
            styles["Normal"]
        )
    )

    elementos.append(Paragraph("<br/>", styles["Normal"]))


    # =====================
    # TABELA DE ITENS
    # =====================

    dados = [
        ["Serviço", "Qtd", "Valor Unit", "Total"]
    ]

    for item in os_obj.itens.all():

        dados.append([
            str(item.tipo_servico),
            item.quantidade,
            formatar_real(item.valor_unitario),
            formatar_real(item.valor),
        ])

    dados.append([
        "",
        "",
        "TOTAL",
        formatar_real(os_obj.total),
    ])


    tabela = Table(
        dados,
        colWidths=[200, 60, 120, 120]
    )

    tabela.setStyle(TableStyle([

        ('GRID', (0,0), (-1,-1), 1, colors.black),

        ('BACKGROUND', (0,0), (-1,0), colors.grey),

        ('TEXTCOLOR', (0,0), (-1,0), colors.white),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

        ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),

        ('ALIGN', (1,1), (-1,-1), 'CENTER'),

    ]))

    elementos.append(tabela)

    elementos.append(Paragraph("<br/><br/>", styles["Normal"]))


    # =====================
    # OBS
    # =====================

    if os_obj.observacao:

        elementos.append(
            Paragraph(
                f"Obs: {os_obj.observacao}",
                styles["Normal"]
            )
        )

        elementos.append(Paragraph("<br/>", styles["Normal"]))


    # =====================
    # ASSINATURA
    # =====================

    elementos.append(
        Paragraph(
            "Assinatura: ____________________________",
            styles["Normal"]
        )
    )


    doc.build(elementos)

    return response

def excluir_item(request, id):
    item = ItemServico.objects.get(id=id)
    ordem_servico = item.ordem
    os_id = ordem_servico.id

    item.delete()

    ordem_servico.calcular_total()
    ordem_servico.save()
    ordem_servico.atualizar_lancamento_receita()

    return redirect(
        "editar_os",
        id=os_id
    )

def excluir_os(request, id):

    os = OrdemServico.objects.get(id=id)

    os.delete()

    return redirect("/servicos/")

def duplicar_os(request, id):

    os = OrdemServico.objects.get(id=id)

    nova = OrdemServico.objects.create(
        cliente=os.cliente,
        data=os.data,
        status="agendado",
        observacao=os.observacao,
    )

    for item in os.itens.all():

        ItemServico.objects.create(
            ordem=nova,
            tipo_servico=item.tipo_servico,
            quantidade=item.quantidade,
            valor_unitario=item.valor_unitario,
            valor=item.valor,
        )

    nova.calcular_total()

    return redirect(
        "editar_os",
        id=nova.id
    )

def lista_os(request):

    status = request.GET.get("status")

    if status:
        ordens = OrdemServico.objects.filter(
            status=status
        )
    else:
        ordens = OrdemServico.objects.all()

    return render(
        request,
        "servicos/lista_os.html",
        {
            "ordens": ordens
        }
    )


def dashboard(request):

    ordens = OrdemServico.objects.all()

    total_os = ordens.count()

    agendadas = ordens.filter(
        status="agendado"
    ).count()

    executadas = ordens.filter(
        status="executado"
    ).count()

    canceladas = ordens.filter(
        status="cancelado"
    ).count()

    ordens_executadas = ordens.filter(
        status="executado"
    )

    faturamento_executado = ordens_executadas.aggregate(
        Sum("total")
    )["total__sum"] or Decimal("0.00")

    quantidade_os_executadas = ordens_executadas.count()

    if quantidade_os_executadas > 0:
        ticket_medio = faturamento_executado / quantidade_os_executadas
    else:
        ticket_medio = Decimal("0.00")

    total_valor = faturamento_executado

    return render(
        request,
        "dashboard.html",
        {
            "total_os": total_os,
            "agendadas": agendadas,
            "executadas": executadas,
            "canceladas": canceladas,
            "total_valor": total_valor,
            "faturamento_executado": faturamento_executado,
            "quantidade_os_executadas": quantidade_os_executadas,
            "ticket_medio": ticket_medio,
        }
    )