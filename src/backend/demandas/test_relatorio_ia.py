from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .constants import ITENS_PADRAO
from .models import Demanda, Evidencia, ItemChecklist
from .relatorio_ia import montar_rascunho


class RascunhoRelatorioTests(TestCase):
    """Testes da US08 e US09 - geração e revisão do relatório."""

    @classmethod
    def setUpTestData(cls):
        cls.gerente = User.objects.create_user(
            "gerente", password="SenhaTeste123!", is_staff=True
        )
        cls.fiscal = User.objects.create_user(
            "fiscal", password="SenhaTeste123!",
            first_name="Mariana", last_name="Souza"
        )
        cls.outro = User.objects.create_user(
            "outro", password="SenhaTeste123!"
        )

    def criar(self, status="andamento", **kwargs):
        params = dict(
            processo_sei="33.000123/2026-45",
            numero_os="OS-2026-0042",
            descricao="Denúncia de ausência de EPI",
            endereco="Rua A, 100",
            distrito="Distrito IV",
            bairro="Boa Vista",
            prazo=date.today() + timedelta(days=5),
            fiscal=self.fiscal,
            status=status,
        )
        params.update(kwargs)
        demanda = Demanda.objects.create(**params)
        ItemChecklist.objects.bulk_create([
            ItemChecklist(demanda=demanda, item=i)
            for i in ITENS_PADRAO
        ])
        return demanda

    def responder(self, demanda, respostas):
        for item, resposta in zip(
            demanda.itens_checklist.order_by("id"), respostas
        ):
            item.resposta = resposta
            item.save(update_fields=["resposta"])

    def test_gerador_local_monta_demanda_checklist_anotacoes_e_evidencias(self):
        demanda = self.criar(anotacoes="Responsável ausente")
        itens = list(demanda.itens_checklist.order_by("id"))
        itens[0].resposta = "nao_conforme"
        itens[0].save(update_fields=["resposta"])

        Evidencia.objects.create(
            demanda=demanda,
            tipo="anotacao",
            descricao="Sem rota de fuga"
        )
        Evidencia.objects.create(
            demanda=demanda,
            tipo="foto",
            descricao="Extintor vencido",
            latitude="-8.063100",
            longitude="-34.871100",
            arquivo=SimpleUploadedFile(
                "a.jpg", b"imagem", content_type="image/jpeg"
            )
        )

        texto = montar_rascunho(demanda)

        for esperado in [
            "RELATÓRIO TÉCNICO SANITÁRIO",
            "OS-2026-0042",
            "Mariana Souza",
            "Não conformidades constatadas",
            "Sem rota de fuga",
            "Extintor vencido",
            "GPS -8.063100, -34.871100",
            "Responsável ausente",
            "RASCUNHO",
        ]:
            self.assertIn(esperado, texto)

    def test_rascunho_tem_secoes_e_identificacao(self):
        demanda = self.criar()
        texto = montar_rascunho(demanda)

        for secao in [
            "RELATÓRIO TÉCNICO SANITÁRIO",
            "1. Identificação",
            "2. Fatos constatados",
            "3. Evidências",
            "4. Anotações do fiscal",
            "5. Recomendações e conclusão",
        ]:
            self.assertIn(secao, texto)

        self.assertIn("OS-2026-0042", texto)
        self.assertIn("33.000123/2026-45", texto)
        self.assertIn("Mariana Souza", texto)
        self.assertIn("RASCUNHO", texto)

    def test_rascunho_lista_nao_conformidades_e_recomenda_regularizacao(self):
        demanda = self.criar()
        self.responder(
            demanda,
            ["nao_conforme"] + ["conforme"] * (len(ITENS_PADRAO) - 1)
        )

        texto = montar_rascunho(demanda)

        self.assertIn(f"- {ITENS_PADRAO[0]}", texto)
        self.assertIn("regularizar", texto)

    def test_rascunho_sem_nao_conformidade(self):
        demanda = self.criar()
        self.responder(demanda, ["conforme"] * len(ITENS_PADRAO))

        texto = montar_rascunho(demanda)

        self.assertIn("Nenhuma não conformidade", texto)
        self.assertNotIn("sem resposta", texto)

    def test_rascunho_aponta_itens_sem_resposta(self):
        demanda = self.criar()
        texto = montar_rascunho(demanda)

        self.assertIn("Itens sem resposta", texto)
        self.assertIn(ITENS_PADRAO[0], texto)

    def test_rascunho_inclui_evidencias_e_gps(self):
        demanda = self.criar()

        Evidencia.objects.create(
            demanda=demanda,
            tipo="foto",
            descricao="Extintor vencido",
            latitude="-8.063100",
            longitude="-34.871100",
            arquivo=SimpleUploadedFile(
                "a.jpg", b"x", content_type="image/jpeg"
            )
        )
        Evidencia.objects.create(
            demanda=demanda,
            tipo="anotacao",
            descricao="Sem rota de fuga"
        )

        texto = montar_rascunho(demanda)

        self.assertIn("Total de evidências registradas: 2", texto)
        self.assertIn("Extintor vencido", texto)
        self.assertIn("GPS -8.063100, -34.871100", texto)

    def test_rascunho_sem_evidencias_e_sem_anotacoes(self):
        texto = montar_rascunho(self.criar())

        self.assertIn("Nenhuma evidência registrada", texto)
        self.assertIn("Sem anotações do fiscal.", texto)

    def test_rascunho_inclui_anotacoes_do_fiscal(self):
        texto = montar_rascunho(
            self.criar(anotacoes="Responsável ausente")
        )

        self.assertIn("Responsável ausente", texto)

    def test_fiscal_responsavel_acessa_tela_sem_gerar_rascunho(self):
        demanda = self.criar()
        self.client.force_login(self.fiscal)

        response = self.client.get(
            reverse("gerar_relatorio", args=[demanda.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rascunho automático")
        self.assertContains(response, "Gerar rascunho")

        demanda.refresh_from_db()
        self.assertEqual(demanda.relatorio, "")

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

        self.client.post(
            url,
            {"acao": "confirmar_revisao", "confirmar_revisao": "sim"}
        )
        demanda.refresh_from_db()

        self.assertTrue(demanda.relatorio_revisado)

    def test_outro_fiscal_nao_acessa_e_gerente_consulta_sem_mensagem_de_revisao(self):
        demanda = self.criar(
            status="concluida",
            assinatura_confirmada=True,
            homologada=True,
            relatorio="Rascunho revisado pelo fiscal"
        )

        self.client.force_login(self.outro)
        self.assertEqual(
            self.client.get(
                reverse("gerar_relatorio", args=[demanda.pk])
            ).status_code,
            404
        )

        self.client.force_login(self.gerente)
        response = self.client.get(
            reverse("gerar_relatorio", args=[demanda.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "A revisão e assinatura são realizadas pelo fiscal"
        )
        self.assertNotContains(
            response,
            "Confirmar revisão e liberar assinatura"
        )

        self.assertEqual(
            self.client.post(
                reverse("gerar_relatorio", args=[demanda.pk]),
                {
                    "acao": "confirmar_revisao",
                    "confirmar_revisao": "sim"
                }
            ).status_code,
            403
        )

    def test_relatorio_bloqueado_fora_da_fiscalizacao_para_fiscal(self):
        self.client.force_login(self.fiscal)

        for status in ("aberta", "concluida"):
            demanda = self.criar(status=status)
            self.assertEqual(
                self.client.get(
                    reverse("gerar_relatorio", args=[demanda.pk])
                ).status_code,
                302
            )

    def test_anonimo_e_redirecionado(self):
        demanda = self.criar()

        self.assertEqual(
            self.client.get(
                reverse("gerar_relatorio", args=[demanda.pk])
            ).status_code,
            302
        )
