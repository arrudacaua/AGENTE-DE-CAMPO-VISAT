# Testes — Entrega 03 / Sprint 01

Esta pasta contém o registro verificável da execução dos testes do VISAT.

- [Resultado dos 17 testes Django](resultado-testes.txt)
- [Execução aprovada no GitHub Actions](https://github.com/arrudacaua/AGENTE-DE-CAMPO-VISAT/actions/runs/39700225004)
- [Baixar log completo: artifact **resultado-testes-django**](https://github.com/arrudacaua/AGENTE-DE-CAMPO-VISAT/actions/runs/39700225004#artifacts)
- [Baixar vídeos: artifact **screencasts-e-capturas-visat**](https://github.com/arrudacaua/AGENTE-DE-CAMPO-VISAT/actions/runs/39700225004#artifacts)
- [Código-fonte dos testes](../../src/backend/demandas/tests.py)
- [Roteiro de gravação automatizada](../../scripts/entrega03/gravar_testes.py)

**Resultado:** 17 testes executados, 17 aprovados; job de gravação dos screencasts aprovado.

**Importante:** os testes executáveis continuam em `src/backend/demandas/tests.py` para o Django encontrá-los normalmente. Esta pasta armazena as **evidências dos testes**, evitando duplicação de código.

Os vídeos US01 e US05 já constam nos cartões do Trello exportado; US02, US03 e US04 têm capturas de tela, sem screencasts anexados identificados. Consulte os links abaixo e confirme as permissões do quadro privado.

## Evidências nos cartões do Trello

| História de usuário | Cartão no Trello | Evidência anexada | Situação do screencast |
| --- | --- | --- | --- |
| US01 — Acessar o sistema por perfil | [Abrir cartão](https://trello.com/c/GHjDK2CQ) | [Assistir ao screencast](https://trello.com/1/cards/6a98788872c0c4640e0847fc/attachments/6ad9656f7c2ec6bc4eb91941/download/screencast-acesso-por-perfil.mp4.mp4) | Vídeo anexado |
| US02 — Consultar minhas Demandas | [Abrir cartão](https://trello.com/c/BJRpvGqc) | [Ver captura de tela](https://trello.com/1/cards/6a987967894b709a7037b01a/attachments/6ad960ebb782600ba6b42771/download/02-minhas-demandas.png) | Vídeo não identificado no cartão |
| US03 — Visualizar detalhe e localização da Demanda | [Abrir cartão](https://trello.com/c/DHJOn8dJ) | [Ver captura de tela](https://trello.com/1/cards/6a987ac04aa5675a96fc2735/attachments/6ad9609af1c60cbfd6858b12/download/03-detalhes.png) | Vídeo não identificado no cartão |
| US04 — Iniciar e retomar a fiscalização | [Abrir cartão](https://trello.com/c/fK9u3TsS) | [Ver captura de tela](https://trello.com/1/cards/6a987a34503f1d24f1baf08d/attachments/6ad9625037a60d147b67b9e7/download/06-retomar.png) | Vídeo não identificado no cartão |
| US05 — Preencher checklist de fiscalização | [Abrir cartão](https://trello.com/c/1wPxs63k) | [Assistir ao screencast](https://trello.com/1/cards/6a987cfb78b897716ce8a72e/attachments/6ad9679f0e2fbf663edec19c/download/US05-screencast-checklist-inspecao.mp4.mp4) | Vídeo anexado |

> **Acesso às evidências:** o quadro Trello está configurado como **privado** no arquivo exportado. O professor precisa ter permissão de acesso aos cartões e anexos. O arquivo exportado registra vídeos para US01 e US05; para US02–US04, registra capturas de tela, não screencasts anexados aos cartões. Os vídeos automatizados do GitHub Actions permanecem disponíveis separadamente, conforme a retenção dos artifacts.
