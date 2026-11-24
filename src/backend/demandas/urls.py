from django.urls import path
from django.views.generic import TemplateView
from . import views
from .offline import sincronizar_foto

urlpatterns = [
    path("visat-sw.js", TemplateView.as_view(template_name="demandas/worker.js", content_type="text/javascript"), name="offline_worker"),
    path("offline/foto/", TemplateView.as_view(template_name="demandas/offline.html"), name="offline_foto"),
    path("demanda/<int:numero>/sincronizar-foto/", sincronizar_foto, name="sincronizar_foto"),
    path("", views.inicio, name="inicio"),
    path("login/", views.login_view, name="login"),
    path("sair/", views.logout_view, name="logout"),
    path("demanda/nova/", views.criar_demanda, name="criar_demanda"),
    path("demanda/<int:numero>/atribuir-fiscal/", views.atribuir_fiscal, name="atribuir_fiscal"),
    path("demanda/<int:numero>/", views.detalhe_demanda, name="detalhe_demanda"),
    path("demanda/<int:numero>/localizacao/", views.editar_localizacao, name="editar_localizacao"),
    path("demanda/<int:numero>/iniciar/", views.iniciar_demanda, name="iniciar_demanda"),
    path("demanda/<int:numero>/checklist/", views.checklist, name="checklist"),
    path("demanda/<int:numero>/evidencia/", views.adicionar_evidencia, name="adicionar_evidencia"),
    path("demanda/<int:numero>/evidencia/<int:evidencia_id>/excluir/", views.excluir_audio, name="excluir_audio"),
    path("demanda/<int:numero>/evidencia/<int:evidencia_id>/excluir-arquivo/", views.excluir_evidencia, name="excluir_evidencia"),
    path("demanda/<int:numero>/concluir/", views.concluir_demanda, name="concluir_demanda"),
    path("demanda/<int:numero>/homologar/", views.homologar_demanda, name="homologar_demanda"),
    path("demanda/<int:numero>/relatorio/", views.gerar_relatorio, name="gerar_relatorio"),
    path("demanda/<int:numero>/vincular-sei/", views.vincular_sei, name="vincular_sei"),
]
