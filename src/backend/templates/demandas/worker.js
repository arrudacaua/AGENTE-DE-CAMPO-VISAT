{% load static %}
const shell = "{% url 'offline_foto' %}";
const assets = [shell, "{% static 'demandas/js/offline.js' %}", "{% static 'demandas/css/app.css' %}"];
const cacheName = "visat-fotos-v1";
self.addEventListener("install", event => event.waitUntil(
  caches.open(cacheName).then(cache => cache.addAll(assets)).then(() => self.skipWaiting())
));
self.addEventListener("activate", event => event.waitUntil(self.clients.claim()));
self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  if (url.origin !== location.origin || event.request.method !== "GET") return;
  if (assets.includes(url.pathname)) {
    event.respondWith(caches.open(cacheName).then(cache => cache.match(url.pathname)).then(hit => hit || fetch(event.request)));
  } else if (event.request.mode === "navigate" && /^\/demanda\/\d+\/(?:evidencia\/|checklist\/)?$/.test(url.pathname)) {
    event.respondWith(fetch(event.request).catch(() => caches.open(cacheName).then(cache => cache.match(shell))));
  }
});
