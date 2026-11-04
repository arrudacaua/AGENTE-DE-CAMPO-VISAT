from urllib.parse import urlencode
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from .forms import DemandaForm, LocalizacaoForm, RespostasChecklistForm, EvidenciaForm
from .constants import ITENS_PADRAO
from .models import Demanda, ItemChecklist



def eh_gerente(user):
    return user.is_staff or user.is_superuser or user.groups.filter(name="Gerencia").exists()


def login_view(request):
    if request.user.is_authenticated:
        return redirect("inicio")
    if request.method == "POST":
        identificador = request.POST.get("username", "").strip()
        senha = request.POST.get("password", "")
        # O login padrão do Django usa username. O formulário aceita usuário ou e-mail.
        user_obj = User.objects.filter(email__iexact=identificador).first()
        username = user_obj.username if user_obj else identificador
        usuario = authenticate(request, username=username, password=senha)
        if usuario:
            login(request, usuario)
            return redirect("inicio")
        messages.error(request, "Usuário/e-mail ou senha inválidos.")
    return render(request, "demandas/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def demandas_visiveis(user):
    qs = Demanda.objects.select_related("fiscal")
    return qs if eh_gerente(user) else qs.filter(fiscal=user)


def demanda_do_fiscal(user, numero):
    if eh_gerente(user):
        raise PermissionDenied("Somente o fiscal responsável pode executar esta ação.")
    return get_object_or_404(demandas_visiveis(user), numero=numero)


def em_edicao(request, demanda):
    if demanda.status != "andamento" or demanda.homologada:
        messages.error(request, "Inicie a fiscalização antes de editar." if demanda.status == "aberta" else "Fiscalização encerrada. Disponível apenas para consulta.")
        return False
    return True


@login_required
def inicio(request):
    gerente = eh_gerente(request.user)
    qs = demandas_visiveis(request.user)
    contexto = {"gerente": gerente}
    if gerente:
        total = qs.count()
        abertas = qs.filter(status="aberta").count()
        andamento = qs.filter(status="andamento").count()
        distritos = list(qs.values("distrito").annotate(total=Count("numero")).order_by("-total", "distrito"))
        maior = max((d["total"] for d in distritos), default=0)
        for d in distritos:
            d["percentual"] = round(d["total"] * 100 / maior) if maior else 0
        contexto.update(total=total, abertas=abertas, andamento=andamento,
            concluidas=qs.filter(status="concluida").count(),
            pct_abertas=round(abertas * 100 / total) if total else 0,
            pct_andamento=round(andamento * 100 / total) if total else 0,
            por_distrito=distritos,
            por_prioridade=qs.values("prioridade").annotate(total=Count("numero")).order_by("prioridade"))
    else:
        ativas = qs.filter(status__in=["aberta", "andamento"])
        contexto.update(ativas=ativas.count(), urgente=ativas.order_by("prazo", "numero").first())
    busca = request.GET.get("q", "").strip()[:200]
    status = request.GET.get("status", "")
    if busca:
        qs = qs.filter(Q(numero__icontains=busca) | Q(numero_os__icontains=busca) |
            Q(processo_sei__icontains=busca) | Q(distrito__icontains=busca) |
            Q(bairro__icontains=busca) | Q(fiscal__username__icontains=busca))
    if status in dict(Demanda.STATUS_CHOICES):
        qs = qs.filter(status=status)
    else:
        status = ""
    qs = qs.order_by("-data_recebimento", "-numero") if gerente else qs.order_by("prazo", "numero")
    pagina = Paginator(qs, 20).get_page(request.GET.get("page"))
    contexto.update(demandas=pagina, pagina=pagina, busca=busca, filtro_status=status,
        query_filtros=urlencode({"q": busca, "status": status}))
    return render(request, "demandas/inicio.html", contexto)


@login_required
@user_passes_test(eh_gerente)
@require_http_methods(["GET", "POST"])
def criar_demanda(request):
    form = DemandaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            demanda = form.save(commit=False)
            demanda.status = "aberta"
            demanda.save()
            ItemChecklist.objects.bulk_create([ItemChecklist(demanda=demanda, item=i) for i in ITENS_PADRAO])
        messages.success(request, "Demanda criada com sucesso.")
        return redirect("detalhe_demanda", numero=demanda.numero)
    return render(request, "demandas/form.html", {"form": form, "titulo": "Nova demanda", "cadastro_demanda": True, "gerente": True})


@login_required
def detalhe_demanda(request, numero):
    demanda = get_object_or_404(demandas_visiveis(request.user), numero=numero)
    contexto = {"demanda": demanda, "gerente": eh_gerente(request.user)}
    endereco = f"{demanda.endereco}, {demanda.bairro}, Recife, PE"
    contexto["busca_mapa"] = "https://www.google.com/maps/search/?" + urlencode({"api": "1", "query": endereco})
    if demanda.tem_coordenadas:
        lat, lon = float(demanda.latitude), float(demanda.longitude)
        bbox = f"{max(-180, lon-.008):.6f},{max(-90, lat-.005):.6f},{min(180, lon+.008):.6f},{min(90, lat+.005):.6f}"
        contexto["mapa_url"] = "https://www.openstreetmap.org/export/embed.html?" + urlencode({"bbox": bbox, "layer": "mapnik", "marker": f"{lat:.6f},{lon:.6f}"})
        contexto["coordenadas"] = f"{lat:.6f}, {lon:.6f}"
        contexto["mapa_externo"] = f"https://www.openstreetmap.org/?mlat={lat:.6f}&mlon={lon:.6f}#map=17/{lat:.6f}/{lon:.6f}"
    return render(request, "demandas/detalhe.html", contexto)


@login_required
@user_passes_test(eh_gerente)
@require_http_methods(["GET", "POST"])
def editar_localizacao(request, numero):
    demanda = get_object_or_404(Demanda, numero=numero)
    if demanda.status == "concluida" or demanda.homologada:
        messages.error(request, "A localização de uma fiscalização encerrada não pode ser alterada.")
        return redirect("detalhe_demanda", numero=numero)
    form = LocalizacaoForm(request.POST or None, instance=demanda)
    if request.method == "POST" and form.is_valid():
        alteradas = Demanda.objects.filter(pk=numero, status__in=["aberta", "andamento"], homologada=False).update(**form.cleaned_data, revisao=F("revisao")+1)
        messages.success(request, "Localização salva.") if alteradas else messages.error(request, "A fiscalização foi encerrada. Localização não alterada.")
        return redirect("detalhe_demanda", numero=numero)
    return render(request, "demandas/form.html", {"form": form, "titulo": "Editar localização", "localizacao": True, "gerente": True, "demanda": demanda})


@login_required
@require_POST
def iniciar_demanda(request, numero):
    demanda = demanda_do_fiscal(request.user, numero)
    if demanda.status == "concluida" or demanda.homologada:
        messages.info(request, "Fiscalização encerrada. Disponível apenas para consulta.")
        return redirect("detalhe_demanda", numero=numero)
    alteradas = Demanda.objects.filter(pk=numero, fiscal=request.user, status="aberta", homologada=False).update(status="andamento", revisao=F("revisao")+1)
    messages.success(request, "Fiscalização iniciada." if alteradas else "Continue o preenchimento. Os registros salvos foram mantidos.")
    return redirect("checklist", numero=numero)


@login_required
@require_http_methods(["GET", "POST"])
def checklist(request, numero):
    demanda = demanda_do_fiscal(request.user, numero)
    if not em_edicao(request, demanda):
        return redirect("detalhe_demanda", numero=numero)
    itens = list(demanda.itens_checklist.order_by("id"))
    form = RespostasChecklistForm(request.POST if request.method == "POST" else None,
        itens=itens, initial={"revisao": demanda.revisao})
    status_code = 200
    if request.method == "POST":
        if form.is_valid():
            with transaction.atomic():
                atualizado = Demanda.objects.filter(pk=numero, fiscal=request.user, status="andamento", homologada=False, revisao=form.cleaned_data["revisao"]).update(revisao=F("revisao")+1)
                if atualizado:
                    for item in itens:
                        # An omitted field preserves its saved answer; empty answers remain pending.
                        if f"item_{item.pk}" in request.POST:
                            item.resposta = form.cleaned_data[f"item_{item.pk}"]
                    ItemChecklist.objects.bulk_update(itens, ["resposta"])
            if atualizado:
                messages.success(request, "Checklist salvo. Você pode sair e continuar depois.")
                return redirect("checklist", numero=numero)
            form.add_error(None, "Esta fiscalização mudou em outra aba ou foi encerrada. Reabra o checklist antes de salvar. Nenhuma resposta foi alterada.")
            status_code = 409
        else:
            status_code = 400
    respostas = [(item, form[f"item_{item.pk}"]) for item in itens]
    return render(request, "demandas/checklist.html", {"demanda": demanda, "itens": itens, "respostas": respostas, "form": form, "gerente": False}, status=status_code)


@login_required
@require_http_methods(["GET", "POST"])
def adicionar_evidencia(request, numero):
    demanda = demanda_do_fiscal(request.user, numero)
    if not em_edicao(request, demanda):
        return redirect("detalhe_demanda", numero=numero)
    form = EvidenciaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            atualizado = Demanda.objects.filter(pk=numero, fiscal=request.user, status="andamento", homologada=False).update(revisao=F("revisao")+1)
            if atualizado:
                evidencia = form.save(commit=False)
                evidencia.demanda = demanda
                evidencia.save()
        messages.success(request, "Evidência registrada.") if atualizado else messages.error(request, "A fiscalização foi encerrada. Registro não alterado.")
        return redirect("detalhe_demanda", numero=numero)
    return render(request, "demandas/form.html", {"form": form, "titulo": "Registrar evidência", "demanda": demanda, "gerente": False})


@login_required
@require_POST
def concluir_demanda(request, numero):
    demanda = demanda_do_fiscal(request.user, numero)
    if not em_edicao(request, demanda):
        return redirect("detalhe_demanda", numero=numero)
    with transaction.atomic():
        atualizado = Demanda.objects.filter(pk=numero, fiscal=request.user, status="andamento", homologada=False).update(revisao=F("revisao")+1)
        if atualizado:
            itens = list(ItemChecklist.objects.filter(demanda_id=numero))
            completo = set(ITENS_PADRAO).issubset({i.item for i in itens}) and all(i.resposta in dict(ItemChecklist.RESPOSTAS) for i in itens)
            if not completo:
                messages.error(request, "Responda todos os seis itens do checklist antes de concluir.")
                transaction.set_rollback(True)
            elif request.POST.get("confirmar") != "sim":
                messages.error(request, "Confirme a revisão dos registros para concluir.")
                transaction.set_rollback(True)
            else:
                Demanda.objects.filter(pk=numero).update(status="concluida", assinatura_confirmada=True)
                messages.success(request, "Fiscalização concluída. Aguardando homologação. A confirmação é demonstrativa.")
    return redirect("detalhe_demanda", numero=numero)


@login_required
@user_passes_test(eh_gerente)
@require_POST
def homologar_demanda(request, numero):
    demanda = get_object_or_404(Demanda, numero=numero)
    if request.method == "POST":
        if demanda.status == "concluida" and demanda.assinatura_confirmada:
            demanda.homologada = True
            demanda.save()
            messages.success(request, "Fiscalização homologada.")
        else:
            messages.error(request, "A demanda precisa estar concluída e confirmada pelo fiscal.")
    return redirect("detalhe_demanda", numero=numero)


@login_required
@user_passes_test(eh_gerente)
def gerar_relatorio(request, numero):
    demanda = get_object_or_404(Demanda, numero=numero)
    if not demanda.homologada:
        messages.error(request, "O relatório só pode ser gerado após a homologação.")
        return redirect("detalhe_demanda", numero=numero)
    checklist_texto = "\n".join(
        f"- {item.item}: {item.get_resposta_display() if item.resposta else 'Sem resposta'}"
        for item in demanda.itens_checklist.all()
    )
    demanda.relatorio = (
        "RELATÓRIO TÉCNICO SANITÁRIO - RASCUNHO DEMONSTRATIVO\n"
        f"Demanda: {demanda.numero}\nProcesso SEI: {demanda.processo_sei}\n"
        f"Descrição: {demanda.descricao}\nEndereço: {demanda.endereco}, "
        f"{demanda.bairro} - {demanda.distrito}\nFiscal: {demanda.fiscal}\n"
        f"Prazo: {demanda.prazo}\n\nChecklist:\n{checklist_texto}\n\n"
        f"Anotações: {demanda.anotacoes}\n\n"
        "Documento demonstrativo. Deve ser revisado por servidor competente."
    )
    demanda.save()
    return render(request, "demandas/relatorio.html", {"demanda": demanda, "gerente": True})


@login_required
@user_passes_test(eh_gerente)
@require_POST
def vincular_sei(request, numero):
    demanda = get_object_or_404(Demanda, numero=numero)
    if request.method == "POST":
        if demanda.relatorio:
            demanda.relatorio_vinculado_sei = True
            demanda.save()
            messages.success(request, "Vínculo conceitual registrado. Nenhuma integração real com o SEI foi realizada.")
        else:
            messages.error(request, "Gere o relatório antes de registrar o vínculo.")
    return redirect("detalhe_demanda", numero=numero)
