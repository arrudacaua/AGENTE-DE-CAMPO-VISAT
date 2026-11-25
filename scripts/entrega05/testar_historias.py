"""Testes E2E das histórias da Entrega 05 usando Playwright."""

import os
import re
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
EVIDENCIAS = Path(__file__).resolve().parents[2] / "evidencias-entrega05"
EVIDENCIAS.mkdir(exist_ok=True)

USUARIOS = {
    "gerencia": ("gerencia_e05", "DemoGerenciaE05!"),
    "fiscal": ("fiscal_e05", "DemoFiscalE05!"),
}


def login(page, perfil):
    usuario, senha = USUARIOS[perfil]
    page.goto(f"{BASE_URL}/login/")
    page.locator("#username").fill(usuario)
    page.locator("#password").fill(senha)
    page.get_by_role("button", name=re.compile("Entrar no sistema")).click()
    page.wait_for_load_state("networkidle")


def abrir_demanda(page, processo_sei):
    page.goto(BASE_URL)
    linha = page.locator("tr[data-demand-item]").filter(
        has_text=processo_sei
    )
    linha.wait_for(state="visible")
    linha.locator("a.table-demand-link").click()
    page.wait_for_load_state("networkidle")


def salvar_evidencia(page):
    abrir_demanda(page, "SEI-E05-US06-EVIDENCIAS")
    page.get_by_role("link", name="Registrar evidência").click()
    formulario = page.locator("#evidencia-form")
    formulario.locator('[name="tipo"]').select_option("anotacao")
    formulario.locator('[name="descricao"]').fill(
        "Evidência textual registrada automaticamente no teste E2E da Entrega 05."
    )
    formulario.locator('button[type="submit"]').first.click()
    page.get_by_text("Evidência textual registrada automaticamente", exact=False).wait_for()


def gerar_relatorio(page):
    abrir_demanda(page, "SEI-E05-US08-RASCUNHO")
    page.get_by_role("link", name="Revisar relatório", exact=True).click()
    page.get_by_role("button", name=re.compile("Gerar rascunho")).click()
    page.locator("article.paper-report").wait_for()


def revisar_relatorio_e_testar_bloqueio(page):
    abrir_demanda(page, "SEI-E05-US09-REVISAO")
    url_detalhe = page.url
    page.get_by_role("link", name="Revisar relatório", exact=True).click()

    page.locator('input[name="confirmar_revisao"]').check()
    page.get_by_role(
        "button", name=re.compile("Confirmar revisão e liberar assinatura")
    ).click()

    page.get_by_text("Revisão do relatório confirmada", exact=False).wait_for()

    page.goto(url_detalhe)
    page.get_by_role("link", name="Preencher").click()
    primeiro_item = page.locator("fieldset.check-item").first
    primeiro_item.locator(
        'input[type="radio"][value="nao_conforme"]'
    ).check()
    page.get_by_role("button", name="Salvar checklist").click()

    page.get_by_role("heading", name="Checklist.").wait_for()
    abrir_demanda(page, "SEI-E05-US09-REVISAO")
    url_detalhe = page.url
    page.get_by_text("Gere e revise o rascunho", exact=False).wait_for()


def assinar_e_concluir(page):
    abrir_demanda(page, "SEI-E05-US10-ASSINATURA")
    page.locator('input[name="confirmar"][value="sim"]').check()
    page.get_by_role(
        "button", name=re.compile("Assinar e concluir fiscalização")
    ).click()
    page.get_by_role("heading", name="Aguardando homologação").wait_for()


def consultar_indicadores(page):
    page.goto(BASE_URL)
    conteudo = page.locator("body").inner_text()
    assert "Distrito E05 Norte" in conteudo
    assert "SEI-E05-US11-ATRASADA" in conteudo
    assert "SEI-E05-US11-VENCENDO" in conteudo


def atribuir_fiscal(page):
    abrir_demanda(page, "SEI-E05-US12-ATRIBUICAO")
    formulario = page.locator('form[action*="atribuir-fiscal"]')
    formulario.locator('select[name="fiscal"]').select_option(
        label="fiscal_e05"
    )
    formulario.locator('button[type="submit"]').click()
    page.get_by_text("Fiscal Entrega 05", exact=False).wait_for()


def cadastrar_demanda(page):
    page.goto(f"{BASE_URL}/demanda/nova/")

    page.locator('[name="numero_os"]').fill("OS-E05-US18-E2E")
    page.locator('[name="processo_sei"]').fill("SEI-E05-US18-E2E")
    page.locator('[name="descricao"]').fill(
        "Demanda cadastrada pela interface no teste automatizado da Entrega 05."
    )
    page.locator('[name="endereco"]').fill("Rua de Teste, 100")
    page.locator('[name="distrito"]').fill("Distrito E05 US18")
    page.locator('[name="bairro"]').fill("Bairro de Teste")
    page.locator('[name="prazo"]').fill(
        (date.today() + timedelta(days=30)).isoformat()
    )
    page.locator('[name="fiscal"]').select_option(label="fiscal_e05")
    page.locator('[name="prioridade"]').select_option("media")

    page.get_by_role("button", name="Cadastrar demanda").click()
    page.get_by_text("SEI-E05-US18-E2E", exact=True).wait_for()

    for item in (
        "Uso de EPI",
        "Validade dos extintores",
        "Sinalização de segurança",
        "Rotas de fuga",
        "Higiene do ambiente",
        "Documentação trabalhista",
    ):
        page.get_by_text(item, exact=False).wait_for()


CENARIOS = [
    ("US06", "fiscal", salvar_evidencia),
    ("US08", "fiscal", gerar_relatorio),
    ("US09", "fiscal", revisar_relatorio_e_testar_bloqueio),
    ("US10", "fiscal", assinar_e_concluir),
    ("US11", "gerencia", consultar_indicadores),
    ("US12", "gerencia", atribuir_fiscal),
    ("US18", "gerencia", cadastrar_demanda),
]


def main():
    resultados = []

    pasta_videos = EVIDENCIAS / "videos"
    pasta_videos.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        navegador = playwright.chromium.launch(headless=True)

        for historia, perfil, teste in CENARIOS:
            for sufixo in ("sucesso", "erro"):
                captura_antiga = EVIDENCIAS / f"{historia.lower()}-{sufixo}.png"
                captura_antiga.unlink(missing_ok=True)

            contexto = navegador.new_context(
                record_video_dir=str(pasta_videos)
            )
            pagina = contexto.new_page()
            video = pagina.video

            try:
                login(pagina, perfil)
                teste(pagina)

                pagina.screenshot(
                    path=str(EVIDENCIAS / f"{historia.lower()}-sucesso.png"),
                    full_page=True,
                )
                resultados.append((historia, "PASSOU"))
                print(f"{historia}: PASSOU")

            except Exception as erro:
                pagina.screenshot(
                    path=str(EVIDENCIAS / f"{historia.lower()}-erro.png"),
                    full_page=True,
                )
                resultados.append((historia, "FALHOU"))
                print(f"{historia}: FALHOU - {erro}")

            finally:
                contexto.close()

                if video:
                    video.save_as(
                        str(pasta_videos / f"{historia.lower()}-execucao.webm")
                    )

        navegador.close()

    falhas = [historia for historia, status in resultados if status == "FALHOU"]

    print("\nResumo da Entrega 05:")
    for historia, status in resultados:
        print(f"  {historia}: {status}")

    if falhas:
        raise SystemExit(1)

if __name__ == "__main__":
    main()





