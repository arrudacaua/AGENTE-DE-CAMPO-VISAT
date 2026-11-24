"""Execute com o servidor de demonstração da Entrega 03 e uma demanda em andamento."""
import argparse
import base64
from uuid import uuid4

from playwright.sync_api import expect, sync_playwright


def testar(url, numero, chromium):
    destino = f"{url}/demanda/{numero}/"
    descricao = f"Foto de teste US07 {uuid4()}"
    png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=chromium)
        context = browser.new_context()
        page = context.new_page()
        page.goto(destino)
        page.locator('[name="username"]').fill("fiscal_demo")
        page.locator('[name="password"]').fill("DemoFiscal123!")
        page.locator('button[type="submit"]').click()
        page.goto(destino)
        page.wait_for_function("navigator.serviceWorker.controller !== null")
        page.wait_for_function("Object.keys(localStorage).some(k => k.startsWith('visat-preparada:'))")
        context.set_offline(True)
        page.get_by_role("link", name="Registrar evidência", exact=True).click()
        expect(page.locator("[data-conexao]")).to_have_text("Modo offline")
        page.locator('[name="arquivo"]').set_input_files({"name": "vistoria.png", "mimeType": "image/png", "buffer": png})
        page.locator('[name="descricao"]').fill(descricao)
        page.get_by_role("button", name="Salvar foto").click()
        expect(page.locator("[data-fotos]")).to_contain_text("Pendente de sincronização")
        page.close()
        page = context.new_page()
        page.goto(destino)
        expect(page.locator("[data-fotos]")).to_contain_text(descricao)
        expect(page.locator("[data-resumo]")).to_contain_text("1")

        # O primeiro POST chega ao Django, mas o navegador perde a confirmação.
        ids = []

        def perder_primeira_confirmacao(route):
            response = route.fetch()
            assert response.ok, response.text()
            ids.append(response.json()["evidencia"])
            if len(ids) == 1:
                route.abort()
            else:
                route.fulfill(response=response)

        page.route("**/sincronizar-foto/", perder_primeira_confirmacao)
        context.set_offline(False)
        expect(page.locator("[data-aviso]")).to_contain_text("continua salva")
        expect(page.locator("[data-fotos]")).to_contain_text(descricao)
        page.evaluate("window.dispatchEvent(new Event('focus'))")
        expect(page.locator("[data-aviso]")).to_contain_text("Sincronizado")
        expect(page.locator("[data-resumo]")).to_contain_text("Nenhuma")
        assert len(ids) == 2 and ids[0] == ids[1], ids
        page.goto(destino)
        expect(page.locator(".evidence-row").filter(has_text=descricao)).to_have_count(1)
        expect(page.locator(".evidence-row").filter(has_text=descricao)).to_contain_text("Sincronizado")
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--demanda", type=int, default=1)
    parser.add_argument("--chromium")
    args = parser.parse_args()
    testar(args.url, args.demanda, args.chromium)
    print("OK: foto persistida offline, confirmação perdida e reenvio sem duplicação.")
