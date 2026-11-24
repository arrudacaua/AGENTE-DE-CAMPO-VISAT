from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .forms import EvidenciaForm
from .models import Demanda, Evidencia
from .views import eh_gerente


@require_POST
def sincronizar_foto(request, numero):
    if not request.user.is_authenticated:
        return JsonResponse({"erro": "Entre novamente para sincronizar."}, status=401)
    if eh_gerente(request.user) or request.POST.get("fiscal") != str(request.user.pk):
        return JsonResponse({"erro": "Entre com a conta do fiscal responsável."}, status=403)
    try:
        identificador = UUID(request.POST.get("identificador", ""))
    except ValueError:
        return JsonResponse({"erro": "Identificador de foto inválido."}, status=400)

    with transaction.atomic():
        demandas = Demanda.objects.filter(pk=numero, fiscal=request.user)
        # Acquire a write lock before checking the receipt, including on SQLite.
        if not demandas.update(revisao=F("revisao")):
            return JsonResponse({"erro": "Demanda indisponível para este fiscal."}, status=403)
        foto = Evidencia.objects.filter(identificador_offline=identificador, demanda_id=numero).first()
        if not foto:
            if not demandas.filter(status="andamento", homologada=False).exists():
                return JsonResponse({"erro": "Fiscalização encerrada. A foto continua no dispositivo."}, status=409)
            form = EvidenciaForm(request.POST, request.FILES)
            if request.POST.get("tipo") != "foto" or not form.is_valid():
                return JsonResponse({"erro": "Confira o formato e o tamanho da foto."}, status=400)
            foto = form.save(commit=False)
            foto.demanda_id = numero
            foto.identificador_offline = identificador
            foto.latitude = request.POST.get("latitude") or None
            foto.longitude = request.POST.get("longitude") or None
            try:
                foto.full_clean()
            except ValidationError:
                return JsonResponse({"erro": "Os dados da foto são inválidos."}, status=400)
            foto.save()
            demandas.update(revisao=F("revisao") + 1)
    return JsonResponse({"identificador": str(identificador), "evidencia": foto.pk})
