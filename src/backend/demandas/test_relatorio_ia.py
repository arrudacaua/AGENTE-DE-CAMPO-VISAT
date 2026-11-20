from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .constants import ITENS_PADRAO
from .models import Demanda, Evidencia, ItemChecklist
from .relatorio_ia import montar_rascunho


class RascunhoRelatorioIATests(TestCase):
    """US08 - Gerar rascunho do relatório com IA."""

    @classmethod
    def setUpTestData(cls):
        cls.gerente = User.objects.create_user("gerente", password="SenhaTeste123!", is_staff=True)
        cls.fiscal = User.objects.create_user("fiscal", password="SenhaTeste123!", first_name="Mariana", last_name="Souza")
        cls.outro = User.objects.create_user("outro", password="SenhaTeste123!")

    def criar(self, status="andamento", **kwargs):
        params = dict(
            processo_sei="33.000123/2026-45", numero_os="OS-2026-0042",
            descricao="Denúncia de ausência de EPI", endereco="Rua A, 100",
            distrito="Distrito IV", bairro="Boa Vista",
            prazo=date.today() + timedelta(days=5), fiscal=self.fiscal, status=status,
        )
        params.update(kwargs)
        d = Demanda.objects.create(**params)
        ItemChecklist.objects.bulk_create([ItemChecklist(demanda=d, item=i) for i in ITENS_PADRAO])
        return d

    def responder(self, d, respostas):
        for item, resposta in zip(d.itens_checklist.order_by("id"), respostas):
            item.resposta = resposta
            item.save(update_fields=["resposta"])

    def test_rascunho_tem_secoes_e_identificacao(self):
        d = self.criar()
        texto = montar_rascunho(d)
        for secao in ["RELATÓRIO TÉCNICO SANITÁRIO", "1. Identificação", "2. Fatos constatados",
                      "3. Evidências", "4. Anotações do fiscal", "5. Recomendações e conclusão"]:
            self.assertIn(secao, texto)
        self.assertIn("OS-2026-0042", texto)
        self.assertIn("33.000123/2026-45", texto)
        self.assertIn("Mariana Souza", texto)
        self.assertIn("RASCUNHO", texto)

    def test_rascunho_lista_nao_conformidades_e_recomenda_regularizacao(self):
        d = self.criar()
        self.responder(d, ["nao_conforme", "conforme", "conforme", "conforme", "conforme", "conforme"])
        texto = montar_rascunho(d)
        self.assertIn(f"- {ITENS_PADRAO[0]}", texto)
        self.assertIn("regularizar", texto)

    def test_rascunho_sem_nao_conformidade(self):
        d = self.criar()
        self.responder(d, ["conforme"] * len(ITENS_PADRAO))
        texto = montar_rascunho(d)
        self.assertIn("Nenhuma não conformidade", texto)
        self.assertNotIn("sem resposta", texto)

    def test_rascunho_aponta_itens_sem_resposta(self):
        d = self.criar()
        texto = montar_rascunho(d)
        self.assertIn("Itens sem resposta", texto)
        self.assertIn(ITENS_PADRAO[0], texto)

    def test_rascunho_inclui_evidencias_e_gps(self):
        d = self.criar()
        Evidencia.objects.create(demanda=d, tipo="foto", descricao="Extintor vencido",
                                 latitude="-8.063100", longitude="-34.871100",
                                 arquivo=SimpleUploadedFile("a.jpg", b"x", content_type="image/jpeg"))
        Evidencia.objects.create(demanda=d, tipo="anotacao", descricao="Sem rota de fuga")
        texto = montar_rascunho(d)
        self.assertIn("Total de evidências registradas: 2", texto)
        self.assertIn("Extintor vencido", texto)
        self.assertIn("GPS -8.063100, -34.871100", texto)

    def test_rascunho_sem_evidencias_e_sem_anotacoes(self):
        texto = montar_rascunho(self.criar())
        self.assertIn("Nenhuma evidência registrada", texto)
        self.assertIn("Sem anotações do fiscal.", texto)

    def test_rascunho_inclui_anotacoes_do_fiscal(self):
        texto = montar_rascunho(self.criar(anotacoes="Responsável ausente"))
        self.assertIn("Responsável ausente", texto)

    def test_fiscal_responsavel_ve_rascunho_sem_persistir(self):
        d = self.criar()
        self.client.force_login(self.fiscal)
        r = self.client.get(reverse("gerar_relatorio", args=[d.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Rascunho gerado automaticamente")
        self.assertContains(r, "2. Fatos constatados")
        d.refresh_from_db()
        self.assertEqual(d.relatorio, "")

    def test_outro_fiscal_nao_acessa_rascunho(self):
        d = self.criar()
        self.client.force_login(self.outro)
        self.assertEqual(self.client.get(reverse("gerar_relatorio", args=[d.pk])).status_code, 404)

    def test_rascunho_bloqueado_fora_da_fiscalizacao(self):
        self.client.force_login(self.fiscal)
        for status in ("aberta", "concluida"):
            d = self.criar(status=status)
            r = self.client.get(reverse("gerar_relatorio", args=[d.pk]))
            self.assertEqual(r.status_code, 302)

    def test_anonimo_e_redirecionado(self):
        d = self.criar()
        self.assertEqual(self.client.get(reverse("gerar_relatorio", args=[d.pk])).status_code, 302)

    def test_gerente_so_gera_apos_homologacao(self):
        d = self.criar(status="concluida", assinatura_confirmada=True)
        self.client.force_login(self.gerente)
        self.assertEqual(self.client.get(reverse("gerar_relatorio", args=[d.pk])).status_code, 302)
        d.homologada = True
        d.save()
        r = self.client.get(reverse("gerar_relatorio", args=[d.pk]))
        self.assertEqual(r.status_code, 200)
        d.refresh_from_db()
        self.assertIn("1. Identificação", d.relatorio)
