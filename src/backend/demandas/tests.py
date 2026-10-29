from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from .models import Demanda, ItemChecklist
from .constants import ITENS_PADRAO
from .forms import DemandaForm


class FluxoFiscalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gerente = User.objects.create_user('gerente', password='SenhaTeste123!', is_staff=True)
        cls.a = User.objects.create_user('fiscal_a', password='SenhaTeste123!')
        cls.b = User.objects.create_user('fiscal_b', password='SenhaTeste123!')

    def setUp(self):
        self.client.force_login(self.a)
        self.d = self.criar(self.a)

    def criar(self, fiscal, status='aberta', **kwargs):
        params = dict(processo_sei='SEI-TESTE-001', numero_os='OS-2026-001', descricao='Descrição completa da inspeção',
            endereco='Rua de teste, 100', distrito='Distrito I', bairro='Bairro teste',
            prazo=date.today()+timedelta(days=7), fiscal=fiscal, status=status)
        params.update(kwargs)
        d = Demanda.objects.create(**params)
        ItemChecklist.objects.bulk_create([ItemChecklist(demanda=d, item=i) for i in ITENS_PADRAO])
        return d

    def url(self, acao='detalhe_demanda', d=None):
        return reverse(acao, args=[(d or self.d).pk])

    def iniciar(self):
        return self.client.post(self.url('iniciar_demanda'))

    def respostas(self, d=None):
        d = d or self.d
        d.refresh_from_db()
        return {'revisao': d.revisao, **{f'item_{i.pk}': 'conforme' for i in d.itens_checklist.all()}}

    def completar(self):
        self.iniciar()
        self.client.post(self.url('checklist'), self.respostas())
        return self.client.post(self.url('concluir_demanda'), {'confirmar': 'sim'})

    def test_inicio_contagem_prazo_e_isolamento(self):
        urgente = self.criar(self.a, 'andamento', prazo=date.today()-timedelta(days=1))
        self.criar(self.a, 'concluida', prazo=date.today()-timedelta(days=9))
        self.criar(self.b, processo_sei='SEGREDO-B', prazo=date.today()-timedelta(days=20))
        r = self.client.get(reverse('inicio'))
        self.assertEqual(r.context['ativas'], 2)
        self.assertEqual(r.context['urgente'].pk, urgente.pk)
        self.assertNotContains(r, 'SEGREDO-B')
        for value in ['OS-2026-001', 'SEI-TESTE-001', 'Distrito I', 'Bairro teste', 'Média', 'Em aberto']:
            self.assertContains(r, value)
        self.assertContains(r, self.url())

    def test_sem_demandas(self):
        self.client.force_login(self.b)
        r = self.client.get(reverse('inicio'))
        self.assertEqual(r.context['ativas'], 0)
        self.assertIsNone(r.context['urgente'])
        self.assertContains(r, 'Nenhuma demanda')

    def test_pesquisa_e_paginacao_com_mais_de_oito(self):
        for n in range(22): self.criar(self.a, processo_sei=f'EXTRA-{n}')
        alvo = self.criar(self.a, processo_sei='LOCALIZAR-ULTIMA')
        self.criar(self.b, processo_sei='EXCLUSIVA-B')
        for user in [self.a, self.gerente]:
            self.client.force_login(user)
            r = self.client.get(reverse('inicio'), {'q': 'LOCALIZAR-ULTIMA'})
            self.assertEqual([d.pk for d in r.context['demandas']], [alvo.pk])
            self.assertTrue(self.client.get(reverse('inicio')).context['pagina'].has_next())
        self.client.force_login(self.a)
        self.assertNotContains(self.client.get(reverse('inicio'), {'q': 'EXCLUSIVA-B'}), 'SEI: EXCLUSIVA-B')
        r = self.client.get(reverse('inicio'), {'status': 'concluida', 'page': 'invalid'})
        self.assertEqual(len(r.context['demandas']), 0)
        self.assertEqual(r.context['ativas'], 24)

    def test_detalhe_completo_sem_fiscal(self):
        self.client.force_login(self.gerente)
        d = self.criar(None)
        for url in [self.url(d=d), reverse('inicio')]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200)
            self.assertContains(r, 'Não atribuído')
        r = self.client.get(self.url(d=d))
        for texto in [d.descricao, d.endereco, d.bairro, d.distrito, d.processo_sei, d.numero_os, 'Coordenadas não cadastradas']:
            self.assertContains(r, texto)

    def test_mapa_coordenadas_reais_inclui_zero(self):
        for lat, lon in [('-8.060000', '-34.880000'), ('0', '0')]:
            self.d.latitude, self.d.longitude = Decimal(lat), Decimal(lon)
            self.d.save()
            r = self.client.get(self.url())
            self.assertContains(r, 'map-dialog')
            self.assertContains(r, 'openstreetmap.org/export/embed.html')
            self.assertEqual(r.context['coordenadas'], f'{float(lat):.6f}, {float(lon):.6f}')

    def test_validacao_localizacao(self):
        self.client.force_login(self.gerente)
        base = {'endereco': 'Rua nova', 'bairro': 'Centro', 'distrito': 'II'}
        for coords in [{'latitude': '91', 'longitude': '0'}, {'latitude': '0', 'longitude': '-181'}, {'latitude': '-8', 'longitude': ''}, {'latitude': 'NaN', 'longitude': '0'}]:
            r = self.client.post(self.url('editar_localizacao'), {**base, **coords})
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.context['form'].errors)
        self.d.refresh_from_db()
        self.assertIsNone(self.d.latitude)
        r = self.client.post(self.url('editar_localizacao'), {**base, 'latitude': '-8.05', 'longitude': '-34.9'})
        self.assertEqual(r.status_code, 302)
        self.d.refresh_from_db(); self.assertEqual(self.d.latitude, Decimal('-8.05'))

    def test_acesso_outro_fiscal_e_anonimo(self):
        outro = self.criar(self.b, 'andamento')
        for acao in ['detalhe_demanda', 'checklist', 'adicionar_evidencia', 'iniciar_demanda', 'concluir_demanda']:
            for method in ['get', 'post']:
                r = getattr(self.client, method)(self.url(acao, outro))
                self.assertIn(r.status_code, [404, 405])
        anon = Client()
        for acao in ['detalhe_demanda', 'checklist', 'iniciar_demanda', 'concluir_demanda', 'editar_localizacao']:
            self.assertEqual(anon.get(self.url(acao)).status_code, 302)
        self.client.force_login(self.gerente)
        self.assertEqual(self.client.post(self.url('iniciar_demanda')).status_code, 403)

    def test_iniciar_post_csrf_retomar_sem_duplicar(self):
        self.assertEqual(self.client.get(self.url('iniciar_demanda')).status_code, 405)
        secure = Client(enforce_csrf_checks=True); secure.force_login(self.a)
        self.assertEqual(secure.post(self.url('iniciar_demanda')).status_code, 403)
        self.assertRedirects(self.iniciar(), self.url('checklist'))
        self.d.refresh_from_db(); self.assertEqual(self.d.status, 'andamento')
        self.assertRedirects(self.iniciar(), self.url('checklist'))
        self.assertEqual(self.d.itens_checklist.count(), 6)

    def test_nao_edita_antes_de_iniciar(self):
        for acao in ['checklist', 'adicionar_evidencia', 'concluir_demanda']:
            self.assertEqual(self.client.post(self.url(acao), {'confirmar': 'sim', **self.respostas()}).status_code, 302)
        self.d.refresh_from_db(); self.assertEqual(self.d.status, 'aberta')
        self.assertEqual(self.d.itens_checklist.exclude(resposta='').count(), 0)
        self.assertEqual(self.d.evidencias.count(), 0)

    def test_salvar_alterar_persistir_checklist(self):
        self.iniciar()
        r = self.client.get(self.url('checklist'))
        for item in ITENS_PADRAO: self.assertContains(r, item)
        self.assertEqual(r.content.decode().count('type="radio"'), 12)
        self.assertRedirects(self.client.post(self.url('checklist'), self.respostas()), self.url('checklist'))
        data = self.respostas(); first = self.d.itens_checklist.first(); data[f'item_{first.pk}'] = 'nao_conforme'
        self.client.post(self.url('checklist'), data)
        self.client.logout(); self.assertTrue(self.client.login(username='fiscal_a', password='SenhaTeste123!'))
        r = self.client.get(self.url('checklist')); self.assertEqual(r.context['form'][f'item_{first.pk}'].value(), 'nao_conforme')
        self.assertContains(r, 'checked')

    def test_invalido_estrangeiro_e_multiplas_respostas_atomico(self):
        self.iniciar()
        data = self.respostas(); primeiro = self.d.itens_checklist.first()
        for extra in [{f'item_{primeiro.pk}': 'invalido'}, {'item_999999': 'conforme'}, {f'item_{primeiro.pk}': ['conforme', 'nao_conforme']}]:
            self.assertEqual(self.client.post(self.url('checklist'), {**data, **extra}).status_code, 400)
            self.assertEqual(self.d.itens_checklist.exclude(resposta='').count(), 0)

    def test_aba_antiga_nao_sobrescreve(self):
        self.iniciar(); data = self.respostas()
        self.client.post(self.url('checklist'), data)
        data[f'item_{self.d.itens_checklist.first().pk}'] = 'nao_conforme'
        self.assertEqual(self.client.post(self.url('checklist'), data).status_code, 409)
        self.assertEqual(self.d.itens_checklist.first().resposta, 'conforme')

    def test_resposta_omitida_preserva(self):
        self.iniciar(); self.client.post(self.url('checklist'), self.respostas())
        self.d.refresh_from_db()
        self.client.post(self.url('checklist'), {'revisao': self.d.revisao})
        self.assertEqual(self.d.itens_checklist.filter(resposta='conforme').count(), 6)

    def test_conclusao_exige_seis_respostas_e_confirmacao(self):
        self.iniciar(); self.client.post(self.url('concluir_demanda'), {'confirmar': 'sim'})
        self.d.refresh_from_db(); self.assertEqual(self.d.status, 'andamento')
        self.client.post(self.url('checklist'), self.respostas())
        self.client.post(self.url('concluir_demanda'), {})
        self.d.refresh_from_db(); self.assertEqual(self.d.status, 'andamento')
        self.d.itens_checklist.first().delete()
        self.client.post(self.url('concluir_demanda'), {'confirmar': 'sim'})
        self.d.refresh_from_db(); self.assertEqual(self.d.status, 'andamento')

    def test_concluida_bloqueia_posts_e_homologacao(self):
        self.completar(); self.d.refresh_from_db()
        self.assertEqual(self.d.status, 'concluida')
        self.assertTrue(self.d.assinatura_confirmada)
        r = self.client.get(self.url()); self.assertContains(r, 'Aguardando homologação')
        self.assertNotContains(r, 'Continuar Fiscalização'); self.assertNotContains(r, 'Salvar checklist')
        antes = list(self.d.itens_checklist.values_list('resposta', flat=True))
        for acao in ['checklist', 'iniciar_demanda', 'adicionar_evidencia', 'concluir_demanda']:
            self.client.post(self.url(acao), {'confirmar': 'sim', 'tipo': 'foto', 'descricao': 'indevida', **self.respostas()})
        self.assertEqual(list(self.d.itens_checklist.values_list('resposta', flat=True)), antes)
        self.assertEqual(self.d.evidencias.count(), 0)
        self.client.force_login(self.gerente)
        self.client.post(self.url('editar_localizacao'), {'endereco': 'INDEVIDO', 'bairro': 'B', 'distrito': 'D'})
        self.d.refresh_from_db(); self.assertNotEqual(self.d.endereco, 'INDEVIDO')
        self.client.post(self.url('homologar_demanda'))
        self.d.refresh_from_db(); self.assertTrue(self.d.homologada)
        self.assertEqual(self.client.get(self.url('gerar_relatorio')).status_code, 200)
        self.client.force_login(self.a)
        r = self.client.get(self.url()); self.assertContains(r, 'Fiscalização homologada'); self.assertNotContains(r, 'Aguardando homologação')

    def test_cadastro_status_forjado_e_fiscais_validos(self):
        grupo = Group.objects.create(name='Gerencia'); self.b.groups.add(grupo)
        self.assertNotIn(self.b, DemandaForm().fields['fiscal'].queryset)
        self.client.force_login(self.gerente)
        r = self.client.post(reverse('criar_demanda'), {'processo_sei': 'NOVO', 'descricao': 'Teste', 'endereco': 'Rua', 'distrito': 'I', 'bairro': 'B', 'prazo': '2027-01-01', 'fiscal': self.a.pk, 'status': 'concluida', 'prioridade': 'alta'})
        self.assertEqual(r.status_code, 302)
        d = Demanda.objects.get(processo_sei='NOVO')
        self.assertEqual(d.status, 'aberta'); self.assertEqual(d.itens_checklist.count(), 6)


from django.test import TransactionTestCase
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


class MigracaoLegadaTests(TransactionTestCase):
    def test_preserva_registros_e_completa_itens_sem_duplicar(self):
        executor = MigrationExecutor(connection)
        anterior = [('demandas', '0001_initial')]
        atual = [('demandas', '0003_completar_checklist')]
        executor.migrate(anterior)
        try:
            apps = executor.loader.project_state(anterior).apps
            Usuario = apps.get_model('auth', 'User')
            DemandaAntiga = apps.get_model('demandas', 'Demanda')
            ItemAntigo = apps.get_model('demandas', 'ItemChecklist')
            u = Usuario.objects.create(username='legado', password='hash-preservado')
            base = dict(processo_sei='LEGADO', descricao='Preservar', endereco='Rua', bairro='B', distrito='D', prazo=date.today(), fiscal_id=u.pk)
            d = DemandaAntiga.objects.create(**base, status='andamento')
            ItemAntigo.objects.create(demanda=d, item='Uso de EPI', resposta='nao_conforme')
            encerrada = DemandaAntiga.objects.create(**base, status='concluida', assinatura_confirmada=True, homologada=True)
            ItemAntigo.objects.create(demanda=encerrada, item='Uso de EPI', resposta='conforme')
            executor = MigrationExecutor(connection); executor.migrate(atual)
            self.assertEqual(User.objects.get(pk=u.pk).password, 'hash-preservado')
            nova = Demanda.objects.get(pk=d.pk)
            self.assertEqual(nova.processo_sei, 'LEGADO')
            self.assertEqual(nova.itens_checklist.count(), 6)
            self.assertEqual(nova.itens_checklist.get(item='Uso de EPI').resposta, 'nao_conforme')
            self.assertEqual(nova.numero_os, '')
            self.assertIsNone(nova.latitude)
            self.assertEqual(Demanda.objects.get(pk=encerrada.pk).itens_checklist.count(), 1)
            MigrationExecutor(connection).migrate(atual)
            self.assertEqual(nova.itens_checklist.count(), 6)
        finally:
            MigrationExecutor(connection).migrate(atual)
