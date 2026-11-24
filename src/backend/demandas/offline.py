from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .forms import EvidenciaForm
from .models import Demanda, Evidencia, ItemChecklist, RespostaOfflineRecebida
from .views import eh_gerente


@require_POST
def sincronizar_registro(request, numero, checklist=False):
    if not request.user.is_authenticated:
        return JsonResponse({"erro": "Entre novamente para sincronizar."}, status=401)
    if eh_gerente(request.user) or request.POST.get("fiscal") != str(request.user.pk):
        return JsonResponse({"erro": "Entre com a conta do fiscal responsável."}, status=403)
    try:
        identificador = UUID(request.POST.get("identificador", ""))
    except ValueError:
        return JsonResponse({"erro": "Identificador de registro inválido."}, status=400)

    with transaction.atomic():
        demandas = Demanda.objects.filter(pk=numero, fiscal=request.user)
        # Acquire a write lock before checking the receipt, including on SQLite.
        if not demandas.update(revisao=F("revisao")):
            return JsonResponse({"erro": "Demanda indisponível para este fiscal."}, status=403)
        editavel = demandas.filter(status="andamento", homologada=False)
        if checklist:
            return salvar_resposta(request, demandas, editavel, identificador)
        evidencia = Evidencia.objects.filter(identificador_offline=identificador, demanda_id=numero).first()
        if not evidencia:
            if not editavel.exists():
                return JsonResponse({"erro": "Fiscalização encerrada. A evidência continua no dispositivo."}, status=409)
            form = EvidenciaForm(request.POST, request.FILES)
            if not form.is_valid():
                return JsonResponse({"erro": "Confira os campos, o formato e o tamanho do arquivo."}, status=400)
            evidencia = form.save(commit=False)
            evidencia.demanda_id = numero
            evidencia.identificador_offline = identificador
            evidencia.latitude = request.POST.get("latitude") or None
            evidencia.longitude = request.POST.get("longitude") or None
            try:
                evidencia.full_clean()
            except ValidationError:
                return JsonResponse({"erro": "Os dados da evidência são inválidos."}, status=400)
            evidencia.save()
            demandas.update(revisao=F("revisao") + 1)
    return JsonResponse({"identificador": str(identificador), "evidencia": evidencia.pk})

def salvar_resposta(request, demandas, editavel, identificador):
    """Compara a resposta que o fiscal viu antes de aplicar a edição offline."""
    item_id = request.POST.get("item", "")
    if not item_id.isascii() or not item_id.isdigit() or len(item_id) > 18:
        return JsonResponse({"erro": "Item inválido."}, status=400)
    item = ItemChecklist.objects.filter(demanda__in=demandas, pk=item_id).first()
    if not item:
        return JsonResponse({"erro": "Item indisponível nesta demanda."}, status=400)
    recibo = {"identificador": str(identificador), "resposta": item.resposta}
    if RespostaOfflineRecebida.objects.filter(pk=identificador, item=item).exists():
        return JsonResponse(recibo)
    if not editavel.exists():
        return JsonResponse({"erro": "Fiscalização encerrada. A resposta continua no dispositivo."}, status=409)
    resposta = request.POST.get("resposta")
    anterior = request.POST.get("anterior")
    valores = dict(ItemChecklist.RESPOSTAS)
    if resposta not in valores or anterior not in {"", *valores}:
        return JsonResponse({"erro": "Resposta inválida."}, status=400)
    if item.resposta not in (anterior, resposta):
        return JsonResponse({"erro": "Este item mudou em outro dispositivo.", "atual": item.resposta}, status=409)
    if item.resposta != resposta:
        item.resposta = resposta
        item.save(update_fields=["resposta"])
        demandas.update(revisao=F("revisao") + 1)
    RespostaOfflineRecebida.objects.create(pk=identificador, item=item)
    return JsonResponse({**recibo, "resposta": resposta})
