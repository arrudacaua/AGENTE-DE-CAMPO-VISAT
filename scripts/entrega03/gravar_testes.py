"""Grava videos reais do Chromium executando fluxos Django com dados ficticios."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path("evidencias-entrega03")
ROOT.mkdir(exist_ok=True)
BASE = "http://127.0.0.1:8000"

def gravar(browser, titulo, usuario, senha, passos):
    pasta = ROOT / titulo
    pasta.mkdir(exist_ok=True)
    contexto = browser.new_context(viewport={"width": 1440, "height": 900},
                                   record_video_dir=str(pasta), record_video_size={"width": 1440, "height": 900})
    pagina = contexto.new_page()
    try:
        pagina.goto(BASE + "/login/")
        pagina.locator('input[name="username"]').fill(usuario)
        pagina.locator('input[name="password"]').fill(senha)
        pagina.get_by_role("button", name="Entrar no sistema").click()
        pagina.wait_for_url(BASE + "/")
        pagina.screenshot(path=str(pasta / "01-painel.png"), full_page=True)
        pagina.wait_for_timeout(1000)
        passos(pagina, pasta)
        pagina.wait_for_timeout(1300)
    finally:
        video = pagina.video
        contexto.close()
        if video:
            video.save_as(str(pasta / (titulo + ".webm")))

with sync_playwright() as p:
    navegador = p.chromium.launch(headless=True)
    def gerente(pagina, pasta):
        assert pagina.get_by_text("Visão geral").count() >= 1
        pagina.goto(BASE + "/demanda/1/")
        pagina.get_by_text("SEI-DEMO-ENTREGA03").first.wait_for()
        pagina.screenshot(path=str(pasta / "02-demanda-criada.png"), full_page=True)
    gravar(navegador, "US01-login-gerencia", "gerencia_demo", "DemoGerencia123!", gerente)

    def fiscal(pagina, pasta):
        pagina.get_by_text("Minhas demandas").first.wait_for()
        pagina.get_by_text("OS-DEMO-001").first.wait_for()
        pagina.screenshot(path=str(pasta / "02-minhas-demandas.png"), full_page=True)
        pagina.goto(BASE + "/demanda/1/")
        pagina.get_by_text("SEI-DEMO-ENTREGA03").first.wait_for()
        pagina.screenshot(path=str(pasta / "03-detalhes.png"), full_page=True)
        pagina.get_by_role("button", name="Iniciar Fiscalização").click()
        pagina.wait_for_url(BASE + "/demanda/1/checklist/")
        pagina.screenshot(path=str(pasta / "04-checklist-inicial.png"), full_page=True)
        radios = pagina.locator('input[type="radio"][value="conforme"]')
        assert radios.count() == 6, f"Esperados seis itens; encontrados {radios.count()}"
        for i in range(radios.count()):
            radios.nth(i).check()
        pagina.get_by_role("button", name="Salvar checklist").click()
        pagina.wait_for_url(BASE + "/demanda/1/checklist/")
        pagina.reload()
        assert pagina.locator('input[type="radio"][value="conforme"]:checked').count() == 6
        pagina.screenshot(path=str(pasta / "05-checklist-salvo.png"), full_page=True)
        pagina.goto(BASE + "/demanda/1/")
        pagina.get_by_role("button", name="Continuar Fiscalização").wait_for()
        pagina.screenshot(path=str(pasta / "06-retomar.png"), full_page=True)
    gravar(navegador, "US02-US05-fluxo-fiscal", "fiscal_demo", "DemoFiscal123!", fiscal)
    navegador.close()
print("Testes de navegador concluídos; videos WEBM e capturas PNG salvos em", ROOT)
