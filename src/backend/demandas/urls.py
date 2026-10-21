from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("login/", views.login_view, name="login"),
    path("sair/", views.logout_view, name="logout"),
    path("demanda/nova/", views.criar_demanda, name="criar_demanda"),
    path("demanda/<int:numero>/", views.detalhe_demanda, name="detalhe_demanda"),
    path("demanda/<int:numero>/localizacao/", views.editar_localizacao, name="editar_localizacao"),
    path("demanda/<int:numero>/iniciar/", views.iniciar_demanda, name="iniciar_demanda"),
    path("demanda/<int:numero>/checklist/", views.checklist, name="checklist"),
    path("demanda/<int:numero>/evidencia/", views.adicionar_evidencia, name="adicionar_evidencia"),
    path("demanda/<int:numero>/concluir/", views.concluir_demanda, name="concluir_demanda"),
    path("demanda/<int:numero>/homologar/", views.homologar_demanda, name="homologar_demanda"),
    path("demanda/<int:numero>/relatorio/", views.gerar_relatorio, name="gerar_relatorio"),
    path("demanda/<int:numero>/vincular-sei/", views.vincular_sei, name="vincular_sei"),
]
