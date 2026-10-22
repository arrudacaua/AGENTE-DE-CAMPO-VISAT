# Entrega 03 — Itens 3 e 4: qualidade, testes e colaboração

> Evidências da Sprint 01. Atualizado em 21/10/2026. Este documento separa o que foi verificado do que ainda precisa ser comprovado pela equipe.

## 3. Qualidade e testes

### Testes automatizados

O projeto contém 17 testes Django em `src/backend/demandas/tests.py`. A execução local informada pela equipe em 21/10/2026 terminou com **17 testes aprovados**, conforme resultado visto durante a validação. Esse resultado não equivale a uma execução de CI no GitHub.

Para reproduzir, na pasta `src/backend`:

```powershell
py manage.py check
py manage.py test demandas --verbosity 2
```

Coberturas identificadas no código:
- US01/US02: autenticação, isolamento de demandas por fiscal, lista, busca e paginação;
- US03: detalhes, ausência de fiscal e validação de coordenadas;
- US04: início protegido por POST/CSRF, retomada e bloqueios de acesso;
- US05: seis itens, gravação, persistência, validações, concorrência e conclusão;
- Migração de dados legados e preservação de registros.

### Testes de sistema no navegador

| Cenário | Evidência conhecida | Screencast no Trello |
| --- | --- | --- |
| Login da gerência e do fiscal | Acessos locais demonstrados em 21/10/2026 | Pendente de anexação |
| Cadastro e atribuição da demanda #001 | Cadastro e fiscal responsável demonstrados | Pendente de anexação |
| US02 — Fiscal visualiza sua demanda | Painel com demanda #001 demonstrado | Pendente de anexação |
| US03 — Fiscal abre detalhes | Não comprovado por captura até o momento | Pendente |
| US04 — Fiscal inicia e retoma fiscalização | Não comprovado por captura até o momento | Pendente |
| US05 — Fiscal preenche e salva checklist | Não comprovado por captura até o momento | Pendente |

**Roteiro de gravação (um vídeo curto por história):**
1. Mostrar a história e o usuário utilizado (sem expor senha).
2. Executar o fluxo do início ao fim.
3. Mostrar o resultado e, quando aplicável, atualizar a página para demonstrar persistência.
4. Anexar o vídeo ao cartão da história no [Trello VISAT](https://trello.com/b/er7tMowp/visat).
5. Colar abaixo o link direto do cartão/vídeo e registrar data, executor e resultado.

| História | Cartão do Trello | Link do vídeo | Resultado/data |
| --- | --- | --- | --- |
| US01 | A preencher | A preencher | A preencher |
| US02 | A preencher | A preencher | A preencher |
| US03 | A preencher | A preencher | A preencher |
| US04 | A preencher | A preencher | A preencher |
| US05 | A preencher | A preencher | A preencher |

### Issue / bug tracker

- [Checklist de validação e evidências — issue #2](https://github.com/arrudacaua/AGENTE-DE-CAMPO-VISAT/issues/2).
- O repositório contém modelo para reportar bugs em `.github/ISSUE_TEMPLATE/bug_report.md`.
- Para cada defeito **reproduzido**, abrir uma issue separada com passos, comportamento esperado/obtido, ambiente, print e referência à história. Não registrar bugs fictícios.

## 4. Colaboração e evidências

### Programação em pares

**Situação:** é necessário confirmar quais sessões efetivamente aconteceram. Preencher somente após confirmação dos participantes.

| Par (nomes) | Data | História/tarefa | O que o par implementou | Evidência (commit, PR ou registro) |
| --- | --- | --- | --- | --- |
| A confirmar | A confirmar | A confirmar | A confirmar | A confirmar |
| A confirmar | A confirmar | A confirmar | A confirmar | A confirmar |

Relato de cada sessão: identificar quem atuou como *driver* (digitou) e *navigator* (revisou/orientou), decisões, testes feitos e link de commit/PR. Não atribuir autoria sem comprovação.

### Prints do backlog e da Sprint 01

O README raiz já referencia `docs/board.png` e `docs/backlog.png`. **É necessário confirmar que as imagens representam o estado da Sprint 01 da Entrega 03** e atualizá-las se estiverem antigas. Capturar o quadro mostrando listas, cartões, responsáveis e situação real.

- [Board do projeto](https://trello.com/b/er7tMowp/visat)
- Print da Sprint 01: conferir/atualizar `docs/board.png`
- Print do backlog: conferir/atualizar `docs/backlog.png`

### Screencasts das histórias no README

Adicionar os links reais à tabela acima e, quando disponíveis, reproduzi-los na seção Entrega 03 do README principal. O vídeo de protótipo antigo não substitui a demonstração das histórias implementadas.

### Revisão final

- [ ] Anexar vídeo de testes ao cartão correspondente
- [ ] Anexar vídeos das histórias US01–US05
- [ ] Validar US03–US05 manualmente
- [ ] Conferir/atualizar prints da Sprint 01 e backlog
- [ ] Confirmar e documentar pares reais e suas contribuições
- [ ] Revisar as evidências com a equipe
