/* US07: only the generic fieldwork screen and its assets are cached by the worker. */
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
    notice.textContent = "Abra esta fiscalização com conexão antes de registrar dados offline.";
    return;
  }
  const snapshotKey = "visat-checklist:" + fiscal + ":" + numero;
  const source = panel?.querySelector("template[data-itens]");
  if (source && panel.dataset.editavel) {
    const items = Array.from(source.content.children, el => ({
      id: el.dataset.id, nome: el.textContent, resposta: el.dataset.resposta
    }));
    localStorage.setItem(snapshotKey + ":detalhe", JSON.stringify([source.dataset.descricao, source.dataset.local]));
    localStorage.setItem(snapshotKey, JSON.stringify(items));
  }
  const items = JSON.parse(localStorage.getItem(snapshotKey) || "[]");
  const registration = shell ? navigator.serviceWorker.ready : navigator.serviceWorker.register("/visat-sw.js").then(() => navigator.serviceWorker.ready);
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
  // Preserve the IndexedDB store used by the first release (including pending photos).
  const records = async () => (await operation("readonly", store => store.index("fiscal").getAll(fiscal)))
    .sort((a, b) => (a.criado || 0) - (b.criado || 0));
  const labels = {conforme: "Conforme", nao_conforme: "Não conforme", "": "Pendente"};
  const receipts = new Map();
  const current = entry => entry.numero === numero;
  const pendingHere = async () => (await records()).filter(current);
  const remove = id => operation("readwrite", store => store.delete(id));
  function remember(entry, value) {
    const key = "visat-checklist:" + fiscal + ":" + entry.numero;
    const snapshot = JSON.parse(localStorage.getItem(key) || "[]");
    const item = snapshot.find(item => item.id === entry.item);
    if (item) {
      item.resposta = value;
      localStorage.setItem(key, JSON.stringify(snapshot));
    }
  }
  function button(label, action) {
    const el = document.createElement("button");
    el.type = "button";
    el.textContent = label;
    el.addEventListener("click", action);
    return el;
  }
  async function render() {
    if (!panel) return;
    const pending = await pendingHere();
    panel.querySelector("[data-resumo]").textContent = pending.length
      ? "Registros pendentes de sincronização: " + pending.length : "Nenhuma pendência de sincronização.";
    const list = panel.querySelector("[data-fotos]");
    list.replaceChildren();
    for (const entry of pending) {
      const li = document.createElement("li");
      li.textContent = (entry.nome || entry.descricao || entry.arquivo?.name) + " — Pendente de sincronização";
      if (entry.conflito !== undefined) {
        li.append(" · Neste dispositivo: " + labels[entry.resposta] + ". No servidor: " + labels[entry.conflito] + ". ");
        li.append(button("Usar resposta do servidor", async () => {
          remember(entry, entry.conflito);
          await remove(entry.id);
          location.reload();
        }), button("Confirmar minha resposta", async () => {
          entry.anterior = entry.conflito;
          delete entry.conflito;
          await operation("readwrite", store => store.put(entry));
          await render();
          await sync();
        }));
      }
      list.append(li);
    }
    for (const message of receipts.values()) {
      const li = document.createElement("li");
      li.textContent = message;
      list.append(li);
    }
    const finish = document.querySelector('form[action$="/concluir/"] button');
    if (finish) finish.disabled = pending.length > 0;
  }
  async function sendQueue() {
    const blocked = new Set();
    for (const entry of await records()) {
      if (localStorage.getItem(activeKey) !== fiscal) break;
      const itemKey = entry.numero + ":" + entry.item;
      if (entry.conflito !== undefined) blocked.add(itemKey);
      if (entry.item && blocked.has(itemKey)) continue;
      const data = new FormData();
      for (const field of ["arquivo", "descricao", "fiscal", "latitude", "longitude", "item", "resposta", "anterior"]) {
        if (entry[field] != null) data.append(field, entry[field]);
      }
      const tipo = entry.tipo || "foto";
      data.append("tipo", tipo);
      data.append("identificador", entry.id);
      const route = entry.item ? "sincronizar-resposta" : tipo === "foto" ? "sincronizar-foto" : "sincronizar-evidencia";
      const csrf = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/)?.[1] || "";
      const response = await fetch("/demanda/" + entry.numero + "/" + route + "/", {
        method: "POST", headers: {"X-CSRFToken": csrf}, body: data
      });
      const result = await response.json().catch(() => ({}));
      if (response.ok && result.identificador === entry.id && (result.evidencia || "resposta" in result)) {
        if (entry.item) remember(entry, result.resposta);
        await remove(entry.id);
        const message = (entry.nome || entry.descricao || entry.arquivo?.name) + " — Sincronizado";
        if (current(entry)) receipts.set(entry.id, message);
        notice.textContent = "Sincronizado — registro da demanda #" + entry.numero + " recebido.";
      } else {
        if (entry.item) blocked.add(itemKey);
        if (entry.item && response.status === 409 && "atual" in result) {
          entry.conflito = result.atual;
          await operation("readwrite", store => store.put(entry));
        }
        notice.textContent = result.erro || "Envio pendente. Confira sua sessão.";
      }
    }
  }
  let syncing = false;
  async function sync() {
    if (syncing || !navigator.onLine) return;
    syncing = true;
    try {
      if (navigator.locks) await navigator.locks.request("visat-envio:" + fiscal, sendQueue);
      else await sendQueue();
    } catch {
      notice.textContent = "Envio pendente. A cópia continua salva no dispositivo.";
    } finally {
      syncing = false;
      await render();
    }
  }
  if (panel?.dataset.editavel) {
    document.querySelector('form[action$="/iniciar/"]')?.addEventListener("submit", event => {
      if (!navigator.onLine) {
        event.preventDefault();
        location.assign("/demanda/" + numero + "/checklist/");
      }
    });
  }
  const checklist = document.querySelector(shell ? "[data-offline-checklist]" : "[data-checklist-form]");
  const form = shell ? document.querySelector("#foto-offline") : document.querySelector('#evidencia-form [name="tipo"]')?.form;
  if (shell) {
    panel.querySelector("[data-identificacao]").textContent = JSON.parse(localStorage.getItem(snapshotKey + ":detalhe") || "[]").filter(Boolean).join(" · ");
    document.querySelector("[data-demanda]").textContent = "#" + numero;
    panel.querySelector("[data-offline-nav]").hidden = false;
    for (const link of panel.querySelectorAll("[data-rota]")) link.href = "/demanda/" + numero + "/" + link.dataset.rota;
    form.hidden = !location.pathname.endsWith("/evidencia/");
    checklist.hidden = !location.pathname.endsWith("/checklist/");
    for (const item of items) {
      const group = document.createElement("fieldset");
      const legend = document.createElement("legend");
      legend.textContent = item.nome;
      group.append(legend);
      for (const value of ["conforme", "nao_conforme"]) {
        const label = document.createElement("label");
        const radio = document.createElement("input");
        Object.assign(radio, {type: "radio", name: "item_" + item.id, value});
        label.append(radio, labels[value]);
        group.append(label);
      }
      checklist.querySelector("[data-campos]").append(group);
    }
    form.elements.tipo.addEventListener("change", () => {
      const input = form.elements.arquivo;
      input.value = "";
      input.disabled = form.elements.tipo.value === "anotacao";
      input.accept = {foto: "image/*", audio: "audio/*", video: "video/*"}[form.elements.tipo.value] || "";
    });
    if (!checklist.hidden && !items.length) notice.textContent = "Reabra a demanda online para preparar os itens do checklist.";
  }
  if (checklist && !checklist.hidden) {
    const baseline = new Map(items.map(item => [item.id, item.resposta]));
    const drafts = (await pendingHere()).filter(entry => entry.item);
    for (const entry of drafts) baseline.set(entry.item, entry.resposta);
    for (const [id, value] of baseline) {
      const radio = checklist.querySelector('input[name="item_' + id + '"][value="' + value + '"]');
      if (radio) radio.checked = true;
    }
    checklist.addEventListener("submit", async event => {
      // Preserve Django's normal online form (including its revision check).
      if (!shell && navigator.onLine && !drafts.length && !checklist.dataset.local) return;
      event.preventDefault();
      checklist.dataset.local = "1";
      const changes = [];
      for (const item of items) {
        const resposta = checklist.querySelector('input[name="item_' + item.id + '"]:checked')?.value;
        if (resposta && resposta !== baseline.get(item.id)) changes.push({
          id: crypto.randomUUID(), criado: Date.now(), fiscal, numero, item: item.id,
          nome: item.nome, anterior: baseline.get(item.id), resposta
        });
      }
      if (!changes.length) return;
      try {
        await operation("readwrite", store => {
          for (const entry of changes) store.add(entry);
          return store.count();
        });
        for (const entry of changes) baseline.set(entry.item, entry.resposta);
        notice.textContent = "Checklist salvo no dispositivo.";
        const state = checklist.querySelector("[data-save-state]");
        if (state) state.textContent = notice.textContent;
        await render();
        await sync();
      } catch {
        notice.textContent = "Não foi possível salvar as respostas neste dispositivo.";
      }
    });
  }
  form?.addEventListener("submit", async event => {
    event.preventDefault();
    if (form.dataset.salvando) return;
    const tipo = form.elements.tipo.value;
    const descricao = form.elements.descricao.value.trim();
    const arquivo = tipo === "anotacao" ? null : form.elements.arquivo.files[0];
    const formats = {
      foto: [/\.(jpe?g|png|webp|gif)$/i, "image/"], video: [/\.(mp4|webm|mov)$/i, "video/"],
      audio: [/\.(mp3|wav|ogg|m4a|webm)$/i, "audio/"]
    };
    if (tipo === "anotacao" ? !descricao : !arquivo || !formats[tipo][0].test(arquivo.name) ||
        !arquivo.type.startsWith(formats[tipo][1]) || arquivo.size > 50 * 1024 * 1024) {
      notice.textContent = tipo === "anotacao" ? "Escreva a anotação." : "Selecione um arquivo válido de até 50 MB.";
      return;
    }
    form.dataset.salvando = "1";
    try {
      await operation("readwrite", store => store.add({
        id: crypto.randomUUID(), criado: Date.now(), tipo, arquivo, numero, fiscal, descricao,
        latitude: form.elements.latitude?.value || "", longitude: form.elements.longitude?.value || ""
      }));
      form.reset();
      form.elements.tipo.dispatchEvent(new Event("change"));
      notice.textContent = "Evidência salva no dispositivo.";
      await render();
      await sync();
    } catch {
      notice.textContent = "Não foi possível guardar a evidência. Confira o espaço disponível.";
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
