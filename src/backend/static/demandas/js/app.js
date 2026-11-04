(() => {
  'use strict';
  const buttons = document.querySelectorAll('[data-toggle-menu]');
  const sidebar = document.getElementById('app-sidebar');
  const setMenu = (open) => {
    document.body.classList.toggle('menu-open', open);
    buttons.forEach(btn => btn.setAttribute('aria-expanded', String(open)));
    if (sidebar) sidebar.setAttribute('aria-hidden', String(!open && window.innerWidth <= 1100));
  };
  buttons.forEach(btn => btn.addEventListener('click', () => setMenu(!document.body.classList.contains('menu-open'))));
  document.querySelector('[data-close-menu]')?.addEventListener('click', () => setMenu(false));
  sidebar?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') setMenu(false); });
  window.addEventListener('resize', () => { if (window.innerWidth > 1100) setMenu(false); });

  const search = document.querySelector('[data-demand-search]');
  const filter = document.querySelector('[data-demand-status]');
  const updateDemands = () => {
    const term = (search?.value || '').trim().toLocaleLowerCase('pt-BR');
    const status = filter?.value || '';
    const items = Array.from(document.querySelectorAll('[data-demand-item]'));
    let visible = 0;
    items.forEach(item => {
      const matches = (!status || item.dataset.demandStatus === status) && (!term || (item.dataset.demandText || '').toLocaleLowerCase('pt-BR').includes(term));
      item.hidden = !matches;
      if (matches && item.classList.contains('mobile-demand-card')) visible++;
    });
    const empty = document.querySelector('[data-filter-empty]');
    if (empty) empty.hidden = !items.length || visible !== 0;
  };
  search?.addEventListener('input', updateDemands);
  filter?.addEventListener('change', updateDemands);

  document.querySelectorAll('[data-dismiss]').forEach(btn => btn.addEventListener('click', () => btn.closest('.flash-message')?.remove()));
  document.querySelectorAll('[data-toggle-password]').forEach(btn => btn.addEventListener('click', () => {
    const input = btn.parentElement.querySelector('input');
    if (!input) return;
    input.type = input.type === 'password' ? 'text' : 'password';
    const showing = input.type === 'text';
    btn.setAttribute('aria-label', showing ? 'Ocultar senha' : 'Mostrar senha');
    const use = btn.querySelector('use');
    if (use) use.setAttribute('href', showing ? '#i-eye-off' : '#i-eye');
  }));
})();

(() => {
  const dialog = document.getElementById('map-dialog');
  const openButton = document.querySelector('[data-map-open]');
  openButton?.addEventListener('click', () => {
    const frame = dialog.querySelector('iframe');
    if (!frame.src) frame.src = frame.dataset.mapSrc;
    if (typeof dialog.showModal === 'function') dialog.showModal();
    else window.open(frame.dataset.mapSrc, '_blank', 'noopener,noreferrer');
  });
  document.querySelector('[data-map-close]')?.addEventListener('click', () => dialog.close());
  dialog?.addEventListener('close', () => openButton?.focus());
  const form = document.querySelector('[data-checklist-form]');
  if (!form) return;
  let dirty = false;
  form.addEventListener('change', () => {
    dirty = true;
    const state = form.querySelector('[data-save-state]');
    state.textContent = 'Alterações ainda não salvas. Clique em Salvar checklist antes de sair.';
    state.classList.add('is-dirty');
    form.querySelectorAll('.check-item').forEach(item => {
      const pending = item.querySelector('.pending-answer');
      if (pending) pending.hidden = !!item.querySelector('input:checked');
    });
  });
  form.addEventListener('submit', () => { dirty = false; });
  window.addEventListener('beforeunload', event => {
    if (dirty) { event.preventDefault(); event.returnValue = ''; }
  });
})();
