# 🔎 AGENTE DE CAMPO VISAT

<p align="center">
  <img src="docs/banner-visat.png" alt="VISAT Banner" width="350">
</p>

<p align="center">
  Sistema web para centralizar, organizar e acompanhar as demandas da Vigilância em Saúde do Trabalhador.
</p>

## 🎯 Sobre o projeto

O VISAT recebe demandas de diferentes instituições que podem resultar em inspeções, análises e documentos técnicos. O projeto centraliza essas informações, facilitando a comunicação entre os inspetores e o acompanhamento dos processos.

## 🚀 Objetivo

Desenvolver uma solução que permita:

- Centralizar as demandas recebidas;
- Acompanhar o andamento dos processos;
- Organizar informações e documentos;
- Controlar responsáveis e prazos;
- Melhorar a visualização das demandas e seus respectivos status.

## ⚙️ Funcionalidades

### 📋 Gestão de Ordens de Serviço

- Cadastro de Ordem de Serviço
- Definição de prioridade e registro de prazo
- Atribuição de responsável e atualização do status
- Consulta dos detalhes da demanda

### 📎 Gestão de Documentos e Inspeções

- Anexação de documentos
- Registro de inspeções e relatórios

### 🔎 Busca e Filtros

- Pesquisa e filtro de demandas

### 📊 Monitoramento e Indicadores

- Alertas de prazo
- Visualização do dashboard e consulta do histórico

### 🔐 Acesso ao Sistema

- Controle de acesso por perfil e autenticação de usuário

### 🏛️ Integração com o SEI

- Validação e vinculação de processo SEI
- Entrada de demandas externas pelo SEI

## 🎨 Protótipo

O protótipo do VISAT apresenta a proposta visual do sistema e permite visualizar a navegação entre as principais funcionalidades.

<p align="center">
  <img src="docs/prototipo.png" alt="Protótipo do sistema VISAT" width="250">
</p>

<p align="center">
  <a href="https://claude.ai/artifact/SjXbqsXkbAX9fMj9x1Ec2A">
    <b>🔗 Acessar protótipo completo</b>
  </a>
</p>

<p align="center">
  <a href="https://youtube.com/shorts/jCpbPQLyhu8?feature=share">
    <b>🎬 Assistir ao vídeo de demonstração no YouTube</b>
  </a>
</p>

## 📐 Diagramas

Os diagramas de atividades representam os fluxos das histórias de usuário do VISAT, detalhando as ações, decisões e responsabilidades envolvidas em cada funcionalidade.

<p align="center">
  <a href="https://claude.ai/artifact/Mb39gmjth4y6PLFV9LAeL5">
    <b>📁 Acessar todos os diagramas</b>
  </a>
</p>

## 🛠️ Tecnologias

<p align="center">
  <img src="https://skillicons.dev/icons?i=html,css,js,python,mysql,git,github" />
</p>

<p align="center">
  HTML • CSS • JavaScript • Python • MySQL • Git • GitHub
</p>

## 📁 Estrutura do projeto

```text
VISAT/
├── docs/
│   ├── banner-visat.png
│   ├── board.png
│   └── backlog.png
│
├── src/
│   ├── frontend/
│   ├── backend/
│   └── database/
│
├── .gitignore
├── README.md
└── requirements.txt
```

- **docs/** — imagens, evidências e documentação do projeto.
- **frontend/** — interface e elementos visuais do sistema.
- **backend/** — regras e funcionalidades da aplicação.
- **database/** — estrutura e comandos do banco de dados.

## 📋 Board

O desenvolvimento é organizado através de um Board Kanban:

**Backlog → A Fazer → Em Andamento → Em Revisão → Concluído**

O backlog possui no mínimo 15 Histórias de Usuário priorizadas, seguindo o padrão 3Cs: Card, Conversation e Confirmation.

<p align="center">
  <img src="docs/board.png" alt="Board atualizado" width="850">
</p>

🔗 [Acessar o Board do projeto](https://trello.com/b/er7tMowp/visat)

## 👥 Equipe

Projeto desenvolvido por estudantes de Sistemas de Informação.

- [CAUÃ FERREIRA ARRUDA](https://www.linkedin.com/in/cauã-arruda-0b30563b0?utm_source=share_via&utm_content=profile&utm_medium=member_ios) - Gerente de Projeto
- [ISABELLY RIBEIRO DO CARMO](https://www.linkedin.com/in/isabellyribeiroc?utm_source=share_via&utm_content=profile&utm_medium=member_ios) - Designer
- [JOÃO GABRIEL CASSIMIRO DE ARAUJO](https://www.linkedin.com/in/joao-cassimiro?utm_source=share_via&utm_content=profile&utm_medium=member_ios) - Desenvolvedor Back-end
- [JOÃO PAULO DO NASCIMENTO](https://www.linkedin.com/in/joão-nascimento-drones?utm_source=share_via&utm_content=profile&utm_medium=member_android) - Product Owner (PO)
- [LETÍCIA CARVALHO BARBOSA](https://www.linkedin.com/in/leticiacarvalhobarbosa/) - Designer
- [SOFIA MARTINS VAN DRUNEN](https://www.linkedin.com/in/sofia-martins-van-drunen-096a08426/) - Arquiteta de Software
- [SURI SAVITRI PROCÓPIO ALVES](https://www.linkedin.com/in/surisavitriprocopioalves) - Analista de Requisitos
- [VINÍCIUS MACHADO LIMA](https://www.linkedin.com/in/vinicius-machado-lima-5a4100406?utm_source=share_via&utm_content=profile&utm_medium=member_android) - Desenvolvedor Front-end

## 📌 Status

🚧 **Em desenvolvimento**


## 🧪 Entrega 03 — Sprint 01: qualidade, testes e colaboração

**Itens 3 e 4 da avaliação.** A documentação detalhada, o roteiro de gravação, o controle de evidências e o quadro de programação em pares estão em [Qualidade e colaboração — Entrega 03](docs/ENTREGA_03_QUALIDADE_COLABORACAO.md).

### Testes do sistema

- **[Pasta de evidências dos testes — docs/testes](docs/testes/README.md)**, incluindo [resultado dos 17 testes](docs/testes/resultado-testes.txt).
- **[Execução aprovada dos testes e screencasts no GitHub Actions](https://github.com/arrudacaua/AGENTE-DE-CAMPO-VISAT/actions/runs/39700225004)**. Na seção **Artifacts**, baixar `resultado-testes-django` e `screencasts-e-capturas-visat`.

- **17 testes automatizados Django** existentes em `src/backend/demandas/tests.py`; execução local aprovada em 21/10/2026, conforme validação da equipe.
- Demonstrações locais já realizadas: login da gerência e fiscal, cadastro/atribuição da demanda #001 e consulta pelo fiscal.
- **Evidência automatizada no navegador aprovada:** detalhes no perfil fiscal (US03), início/retomada (US04) e checklist (US05), com vídeos disponíveis nos Artifacts. No Trello exportado, há vídeos anexados aos cartões US01 e US05 e capturas de tela nos cartões US02, US03 e US04.
- [Acompanhamento de evidências e validação — issue #2](https://github.com/arrudacaua/AGENTE-DE-CAMPO-VISAT/issues/2). Bugs confirmados devem ter issues próprias.

### Evidências da Sprint 01

| História de usuário | Cartão no Trello | Evidência anexada | Situação do screencast |
| --- | --- | --- | --- |
| US01 — Acessar o sistema por perfil | [Abrir cartão](https://trello.com/c/GHjDK2CQ) | [Assistir ao screencast](https://trello.com/1/cards/6a98788872c0c4640e0847fc/attachments/6ad9656f7c2ec6bc4eb91941/download/screencast-acesso-por-perfil.mp4.mp4) | Vídeo anexado |
| US02 — Consultar minhas Demandas | [Abrir cartão](https://trello.com/c/BJRpvGqc) | [Ver captura de tela](https://trello.com/1/cards/6a987967894b709a7037b01a/attachments/6ad960ebb782600ba6b42771/download/02-minhas-demandas.png) | Vídeo não identificado no cartão |
| US03 — Visualizar detalhe e localização da Demanda | [Abrir cartão](https://trello.com/c/DHJOn8dJ) | [Ver captura de tela](https://trello.com/1/cards/6a987ac04aa5675a96fc2735/attachments/6ad9609af1c60cbfd6858b12/download/03-detalhes.png) | Vídeo não identificado no cartão |
| US04 — Iniciar e retomar a fiscalização | [Abrir cartão](https://trello.com/c/fK9u3TsS) | [Ver captura de tela](https://trello.com/1/cards/6a987a34503f1d24f1baf08d/attachments/6ad9625037a60d147b67b9e7/download/06-retomar.png) | Vídeo não identificado no cartão |
| US05 — Preencher checklist de fiscalização | [Abrir cartão](https://trello.com/c/1wPxs63k) | [Assistir ao screencast](https://trello.com/1/cards/6a987cfb78b897716ce8a72e/attachments/6ad9679f0e2fbf663edec19c/download/US05-screencast-checklist-inspecao.mp4.mp4) | Vídeo anexado |

> **Acesso às evidências:** o quadro Trello está configurado como **privado** no arquivo exportado. O professor precisa ter permissão de acesso aos cartões e anexos. O arquivo exportado registra vídeos para US01 e US05; para US02–US04, registra capturas de tela, não screencasts anexados aos cartões. Os vídeos automatizados do GitHub Actions permanecem disponíveis separadamente, conforme a retenção dos artifacts.

**Prints:** [Board](docs/board.png) · [Backlog](docs/backlog.png) · [Trello da equipe](https://trello.com/b/er7tMowp/visat). A equipe deve confirmar que os prints correspondem à Sprint 01 atual e substituí-los se necessário.

### Programação em pares

**Registro a completar pela equipe com informações reais.** Identificar os dois participantes de cada par, data, história implementada, papel de driver/navigator, resultado e commit/PR que comprove a contribuição. O [formulário de registro](docs/ENTREGA_03_QUALIDADE_COLABORACAO.md#programação-em-pares) já está preparado.

> A ausência de vídeo, print atualizado ou relato confirmado é marcada como pendente, não como atividade concluída.
