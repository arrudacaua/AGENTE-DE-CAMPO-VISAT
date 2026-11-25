from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User, Group
from django.urls import reverse
from .models import Demanda, ItemChecklist, Evidencia
from unittest.mock import patch
from .constants import ITENS_PADRAO
from .forms import DemandaForm, EvidenciaForm


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
        self.d.refresh_from_db()
        self.d.relatorio = 'RASCUNHO DE TESTE'
        self.d.relatorio_revisao = self.d.revisao
        self.d.relatorio_revisado = True
        self.d.save(update_fields=['relatorio', 'relatorio_revisao', 'relatorio_revisado'])
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
        for acao in ['detalhe_demanda', 'checklist', 'adicionar_evidencia', 'iniciar_demanda', 'concluir_demanda', 'gerar_relatorio']:
            for method in ['get', 'post']:
                r = getattr(self.client, method)(self.url(acao, outro))
                self.assertIn(r.status_code, [404, 405])
        anon = Client()
        for acao in ['detalhe_demanda', 'checklist', 'iniciar_demanda', 'concluir_demanda', 'editar_localizacao']:
            self.assertEqual(anon.get(self.url(acao)).status_code, 302)
        self.client.force_login(self.gerente)
        self.assertEqual(self.client.post(self.url('iniciar_demanda')).status_code, 403)

    @patch('demandas.views.montar_rascunho', return_value='RASCUNHO GERADO AUTOMATICAMENTE')
    def test_fiscal_gera_relatorio_confirma_revisao_e_assina(self, montar):
        self.d.status = 'andamento'
        self.d.save(update_fields=['status'])
        url = self.url('gerar_relatorio')
        resposta = self.client.get(url)
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Rascunho automático')
        self.assertContains(resposta, 'gerador local não interpreta')
        self.client.post(url, {'acao': 'gerar'})
        montar.assert_called_once()
        self.d.refresh_from_db()
        self.assertEqual(self.d.relatorio, 'RASCUNHO GERADO AUTOMATICAMENTE')
        self.assertFalse(self.d.relatorio_revisado)
        self.assertEqual(self.client.post(self.url('concluir_demanda'), {'confirmar': 'sim'}).status_code, 302)
        self.d.refresh_from_db()
        self.assertEqual(self.d.status, 'andamento')
        self.assertEqual(self.client.post(url, {'acao': 'confirmar_revisao', 'confirmar_revisao': 'sim'}).status_code, 302)
        self.d.refresh_from_db()
        self.assertTrue(self.d.relatorio_revisado)
        self.assertEqual(self.client.post(self.url('concluir_demanda'), {'confirmar': 'sim'}).status_code, 302)
        self.d.refresh_from_db()
        self.assertEqual(self.d.status, 'andamento')  # checklist ainda incompleto
        montar.assert_called_once()

    def test_alteracao_dos_dados_invalida_revisao_e_bloqueia_assinatura(self):
        self.d.status = 'andamento'
        self.d.relatorio = 'Rascunho'
        self.d.relatorio_revisado = True
        self.d.relatorio_revisao = self.d.revisao
        self.d.save()
        self.d.revisao += 1
        self.d.save(update_fields=['revisao'])
        self.client.post(self.url('concluir_demanda'), {'confirmar': 'sim'})
        self.d.refresh_from_db()
        self.assertEqual(self.d.status, 'andamento')

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
        self.d.relatorio = 'Relatório de teste gerado pelo fiscal.'
        self.d.save(update_fields=['relatorio'])
        self.assertEqual(self.client.get(self.url('gerar_relatorio')).status_code, 200)
        self.assertEqual(self.client.post(self.url('gerar_relatorio'), {'acao': 'confirmar_revisao', 'confirmar_revisao': 'sim'}).status_code, 403)
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


    def test_cadastro_demanda_restrito_a_gerencia(self):
        self.client.logout()

        resposta = self.client.get(reverse('criar_demanda'))
        self.assertEqual(resposta.status_code, 302)

        self.client.force_login(self.a)
        resposta = self.client.get(reverse('criar_demanda'))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn('/login/', resposta.url)

    def test_vincular_sei_exige_gerente_e_relatorio(self):
        url = self.url('vincular_sei')

        # Fiscal não pode registrar o vínculo.
        resposta = self.client.post(url)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn('/login/', resposta.url)

        # Gerente sem relatório não pode registrar o vínculo.
        self.client.force_login(self.gerente)
        resposta = self.client.post(url)
        self.assertRedirects(resposta, self.url())

        self.d.refresh_from_db()
        self.assertFalse(self.d.relatorio_vinculado_sei)

    def test_vincular_sei_registra_vinculo_conceitual(self):
        self.d.relatorio = "Relatório técnico de teste."
        self.d.save()

        self.client.force_login(self.gerente)
        resposta = self.client.post(self.url('vincular_sei'))

        self.assertRedirects(resposta, self.url())

        self.d.refresh_from_db()
        self.assertTrue(self.d.relatorio_vinculado_sei)
        self.assertEqual(self.d.processo_sei, 'SEI-TESTE-001')


    def test_logout_bloqueia_get_sem_encerrar_sessao(self):
        resposta = self.client.get(reverse('logout'))

        self.assertEqual(resposta.status_code, 405)

        # O usuário continua autenticado após a tentativa por GET.
        resposta_inicio = self.client.get(reverse('inicio'))
        self.assertEqual(resposta_inicio.status_code, 200)

    def test_logout_post_encerra_sessao(self):
        resposta = self.client.post(reverse('logout'))

        self.assertRedirects(resposta, reverse('login'))

        # Após o logout, o usuário não consegue acessar área restrita.
        resposta_inicio = self.client.get(reverse('inicio'))
        self.assertEqual(resposta_inicio.status_code, 302)
        self.assertIn(reverse('login'), resposta_inicio.url)

    def test_logout_post_sem_csrf_e_bloqueado(self):
        cliente_seguro = Client(enforce_csrf_checks=True)
        cliente_seguro.force_login(self.a)

        resposta = cliente_seguro.post(reverse('logout'))

        self.assertEqual(resposta.status_code, 403)

        # A sessão continua ativa porque o POST foi rejeitado.
        resposta_inicio = cliente_seguro.get(reverse('inicio'))
        self.assertEqual(resposta_inicio.status_code, 200)


from django.test import TransactionTestCase
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


class MigracaoLegadaTests(TransactionTestCase):
    def test_preserva_registros_e_completa_itens_sem_duplicar(self):
        executor = MigrationExecutor(connection)
        anterior = [('demandas', '0001_initial')]
        atual = [('demandas', '0007_demanda_relatorio_revisado_demanda_relatorio_revisao')]
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

class EvidenciasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gerente = User.objects.create_user(
            'gerente_evidencias',
            password='SenhaTeste123!',
            is_staff=True
        )
        cls.fiscal = User.objects.create_user(
            'fiscal_evidencias',
            password='SenhaTeste123!'
        )
        cls.outro_fiscal = User.objects.create_user(
            'outro_fiscal_evidencias',
            password='SenhaTeste123!'
        )

    def setUp(self):
        self.client.force_login(self.fiscal)

        self.demanda = Demanda.objects.create(
            processo_sei='SEI-EVIDENCIA-001',
            numero_os='OS-EVIDENCIA-001',
            descricao='Teste de evidências',
            endereco='Rua de teste',
            distrito='Distrito I',
            bairro='Centro',
            prazo=date.today() + timedelta(days=7),
            fiscal=self.fiscal,
            status='andamento'
        )

        ItemChecklist.objects.bulk_create([
            ItemChecklist(demanda=self.demanda, item=item)
            for item in ITENS_PADRAO
        ])

    def url(self, acao='detalhe_demanda'):
        return reverse(acao, args=[self.demanda.pk])

    def arquivo(self, nome='foto.jpg', conteudo=b'conteudo', tipo='image/jpeg'):
        return SimpleUploadedFile(
            nome,
            conteudo,
            content_type=tipo
        )

    def test_registrar_foto_vinculada_a_demanda(self):
        resposta = self.client.post(
            self.url('adicionar_evidencia'),
            {
                'tipo': 'foto',
                'descricao': 'Foto da fachada',
                'arquivo': self.arquivo(),
                'latitude': '-8.060000',
                'longitude': '-34.880000',
            }
        )

        self.assertRedirects(resposta, self.url())

        evidencia = Evidencia.objects.get(demanda=self.demanda)

        self.assertEqual(evidencia.tipo, 'foto')
        self.assertEqual(evidencia.descricao, 'Foto da fachada')
        self.assertEqual(evidencia.latitude, Decimal('-8.060000'))
        self.assertEqual(evidencia.longitude, Decimal('-34.880000'))
        self.assertTrue(evidencia.arquivo)

    def test_registrar_video_audio_e_anotacao(self):
        casos = [
            {
                'tipo': 'video',
                'descricao': 'Vídeo da inspeção',
                'arquivo': self.arquivo(
                    'inspecao.mp4',
                    b'video-teste',
                    'video/mp4'
                ),
            },
            {
                'tipo': 'audio',
                'descricao': 'Áudio da inspeção',
                'arquivo': self.arquivo(
                    'relato.mp3',
                    b'audio-teste',
                    'audio/mpeg'
                ),
            },
            {
                'tipo': 'anotacao',
                'descricao': 'Constatação realizada no local',
            },
        ]

        for caso in casos:
            resposta = self.client.post(
                self.url('adicionar_evidencia'),
                caso
            )
            self.assertRedirects(resposta, self.url())

        self.assertEqual(self.demanda.evidencias.count(), 3)
        self.assertTrue(
            self.demanda.evidencias.filter(tipo='video').exists()
        )
        self.assertTrue(
            self.demanda.evidencias.filter(tipo='audio').exists()
        )
        self.assertTrue(
            self.demanda.evidencias.filter(tipo='anotacao').exists()
        )

    def test_validacoes_do_formulario_de_evidencias(self):
        casos_invalidos = [
            {
                'tipo': 'foto',
                'arquivo': self.arquivo(
                    'documento.txt',
                    b'texto',
                    'text/plain'
                ),
            },
            {
                'tipo': 'foto',
                'arquivo': self.arquivo(
                    'foto.jpg',
                    b'conteudo',
                    'text/plain'
                ),
            },
            {
                'tipo': 'foto',
                'arquivo': self.arquivo(
                    'grande.jpg',
                    b'x' * (50 * 1024 * 1024 + 1),
                    'image/jpeg'
                ),
            },
        ]

        for dados in casos_invalidos:
            with self.subTest(dados=dados['arquivo'].name):
                form = EvidenciaForm(
                    data={
                        'tipo': dados['tipo'],
                        'descricao': 'Teste de validação',
                    },
                    files={'arquivo': dados['arquivo']}
                )
                self.assertFalse(form.is_valid())

        form_sem_arquivo = EvidenciaForm(
            data={
                'tipo': 'foto',
                'descricao': 'Foto sem arquivo',
            }
        )
        self.assertFalse(form_sem_arquivo.is_valid())

        form_anotacao_com_arquivo = EvidenciaForm(
            data={
                'tipo': 'anotacao',
                'descricao': 'Anotação com arquivo indevido',
            },
            files={
                'arquivo': self.arquivo()
            }
        )
        self.assertFalse(form_anotacao_com_arquivo.is_valid())

    def test_acesso_a_evidencias_restrito_ao_fiscal_responsavel(self):
        dados = {
            'tipo': 'foto',
            'descricao': 'Foto não autorizada',
            'arquivo': self.arquivo(),
        }

        self.client.force_login(self.outro_fiscal)
        resposta = self.client.post(
            self.url('adicionar_evidencia'),
            dados
        )
        self.assertEqual(resposta.status_code, 404)

        self.client.force_login(self.gerente)
        resposta = self.client.post(
            self.url('adicionar_evidencia'),
            dados
        )
        self.assertEqual(resposta.status_code, 403)

        cliente_anonimo = Client()
        resposta = cliente_anonimo.get(
            self.url('adicionar_evidencia')
        )
        self.assertEqual(resposta.status_code, 302)

        self.assertEqual(self.demanda.evidencias.count(), 0)

    def test_excluir_audio_por_post(self):
        audio = Evidencia.objects.create(
            demanda=self.demanda,
            tipo='audio',
            descricao='Áudio para excluir',
            arquivo=self.arquivo(
                'relato.mp3',
                b'audio-teste',
                'audio/mpeg'
            )
        )

        resposta = self.client.get(
            reverse(
                'excluir_audio',
                args=[self.demanda.pk, audio.pk]
            )
        )
        self.assertEqual(resposta.status_code, 405)
        self.assertTrue(Evidencia.objects.filter(pk=audio.pk).exists())

        resposta = self.client.post(
            reverse(
                'excluir_audio',
                args=[self.demanda.pk, audio.pk]
            )
        )

        self.assertRedirects(resposta, self.url())
        self.assertFalse(Evidencia.objects.filter(pk=audio.pk).exists())

    def test_excluir_audio_nao_remove_foto_ou_video(self):
        for tipo, nome, mime in [
            ('foto', 'foto.jpg', 'image/jpeg'),
            ('video', 'video.mp4', 'video/mp4'),
        ]:
            evidencia = Evidencia.objects.create(
                demanda=self.demanda,
                tipo=tipo,
                descricao='Evidência protegida',
                arquivo=self.arquivo(nome, b'teste', mime)
            )

            resposta = self.client.post(
                reverse(
                    'excluir_audio',
                    args=[self.demanda.pk, evidencia.pk]
                )
            )

            self.assertEqual(resposta.status_code, 404)
            self.assertTrue(
                Evidencia.objects.filter(pk=evidencia.pk).exists()
            )

    def test_outro_fiscal_nao_pode_excluir_audio(self):
        audio = Evidencia.objects.create(
            demanda=self.demanda,
            tipo='audio',
            descricao='Áudio protegido',
            arquivo=self.arquivo(
                'protegido.mp3',
                b'audio-teste',
                'audio/mpeg'
            )
        )

        self.client.force_login(self.outro_fiscal)

        resposta = self.client.post(
            reverse(
                'excluir_audio',
                args=[self.demanda.pk, audio.pk]
            )
        )

        self.assertEqual(resposta.status_code, 404)
        self.assertTrue(
            Evidencia.objects.filter(pk=audio.pk).exists()
        )

    def test_demanda_encerrada_bloqueia_registro_e_exclusao(self):
        audio = Evidencia.objects.create(
            demanda=self.demanda,
            tipo='audio',
            descricao='Áudio preservado',
            arquivo=self.arquivo(
                'preservado.mp3',
                b'audio-teste',
                'audio/mpeg'
            )
        )

        self.demanda.status = 'concluida'
        self.demanda.save()

        resposta = self.client.post(
            self.url('adicionar_evidencia'),
            {
                'tipo': 'foto',
                'descricao': 'Foto indevida',
                'arquivo': self.arquivo(),
            }
        )

        self.assertRedirects(resposta, self.url())
        self.assertEqual(self.demanda.evidencias.count(), 1)

        resposta = self.client.post(
            reverse(
                'excluir_audio',
                args=[self.demanda.pk, audio.pk]
            )
        )

        self.assertRedirects(resposta, self.url())
        self.assertTrue(
            Evidencia.objects.filter(pk=audio.pk).exists()
        )

    def test_contagem_de_evidencias_por_tipo(self):
        resposta = self.client.get(self.url())

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.context['contagem_evidencias'],
            {
                'foto': 0,
                'video': 0,
                'audio': 0,
                'anotacao': 0,
            }
        )

        for tipo in ['foto', 'foto', 'video', 'audio', 'anotacao']:
            Evidencia.objects.create(
                demanda=self.demanda,
                tipo=tipo,
                descricao=f'Teste {tipo}'
            )

        resposta = self.client.get(self.url())

        self.assertEqual(
            resposta.context['contagem_evidencias'],
            {
                'foto': 2,
                'video': 1,
                'audio': 1,
                'anotacao': 1,
            }
        )

        for texto in ['Fotos: 2', 'Vídeos: 1', 'Áudios: 1', 'Anotações: 1']:
            self.assertContains(resposta, texto)