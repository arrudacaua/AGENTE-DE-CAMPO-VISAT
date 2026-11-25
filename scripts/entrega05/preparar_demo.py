"""Prepara dados fictícios e isolados para os testes E2E da Entrega 05."""

import os
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone

from demandas.constants import ITENS_PADRAO
from demandas.models import Demanda, ItemChecklist


def obter_usuario(username, senha, **dados):
    """Cria ou atualiza um usuário de demonstração."""
    usuario, _ = User.objects.get_or_create(username=username)
    for campo, valor in dados.items():
        setattr(usuario, campo, valor)
    usuario.is_active = True
    usuario.set_password(senha)
    usuario.save()
    return usuario


def obter_demanda(processo_sei, **dados):
    """Cria ou atualiza uma demanda identificada pelo processo SEI."""
    demanda, criada = Demanda.objects.update_or_create(
        processo_sei=processo_sei,
        defaults=dados,
    )
    return demanda


def preparar_checklist(demanda, respostas=None):
    """Garante os seis itens oficiais do checklist sem duplicações."""
    respostas = respostas or {}

    for nome_item in ITENS_PADRAO:
        ItemChecklist.objects.update_or_create(
            demanda=demanda,
            item=nome_item,
            defaults={"resposta": respostas.get(nome_item, "")},
        )



def criar_demanda_demo(sufixo, fiscal, status, dias_prazo, distrito,
                       prioridade="media", **extras):
    """Cria uma demanda com identificador exclusivo da Entrega 05."""
    hoje = timezone.localdate()

    dados = {
        "numero_os": f"OS-E05-{sufixo}",
        "descricao": f"Demanda demonstrativa da Entrega 05 - {sufixo}",
        "endereco": "Rua de Demonstração, 100",
        "distrito": distrito,
        "bairro": "Bairro Demonstrativo",
        "prazo": hoje + timedelta(days=dias_prazo),
        "fiscal": fiscal,
        "status": status,
        "prioridade": prioridade,
        "assinatura_confirmada": False,
        "assinatura_nome": "",
        "assinatura_em": None,
        "homologada": False,
        "revisao": 0,
        "relatorio": "",
        "relatorio_revisado": False,
        "relatorio_revisao": 0,
        "relatorio_vinculado_sei": False,
    }
    dados.update(extras)

    return obter_demanda(f"SEI-E05-{sufixo}", **dados)


def main():

    gerente = obter_usuario(
        "gerencia_e05",
        "DemoGerenciaE05!",
        first_name="Gerência",
        last_name="Entrega 05",
        is_staff=True,
        is_superuser=False,
    )

    fiscal = obter_usuario(
        "fiscal_e05",
        "DemoFiscalE05!",
        first_name="Fiscal",
        last_name="Entrega 05",
        is_staff=False,
        is_superuser=False,
    )

    fiscal2 = obter_usuario(
        "fiscal2_e05",
        "DemoFiscal2E05!",
        first_name="Segundo Fiscal",
        last_name="Entrega 05",
        is_staff=False,
        is_superuser=False,
    )

    # US07: demanda exclusiva para testes de operação offline.
    us07 = criar_demanda_demo(
        "US07-OFFLINE", fiscal, "andamento", 10,
        "Distrito E05 Offline",
    )
    preparar_checklist(us07)

    # US06: demanda em andamento para registro de evidências.
    us06 = criar_demanda_demo(
        "US06-EVIDENCIAS", fiscal, "andamento", 10,
        "Distrito E05 Evidências",
    )
    preparar_checklist(us06)

    # US08: demanda pronta para geração do rascunho.
    us08 = criar_demanda_demo(
        "US08-RASCUNHO", fiscal, "andamento", 10,
        "Distrito E05 Relatórios",
    )
    preparar_checklist(
        us08,
        {item: "conforme" for item in ITENS_PADRAO},
    )

    # US09: relatório existente, mas ainda não revisado.
    us09 = criar_demanda_demo(
        "US09-REVISAO", fiscal, "andamento", 10,
        "Distrito E05 Revisão",
        relatorio="Rascunho demonstrativo aguardando revisão do fiscal.",
        relatorio_revisado=False,
        relatorio_revisao=0,
    )
    preparar_checklist(
        us09,
        {item: "conforme" for item in ITENS_PADRAO},
    )

    # US10: todos os requisitos atendidos, aguardando assinatura pela interface.
    us10 = criar_demanda_demo(
        "US10-ASSINATURA", fiscal, "andamento", 10,
        "Distrito E05 Assinatura",
        revisao=1,
        relatorio="Relatório técnico demonstrativo revisado e pronto para assinatura.",
        relatorio_revisado=True,
        relatorio_revisao=1,
    )
    preparar_checklist(
        us10,
        {item: "conforme" for item in ITENS_PADRAO},
    )

    # US11: indicadores do dashboard da Gerência.
    us11_atrasada = criar_demanda_demo(
        "US11-ATRASADA", fiscal, "andamento", -2,
        "Distrito E05 Norte",
    )
    us11_vencendo = criar_demanda_demo(
        "US11-VENCENDO", fiscal, "aberta", 2,
        "Distrito E05 Norte",
    )
    us11_sem_fiscal = criar_demanda_demo(
        "US11-SEM-FISCAL", None, "aberta", 10,
        "Distrito E05 Sul",
    )
    us11_homologacao = criar_demanda_demo(
        "US11-HOMOLOGACAO", fiscal2, "concluida", 10,
        "Distrito E05 Centro",
    )
    us11_homologada = criar_demanda_demo(
        "US11-HOMOLOGADA", fiscal2, "concluida", 10,
        "Distrito E05 Centro",
        homologada=True,
    )

    for demanda in (
        us11_atrasada,
        us11_vencendo,
        us11_sem_fiscal,
        us11_homologacao,
        us11_homologada,
    ):
        preparar_checklist(demanda)

    # US12: demanda aberta aguardando atribuição pela Gerência.
    us12 = criar_demanda_demo(
        "US12-ATRIBUICAO", None, "aberta", 10,
        "Distrito E05 Atribuição",
    )
    preparar_checklist(us12)

    print("Dados fictícios da Entrega 05 preparados.")
    print("Gerência:", gerente.username)
    print("Fiscal:", fiscal.username)
    print("Segundo fiscal:", fiscal2.username)
    print("Demandas preparadas:", 11)


if __name__ == "__main__":
    main()




