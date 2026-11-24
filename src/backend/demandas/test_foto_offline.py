from datetime import date
from tempfile import TemporaryDirectory
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Demanda, Evidencia


class FotoOfflineTests(TestCase):
    def setUp(self):
        media = TemporaryDirectory()
        self.addCleanup(media.cleanup)
        self.enterContext(self.settings(MEDIA_ROOT=media.name))
        self.fiscal = User.objects.create_user("fiscal")
        self.client.force_login(self.fiscal)
        self.demanda = Demanda.objects.create(fiscal=self.fiscal, prazo=date.today(), status="andamento")
        self.url = reverse("sincronizar_foto", args=[self.demanda.pk])
        self.identificador = str(uuid4())

    def enviar(self):
        return self.client.post(self.url, {
            "fiscal": str(self.fiscal.pk), "identificador": self.identificador,
            "tipo": "foto", "arquivo": SimpleUploadedFile("foto.jpg", b"foto", "image/jpeg"),
        })

    def test_reenvio_depois_de_encerrar_confirma_o_mesmo_registro(self):
        primeira = self.enviar()
        self.assertEqual(primeira.status_code, 200)
        Demanda.objects.update(status="concluida")
        self.assertEqual(self.enviar().json(), primeira.json())
        self.assertEqual(Evidencia.objects.count(), 1)
        self.demanda.refresh_from_db()
        self.assertEqual(self.demanda.revisao, 1)
        self.identificador = str(uuid4())
        self.assertEqual(self.enviar().status_code, 409)

    def test_outro_fiscal_e_sessao_expirada(self):
        self.client.force_login(User.objects.create_user("outro"))
        self.assertEqual(self.enviar().status_code, 403)
        self.client.logout()
        self.assertEqual(self.enviar().status_code, 401)
        self.assertFalse(Evidencia.objects.exists())

    def test_resposta_concorrente_e_reenvio_preservam_edicao_posterior(self):
        item = self.demanda.itens_checklist.create(item="Uso de EPI", resposta="conforme")
        url = reverse("sincronizar_resposta", args=[self.demanda.pk])
        dados = {"fiscal": self.fiscal.pk, "identificador": self.identificador,
                 "item": item.pk, "anterior": "", "resposta": "nao_conforme"}
        conflito = self.client.post(url, dados)
        self.assertEqual(conflito.status_code, 409)
        self.assertEqual(conflito.json()["atual"], "conforme")
        dados["anterior"] = "conforme"
        self.assertEqual(self.client.post(url, dados).json()["resposta"], "nao_conforme")
        item.resposta = "conforme"
        item.save()
        self.assertEqual(self.client.post(url, dados).json()["resposta"], "conforme")
        self.demanda.refresh_from_db()
        self.assertEqual(self.demanda.revisao, 1)
