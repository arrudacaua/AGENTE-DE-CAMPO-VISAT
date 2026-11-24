"""Execute com o servidor de demonstração da Entrega 03 e uma demanda em andamento."""
import argparse
import base64
from uuid import uuid4
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def testar(url, numero, chromium):
    destino = f"{url}/demanda/{numero}/"
    descricao = f"Foto de teste US07 {uuid4()}"
    png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=chromium)
        pasta = Path("evidencias-entrega03/US07-registros-offline")
        pasta.mkdir(parents=True, exist_ok=True)
        context = browser.new_context(record_video_dir=str(pasta))
        # O runner não possui periféricos. Som e quadros sintéticos alimentam o MediaRecorder real.
        context.add_init_script("""navigator.mediaDevices.getUserMedia = async constraints => {
            if (constraints.audio) {
                const audio = new AudioContext();
                const oscillator = audio.createOscillator();
                const output = audio.createMediaStreamDestination();
                oscillator.connect(output);
                oscillator.start();
                await audio.resume();
                return output.stream;
            }
            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");
            const stream = canvas.captureStream(10);
            const timer = setInterval(() => ctx.fillRect(0, 0, 20, 20), 100);
            setTimeout(() => clearInterval(timer), 1500);
            return stream;
        }""")
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
        page.get_by_role("button", name="Salvar registro").click()
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
        page.unroute("**/sincronizar-foto/")
        testar_registros(page, context, destino, descricao, pasta)
        context.close()
        browser.close()


def testar_registros(page, context, destino, descricao, pasta):
    for rota in ["", "checklist/", "evidencia/"]:
        page.goto(destino + rota)
        expect(page.locator("[data-conexao]")).to_have_text("Online")
    context.set_offline(True)
    for rota in ["", "evidencia/", "checklist/"]:
        page.goto(destino + rota)
        expect(page.locator("[data-conexao]")).to_have_text("Modo offline")

    item = page.locator("[data-campos] fieldset").first
    anterior = item.locator("input:checked").get_attribute("value") if item.locator("input:checked").count() else ""
    valor = "conforme" if anterior != "conforme" else "nao_conforme"
    item.locator(f'input[value="{valor}"]').check()
    page.get_by_role("button", name="Salvar checklist").click()
    expect(page.locator("[data-resumo]")).to_contain_text("1")
    page.reload()
    expect(page.locator("[data-campos] fieldset").first.locator(f'input[value="{valor}"]')).to_be_checked()

    page.get_by_role("link", name="Registrar evidência").click()
    for tipo in ["anotacao", "audio", "video"]:
        page.locator('[name="tipo"]').select_option(tipo)
        if tipo == "audio":
            page.get_by_role("button", name="Iniciar gravação").click()
            expect(page.locator("#audio-status")).to_contain_text("Gravando")
            page.wait_for_timeout(500)
            page.get_by_role("button", name="Parar gravação").click()
            expect(page.locator("#audio-status")).to_contain_text("Gravação concluída")
        elif tipo == "video":
            page.locator('[name="arquivo"]').evaluate("""async input => {
                const stream = await navigator.mediaDevices.getUserMedia({video: true});
                const recorder = new MediaRecorder(stream, {mimeType: "video/webm"});
                const chunks = [];
                recorder.ondataavailable = e => chunks.push(e.data);
                const stopped = new Promise(resolve => recorder.onstop = resolve);
                recorder.start(100);
                await new Promise(resolve => setTimeout(resolve, 600));
                recorder.stop();
                await stopped;
                stream.getTracks().forEach(track => track.stop());
                const transfer = new DataTransfer();
                transfer.items.add(new File(chunks, "vistoria.webm", {type: "video/webm"}));
                input.files = transfer.files;
            }""")
        page.locator('[name="descricao"]').fill(f"{tipo} {descricao}")
        page.get_by_role("button", name="Salvar registro").click()
        expect(page.locator("[data-fotos]")).to_contain_text(f"{tipo} {descricao} — Pendente")
    page.get_by_role("link", name="Detalhe da demanda").click()
    expect(page.locator("[data-resumo]")).to_contain_text("4")
    page.screenshot(path=str(pasta / "resumo-pendente.png"))
    context.set_offline(False)
    expect(page.locator("[data-resumo]")).to_contain_text("Nenhuma")
    expect(page.locator("[data-fotos] li").filter(has_text="Sincronizado")).to_have_count(4)
    expect(page.locator("[data-aviso]")).to_contain_text("Sincronizado")
    page.screenshot(path=str(pasta / "sincronizado.png"))
    page.goto(destino + "checklist/")
    expect(page.locator(".check-item").first.locator(f'input[value="{valor}"]')).to_be_checked()
    page.goto(destino)
    for tipo in ["anotacao", "audio", "video"]:
        row = page.locator(".evidence-row").filter(has_text=f"{tipo} {descricao}")
        expect(row).to_have_count(1)
        expect(row).to_contain_text("Sincronizado")
        if tipo in ("audio", "video"):
            src = row.locator("source").get_attribute("src")
            response = context.request.get(src if src.startswith("http") else destino.split("/demanda/")[0] + src)
            assert response.ok and response.body()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--demanda", type=int, default=1)
    parser.add_argument("--chromium")
    args = parser.parse_args()
    testar(args.url, args.demanda, args.chromium)
    print("OK: checklist e quatro tipos de evidência, reabertura, indicadores e sincronização.")
