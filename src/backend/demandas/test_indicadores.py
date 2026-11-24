from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .indicadores import calcular_indicadores
from .models import Demanda


class IndicadoresDashboardTests(TestCase):
    """US11 - Acompanhar indicadores no Dashboard."""

    @classmethod
    def setUpTestData(cls):
        cls.gerente = User.objects.create_user("gerente", password="SenhaTeste123!", is_staff=True)
        cls.ana = User.objects.create_user("ana", password="SenhaTeste123!", first_name="Ana", last_name="Lima")
        cls.beto = User.objects.create_user("beto", password="SenhaTeste123!")
        cls.hoje = date.today()

    def criar(self, fiscal=None, status="aberta", dias=10, distrito="Distrito I", **kw):
        return Demanda.objects.create(
            processo_sei="SEI-1", descricao="Descrição", endereco="Rua X", bairro="B",
            distrito=distrito, prazo=self.hoje + timedelta(days=dias), fiscal=fiscal, status=status, **kw)

    def ind(self):
        return calcular_indicadores(Demanda.objects.all(), hoje=self.hoje)

    def test_sem_dados_zera_tudo(self):
        i = self.ind()
        self.assertEqual((i["total_ativas"], i["atrasadas"], i["vencendo"]), (0, 0, 0))
        self.assertEqual(i["carga_distritos"], [])
        self.assertEqual(sorted(i["fiscais_ociosos"]), ["Ana Lima", "beto"])

    def test_atrasadas_so_contam_demandas_ativas(self):
        self.criar(dias=-2)
        self.criar(dias=-1, status="andamento")
        self.criar(dias=-5, status="concluida")
        self.assertEqual(self.ind()["atrasadas"], 2)

    def test_vencendo_em_ate_tres_dias(self):
        self.criar(dias=0)
        self.criar(dias=3)
        self.criar(dias=4)
        self.criar(dias=-1)
        self.assertEqual(self.ind()["vencendo"], 2)
        self.assertEqual(self.ind()["atrasadas"], 1)

    def test_carga_por_distrito_e_sobrecarga(self):
        self.criar(distrito="Distrito I")
        self.criar(distrito="Distrito I", status="andamento")
        self.criar(distrito="Distrito II")
        self.criar(distrito="Distrito II", status="concluida")
        carga = {c["distrito"]: c for c in self.ind()["carga_distritos"]}
        self.assertEqual(carga["Distrito I"]["ativas"], 2)
        self.assertTrue(carga["Distrito I"]["sobrecarregado"])
        self.assertEqual(carga["Distrito II"]["ativas"], 1)
        self.assertFalse(carga["Distrito II"]["sobrecarregado"])
        self.assertEqual(self.ind()["distritos_sobrecarregados"], 1)

    def test_homologacao_e_sem_fiscal(self):
        self.criar(status="concluida")
        self.criar(status="concluida", homologada=True)
        self.criar(fiscal=self.ana)
        i = self.ind()
        self.assertEqual(i["aguardando_homologacao"], 1)
        self.assertEqual(i["homologadas"], 1)
        self.assertEqual(i["sem_fiscal"], 0)
        self.criar()
        self.assertEqual(self.ind()["sem_fiscal"], 1)

    def test_fiscal_ocioso_e_quem_nao_tem_demanda_ativa(self):
        self.criar(fiscal=self.ana, status="andamento")
        self.criar(fiscal=self.beto, status="concluida")
        self.assertEqual(self.ind()["fiscais_ociosos"], ["beto"])

    def test_gerencia_nao_entra_como_fiscal_ocioso(self):
        grupo = Group.objects.create(name="Gerencia")
        chefe = User.objects.create_user("chefe", password="SenhaTeste123!")
        chefe.groups.add(grupo)
        self.assertNotIn("chefe", self.ind()["fiscais_ociosos"])
        self.assertNotIn("gerente", self.ind()["fiscais_ociosos"])

    def test_dashboard_da_gerencia_exibe_indicadores(self):
        self.criar(dias=-1, distrito="Distrito III")
        self.client.force_login(self.gerente)
        r = self.client.get(reverse("inicio"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Demandas atrasadas")
        self.assertContains(r, "Demandas ativas por distrito")
        self.assertContains(r, "Distrito III")
        self.assertEqual(r.context["ind"]["atrasadas"], 1)

    def test_fiscal_nao_ve_indicadores_da_gerencia(self):
        self.client.force_login(self.ana)
        r = self.client.get(reverse("inicio"))
        self.assertNotContains(r, "Demandas ativas por distrito")
        self.assertNotIn("ind", r.context)

    def test_anonimo_vai_para_login(self):
        self.assertEqual(self.client.get(reverse("inicio")).status_code, 302)
