/* US07: only the generic photo screen and its assets are cached by the worker. */
(async function () {
  const panel = document.querySelector("#fotos-locais");
  const shell = panel?.hasAttribute("data-offline");
  const activeKey = "visat-fiscal";
  if (!shell) {
    localStorage.setItem(activeKey, document.body.dataset.fiscal || "");
    document.querySelector('form[action="/sair/"]')?.addEventListener("submit", () => localStorage.removeItem(activeKey));
  }
  const fiscal = localStorage.getItem(activeKey);
  const numero = panel?.dataset.numero || location.pathname.match(/^\/demanda\/(\d+)\//)?.[1];
  const notice = panel?.querySelector("[data-aviso]") || document.createElement("p");
  if (!panel && fiscal) {
    notice.setAttribute("role", "status");
    document.querySelector("main")?.prepend(notice);
  }
  function connection() {
    const text = navigator.onLine ? "Online" : "Modo offline";
    const badge = panel?.querySelector("[data-conexao]");
    if (badge) badge.textContent = text;
    const header = document.querySelector(".connection-pill");
    if (header && panel) header.textContent = text;
  }
  if (panel) panel.hidden = false;
  connection();
  window.addEventListener("offline", connection);
  window.addEventListener("online", connection);
  if (!fiscal || !("serviceWorker" in navigator) || !window.indexedDB) {
    if (panel) notice.textContent = "Registro offline indisponível neste navegador ou sessão.";
    return;
  }

  const preparedKey = "visat-preparada:" + fiscal + ":" + numero;
  if (panel && !shell && !panel.dataset.editavel) localStorage.removeItem(preparedKey);
  if (shell && !localStorage.getItem(preparedKey)) {
    notice.textContent = "Abra esta fiscalização com conexão antes de registrar fotos offline.";
    return;
  }
  const registration = navigator.serviceWorker.register("/visat-sw.js").then(() => navigator.serviceWorker.ready);
  registration.then(() => {
    if (panel?.dataset.editavel) localStorage.setItem(preparedKey, "1");
  }).catch(() => { notice.textContent = "Falha ao preparar a tela para reabertura offline."; });

  const db = await new Promise((resolve, reject) => {
    const req = indexedDB.open("visat-fotos", 1);
    req.onupgradeneeded = () => req.result.createObjectStore("fotos", {keyPath: "id"}).createIndex("fiscal", "fiscal");
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
  function operation(mode, action) {
    return new Promise((resolve, reject) => {
      const tx = db.transaction("fotos", mode);
      const req = action(tx.objectStore("fotos"));
      tx.oncomplete = () => resolve(req.result);
      tx.onabort = () => reject(tx.error);
    });
  }
  const photos = () => operation("readonly", store => store.index("fiscal").getAll(fiscal));
  async function render() {
    if (!panel) return;
    const pending = (await photos()).filter(photo => photo.numero === numero);
    panel.querySelector("[data-resumo]").textContent = pending.length
      ? "Fotos pendentes de sincronização: " + pending.length : "Nenhuma foto pendente de sincronização.";
    const list = panel.querySelector("[data-fotos]");
    list.replaceChildren();
    for (const photo of pending) {
      const li = document.createElement("li");
      li.textContent = (photo.descricao || photo.arquivo.name) + " — Pendente de sincronização";
      list.append(li);
    }
    const finish = document.querySelector('form[action$="/concluir/"] button');
    if (finish && pending.length) finish.setAttribute("data-aguarda-foto", "1");
    if (finish?.dataset.aguardaFoto) finish.disabled = pending.length > 0;
  }
  let syncing = false;
  async function sync() {
    if (syncing || !navigator.onLine || localStorage.getItem(activeKey) !== fiscal) return;
    syncing = true;
    try {
      for (const photo of await photos()) {
        const data = new FormData();
        for (const field of ["arquivo", "descricao", "fiscal", "latitude", "longitude"]) data.append(field, photo[field]);
        data.append("tipo", "foto");
        data.append("identificador", photo.id);
        const csrf = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/)?.[1] || "";
        const response = await fetch("/demanda/" + photo.numero + "/sincronizar-foto/", {
          method: "POST", headers: {"X-CSRFToken": csrf}, body: data
        });
        const result = await response.json().catch(() => ({}));
        if (response.ok && result.identificador === photo.id && result.evidencia) {
          await operation("readwrite", store => store.delete(photo.id));
          notice.textContent = "Sincronizado — foto da demanda #" + photo.numero + " recebida.";
        } else {
          notice.textContent = result.erro || "Envio pendente. Confira sua sessão e tente novamente.";
        }
      }
    } catch {
      notice.textContent = "Envio pendente. A foto continua salva no dispositivo.";
    } finally {
      syncing = false;
      await render();
    }
  }
  const form = shell ? document.querySelector("#foto-offline") : document.querySelector('#evidencia-form [name="tipo"]')?.form;
  if (shell) {
    form.hidden = false;
    panel.querySelector("a").href = "/demanda/" + numero + "/";
  }
  form?.addEventListener("submit", async event => {
    if (!shell && form.elements.tipo.value !== "foto") return;
    event.preventDefault();
    if (form.dataset.salvando) return;
    const arquivo = form.elements.arquivo.files[0];
    if (!arquivo || !/^image\//.test(arquivo.type) || !/\.(jpe?g|png|webp|gif)$/i.test(arquivo.name) || arquivo.size > 50 * 1024 * 1024) {
      notice.textContent = "Selecione uma foto JPG, PNG, WEBP ou GIF com até 50 MB.";
      return;
    }
    form.dataset.salvando = "1";
    try {
      await operation("readwrite", store => store.add({
        id: crypto.randomUUID(), arquivo, numero, fiscal, descricao: form.elements.descricao.value,
        latitude: form.elements.latitude?.value || "", longitude: form.elements.longitude?.value || ""
      }));
      form.reset();
      notice.textContent = "Foto salva no dispositivo.";
      await render();
      await sync();
    } catch {
      notice.textContent = "Não foi possível guardar a foto. Confira o espaço disponível.";
    } finally {
      delete form.dataset.salvando;
    }
  });
  window.addEventListener("storage", event => {
    if (event.key === activeKey && event.newValue !== fiscal) location.reload();
  });
  window.addEventListener("online", sync);
  window.addEventListener("focus", sync);
  window.setInterval(() => { if (!document.hidden) sync(); }, 30000);
  await render();
  await sync();
})().catch(() => {
  const notice = document.querySelector("[data-aviso]");
  if (notice) notice.textContent = "Armazenamento offline indisponível neste dispositivo.";
});
