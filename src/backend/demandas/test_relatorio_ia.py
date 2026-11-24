from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .constants import ITENS_PADRAO
from .models import Demanda, Evidencia, ItemChecklist
from .relatorio_ia import montar_rascunho


class RascunhoRelatorioTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gerente = User.objects.create_user("gerente", password="SenhaTeste123!", is_staff=True)
        cls.fiscal = User.objects.create_user("fiscal", password="SenhaTeste123!", first_name="Mariana", last_name="Souza")
        cls.outro = User.objects.create_user("outro", password="SenhaTeste123!")

    def criar(self, status="andamento", **kwargs):
        params = dict(processo_sei="33.000123/2026-45", numero_os="OS-2026-0042",
            descricao="Denúncia de ausência de EPI", endereco="Rua A, 100",
            distrito="Distrito IV", bairro="Boa Vista", prazo=date.today() + timedelta(days=5),
            fiscal=self.fiscal, status=status)
        params.update(kwargs)
        demanda = Demanda.objects.create(**params)
        ItemChecklist.objects.bulk_create([ItemChecklist(demanda=demanda, item=i) for i in ITENS_PADRAO])
        return demanda

    def test_gerador_local_monta_demanda_checklist_anotacoes_e_evidencias(self):
        demanda = self.criar(anotacoes="Responsável ausente")
        itens = list(demanda.itens_checklist.order_by("id"))
        itens[0].resposta = "nao_conforme"
        itens[0].save(update_fields=["resposta"])
        Evidencia.objects.create(demanda=demanda, tipo="anotacao", descricao="Sem rota de fuga")
        Evidencia.objects.create(demanda=demanda, tipo="foto", descricao="Extintor vencido",
            latitude="-8.063100", longitude="-34.871100",
            arquivo=SimpleUploadedFile("a.jpg", b"imagem", content_type="image/jpeg"))
        texto = montar_rascunho(demanda)
        for esperado in ["RELATÓRIO TÉCNICO SANITÁRIO", "OS-2026-0042", "Mariana Souza",
                         "Não conformidades constatadas", "Sem rota de fuga", "Extintor vencido",
                         "GPS -8.063100, -34.871100", "Responsável ausente", "RASCUNHO"]:
            self.assertIn(esperado, texto)

    def test_fiscal_gera_e_confirma_revisao_sem_chave_externa(self):
        demanda = self.criar()
        self.client.force_login(self.fiscal)
        url = reverse("gerar_relatorio", args=[demanda.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.post(url, {"acao": "gerar"})
        demanda.refresh_from_db()
        self.assertIn("RASCUNHO GERADO AUTOMATICAMENTE", demanda.relatorio)
        self.assertFalse(demanda.relatorio_revisado)
        response = self.client.get(url)
        self.assertContains(response, "gerador local não interpreta")
        self.client.post(url, {"acao": "confirmar_revisao", "confirmar_revisao": "sim"})
        demanda.refresh_from_db()
        self.assertTrue(demanda.relatorio_revisado)

    def test_outro_fiscal_nao_acessa_e_gerente_consulta_sem_mensagem_de_revisao(self):
        demanda = self.criar(status="concluida", assinatura_confirmada=True, homologada=True,
                             relatorio="Rascunho revisado pelo fiscal")
        self.client.force_login(self.outro)
        self.assertEqual(self.client.get(reverse("gerar_relatorio", args=[demanda.pk])).status_code, 404)
        self.client.force_login(self.gerente)
        response = self.client.get(reverse("gerar_relatorio", args=[demanda.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "A revisão e assinatura são realizadas pelo fiscal")
        self.assertNotContains(response, "Confirmar revisão e liberar assinatura")
        self.assertEqual(self.client.post(reverse("gerar_relatorio", args=[demanda.pk]),
                         {"acao": "confirmar_revisao", "confirmar_revisao": "sim"}).status_code, 403)

    def test_relatorio_bloqueado_fora_da_fiscalizacao_para_fiscal(self):
        self.client.force_login(self.fiscal)
        for status in ("aberta", "concluida"):
            demanda = self.criar(status=status)
            self.assertEqual(self.client.get(reverse("gerar_relatorio", args=[demanda.pk])).status_code, 302)
