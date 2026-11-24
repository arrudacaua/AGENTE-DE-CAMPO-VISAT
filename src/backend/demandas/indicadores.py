"""US11 - Indicadores do dashboard da Gerência VISAT.

Funções puras sobre os dados já cadastrados. Nada aqui depende do SEI.
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone

STATUS_ATIVOS = ("aberta", "andamento")
DIAS_ALERTA_PRAZO = 3
LIMITE_SOBRECARGA = 2  # demandas ativas no mesmo distrito


def _fiscais_ativos():
    """Usuários que atuam como fiscal (não são da Gerência)."""
    return User.objects.filter(is_active=True, is_staff=False, is_superuser=False).exclude(
        groups__name="Gerencia"
    )


def calcular_indicadores(demandas, hoje=None):
    hoje = hoje or timezone.localdate()
    limite = hoje + timedelta(days=DIAS_ALERTA_PRAZO)
    ativas = demandas.filter(status__in=STATUS_ATIVOS)

    atrasadas = ativas.filter(prazo__lt=hoje)
    vencendo = ativas.filter(prazo__gte=hoje, prazo__lte=limite)

    carga = []
    por_distrito = ativas.values("distrito").annotate(total=Count("numero")).order_by("-total", "distrito")
    maior = max((d["total"] for d in por_distrito), default=0)
    for item in por_distrito:
        carga.append({
            "distrito": item["distrito"] or "Não informado",
            "ativas": item["total"],
            "percentual": round(item["total"] * 100 / maior) if maior else 0,
            "sobrecarregado": item["total"] >= LIMITE_SOBRECARGA,
        })

    ocupados = set(ativas.exclude(fiscal=None).values_list("fiscal_id", flat=True))
    ociosos = [
        (u.get_full_name() or u.username)
        for u in _fiscais_ativos().order_by("first_name", "username")
        if u.pk not in ocupados
    ]

    concluidas = demandas.filter(status="concluida")
    return {
        "total_ativas": ativas.count(),
        "atrasadas": atrasadas.count(),
        "vencendo": vencendo.count(),
        "dias_alerta": DIAS_ALERTA_PRAZO,
        "sem_fiscal": ativas.filter(fiscal=None).count(),
        "aguardando_homologacao": concluidas.filter(homologada=False).count(),
        "homologadas": concluidas.filter(homologada=True).count(),
        "carga_distritos": carga,
        "distritos_sobrecarregados": sum(1 for c in carga if c["sobrecarregado"]),
        "limite_sobrecarga": LIMITE_SOBRECARGA,
        "fiscais_ociosos": ociosos,
    }
