from django.urls import path
from .views import (
    lista_servicos,
    novo_servico,
    editar_servico,
    excluir_servico,
    servicos_hoje,
    servicos_por_data,
    gerar_os_pdf,
    nova_os,
    editar_os,
    gerar_os_pdf_os,
    excluir_item,
    excluir_os,
    duplicar_os,
    lista_os,
)


urlpatterns = [

    path('', lista_os, name='lista_os'),

    path('novo/', novo_servico, name='novo_servico'),

    path('editar/<int:id>/', editar_servico, name='editar_servico'),

    path('excluir/<int:id>/', excluir_servico, name='excluir_servico'),

    path('hoje/', servicos_hoje, name='servicos_hoje'),

    path('data/', servicos_por_data, name='servicos_por_data'),

    path(
    'os/<int:id>/',
    gerar_os_pdf,
    name='os_pdf'
    ),

    path(
    'nova-os/',
    nova_os,
    name='nova_os'
    ),

    path(
    'os/<int:id>/editar/',
    editar_os,
    name='editar_os'
    ),

    path(
    'os-pdf/<int:id>/',
    gerar_os_pdf_os,
    name='os_pdf_os'
    ),

    path(
    "item/<int:id>/excluir/",
    excluir_item,
    name="excluir_item"
    ),

    path(
    "os/<int:id>/excluir/",
    excluir_os,
    name="excluir_os"
    ),

    path(
    "os/<int:id>/duplicar/",
    duplicar_os,
    name="duplicar_os"
    ),

    path(
    "os/",
    lista_os,
    name="lista_os"
    ),

    path(
    "servicos-antigo/",
    lista_servicos,
    name="lista_servicos"
    ),

]