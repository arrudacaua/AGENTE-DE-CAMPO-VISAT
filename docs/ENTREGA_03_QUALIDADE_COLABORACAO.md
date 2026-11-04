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

### Testes de sistema no navegador — evidências no Trello

A tabela abaixo reflete os anexos identificados na exportação do quadro Trello; capturas de tela não são classificadas como screencasts.

| História de usuário | Cartão no Trello | Evidência anexada | Situação do screencast |
| --- | --- | --- | --- |
| US01 — Acessar o sistema por perfil | [Abrir cartão](https://trello.com/c/GHjDK2CQ) | [Assistir ao screencast](https://trello.com/1/cards/6a98788872c0c4640e0847fc/attachments/6ad9656f7c2ec6bc4eb91941/download/screencast-acesso-por-perfil.mp4.mp4) | Vídeo anexado |
| US02 — Consultar minhas Demandas | [Abrir cartão](https://trello.com/c/BJRpvGqc) | [Ver captura de tela](https://trello.com/1/cards/6a987967894b709a7037b01a/attachments/6ad960ebb782600ba6b42771/download/02-minhas-demandas.png) | Vídeo não identificado no cartão |
| US03 — Visualizar detalhe e localização da Demanda | [Abrir cartão](https://trello.com/c/DHJOn8dJ) | [Ver captura de tela](https://trello.com/1/cards/6a987ac04aa5675a96fc2735/attachments/6ad9609af1c60cbfd6858b12/download/03-detalhes.png) | Vídeo não identificado no cartão |
| US04 — Iniciar e retomar a fiscalização | [Abrir cartão](https://trello.com/c/fK9u3TsS) | [Ver captura de tela](https://trello.com/1/cards/6a987a34503f1d24f1baf08d/attachments/6ad9625037a60d147b67b9e7/download/06-retomar.png) | Vídeo não identificado no cartão |
| US05 — Preencher checklist de fiscalização | [Abrir cartão](https://trello.com/c/1wPxs63k) | [Assistir ao screencast](https://trello.com/1/cards/6a987cfb78b897716ce8a72e/attachments/6ad9679f0e2fbf663edec19c/download/US05-screencast-checklist-inspecao.mp4.mp4) | Vídeo anexado |

> **Acesso às evidências:** o quadro Trello está configurado como **privado** no arquivo exportado. O professor precisa ter permissão de acesso aos cartões e anexos. O arquivo exportado registra vídeos para US01 e US05; para US02–US04, registra capturas de tela, não screencasts anexados aos cartões. Os vídeos automatizados do GitHub Actions permanecem disponíveis separadamente, conforme a retenção dos artifacts.

Para US02–US04, anexar o screencast ao cartão correspondente quando estiver disponível. Os vídeos automatizados gerados pelo GitHub Actions são evidências separadas dos anexos do Trello.

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

Os links dos cartões e anexos identificados estão na tabela acima e no README. O vídeo de protótipo antigo não substitui a demonstração das histórias implementadas.

### Revisão final

- [x] Identificar e vincular os vídeos anexados às histórias US01 e US05
- [ ] Anexar os vídeos das histórias US02–US04 aos respectivos cartões (atualmente há capturas de tela)
- [ ] Validar US03–US05 manualmente
- [ ] Conferir/atualizar prints da Sprint 01 e backlog
- [ ] Confirmar e documentar pares reais e suas contribuições
- [ ] Revisar as evidências com a equipe
