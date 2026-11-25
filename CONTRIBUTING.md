# Como contribuir com o Agente de Campo VISAT

Este guia explica como preparar um ambiente de desenvolvimento do zero, rodar o sistema e os testes, e enviar contribuições seguindo o fluxo do grupo. Se algo aqui não funcionar como descrito, abra uma issue: o guia também é parte do projeto.

## Sumário

1. [Visão geral do projeto](#1-visão-geral-do-projeto)
2. [Pré-requisitos](#2-pré-requisitos)
3. [Configurando o ambiente](#3-configurando-o-ambiente)
4. [Criando usuários e dados de teste](#4-criando-usuários-e-dados-de-teste)
5. [Rodando o sistema](#5-rodando-o-sistema)
6. [Rodando os testes](#6-rodando-os-testes)
7. [Estrutura de pastas](#7-estrutura-de-pastas)
8. [Fluxo de contribuição](#8-fluxo-de-contribuição)
9. [Padrões de código](#9-padrões-de-código)
10. [Reportando bugs](#10-reportando-bugs)
11. [Problemas comuns](#11-problemas-comuns)

---

## 1. Visão geral do projeto

O VISAT é uma aplicação web em **Django** que centraliza as demandas da Vigilância em Saúde do Trabalhador. Há dois perfis de uso:

- **Gerência**: cadastra demandas, atribui fiscais, acompanha indicadores e homologa fiscalizações.
- **Fiscal de campo**: consulta suas demandas, preenche o checklist, registra evidências (inclusive sem conexão), revisa o relatório e assina.

| Camada | Tecnologia |
| --- | --- |
| Back-end | Python 3.13 e Django 5.2 |
| Front-end | Templates Django (HTML, CSS e JavaScript) |
| Banco de dados | SQLite em desenvolvimento; PostgreSQL em produção via `DATABASE_URL` |
| Arquivos estáticos | WhiteNoise |
| Testes e CI | Testes do Django e GitHub Actions |

Todo o código da aplicação fica em `src/backend/`. É lá que ficam o `manage.py`, as dependências e as configurações.

## 2. Pré-requisitos

Instale antes de começar:

- **Python 3.13**: a mesma versão usada no GitHub Actions. Download em <https://www.python.org/downloads/>. No Windows, marque a opção *"Add Python to PATH"* na instalação.
- **Git**: <https://git-scm.com/downloads>
- Uma conta no **GitHub** com acesso de escrita ao repositório. Peça ao gerente do projeto para ser adicionado como colaborador.

Confira se está tudo instalado:

```bash
python --version   # deve mostrar Python 3.13.x  (no Windows também funciona: py -3.13 --version)
git --version
```

## 3. Configurando o ambiente

### 3.1. Clonar o repositório

```bash
git clone https://github.com/arrudacaua/AGENTE-DE-CAMPO-VISAT.git
cd AGENTE-DE-CAMPO-VISAT/src/backend
```

> Todos os comandos a partir daqui são executados dentro de `src/backend/`.

### 3.2. Criar e ativar o ambiente virtual

O ambiente virtual isola as dependências do projeto das do seu computador.

**Windows (PowerShell ou CMD):**

```bat
py -3.13 -m venv .venv
.venv\Scripts\activate
```

**Linux e macOS:**

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

Com o ambiente ativado, o terminal passa a mostrar `(.venv)` no começo da linha. Ative-o de novo sempre que abrir um terminal novo.

### 3.3. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

> Use o `requirements.txt` de **`src/backend/`**. O arquivo de mesmo nome na raiz do repositório está vazio.

### 3.4. Configurar as variáveis de ambiente

Copie o arquivo de exemplo:

```bash
# Windows
copy .env.example .env
# Linux e macOS
cp .env.example .env
```

O `.env` padrão já serve para desenvolvimento. As variáveis aceitas são:

| Variável | Para que serve | Valor em desenvolvimento |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Chave secreta do Django | Qualquer texto |
| `DJANGO_DEBUG` | Liga o modo de depuração | `True` |
| `DJANGO_ALLOWED_HOSTS` | Endereços aceitos pelo servidor | `localhost,127.0.0.1` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origens confiáveis (só em produção) | deixe vazio |
| `DATABASE_URL` | Banco externo, como PostgreSQL (só em produção) | não defina, para usar SQLite |

> **Nunca faça commit do `.env`.** Ele já está no `.gitignore`. Com `DJANGO_DEBUG=False`, o sistema exige `DJANGO_SECRET_KEY` e `DJANGO_ALLOWED_HOSTS` configurados e força HTTPS. Por isso, use `True` na sua máquina.

### 3.5. Criar o banco de dados

```bash
python manage.py migrate
```

Esse comando cria o arquivo `db.sqlite3` com todas as tabelas. O banco é local e não vai para o Git.

## 4. Criando usuários e dados de teste

O sistema decide o perfil assim:

- **Gerência**: usuário com `is_staff` ou superusuário, ou que esteja no grupo `Gerencia`.
- **Fiscal**: qualquer outro usuário ativo.

### Opção A: dados de demonstração prontos (mais rápido)

```bash
# Windows (PowerShell)
$env:PYTHONPATH="."; python ..\..\scripts\entrega03\preparar_demo.py
# Linux e macOS
PYTHONPATH=. python ../../scripts/entrega03/preparar_demo.py
```

Esse script cria uma demanda de exemplo e dois usuários **fictícios, só para uso local**:

| Perfil | Usuário | Senha |
| --- | --- | --- |
| Gerência | `gerencia_demo` | `DemoGerencia123!` |
| Fiscal | `fiscal_demo` | `DemoFiscal123!` |

### Opção B: criar seus próprios usuários

```bash
python manage.py createsuperuser
```

O superusuário entra como Gerência. Para criar fiscais, acesse <http://127.0.0.1:8000/admin/> com o superusuário, vá em **Usuários → Adicionar usuário** e deixe a opção *Membro da equipe* desmarcada.

## 5. Rodando o sistema

```bash
python manage.py runserver
```

Abra <http://127.0.0.1:8000> e entre com um dos usuários acima. Para parar o servidor, use `Ctrl + C`.

| Endereço | O que é |
| --- | --- |
| `/login/` | Tela de login |
| `/` | Painel inicial: Gerência ou Fiscal, conforme o perfil |
| `/admin/` | Administração do Django, só para superusuário |

> Usuários de Windows também podem usar o `ABRIR_VISAT.bat`, que fica em `src/backend/`, depois que o ambiente estiver configurado.

## 6. Rodando os testes

Antes de abrir um pull request, rode os três comandos abaixo. Eles são os mesmos que o GitHub Actions executa:

```bash
python manage.py check                          # verifica a configuração do projeto
python manage.py makemigrations --check --dry-run   # confirma que nenhum model ficou sem migração
python manage.py test demandas                  # roda todos os testes automatizados
```

O resultado esperado do último comando termina em `OK`. Todos os testes precisam passar.

Os testes ficam em `src/backend/demandas/`: o `tests.py` geral e um arquivo `test_<assunto>.py` por funcionalidade, como `test_relatorio_ia.py` e `test_indicadores.py`. Ao criar uma funcionalidade, prefira **criar um arquivo de teste novo** a editar o `tests.py`, para evitar conflitos com outras pessoas.

## 7. Estrutura de pastas

```text
AGENTE-DE-CAMPO-VISAT/
├── .github/
│   ├── ISSUE_TEMPLATE/      # modelo para relatar bugs
│   └── workflows/           # GitHub Actions: testes automáticos em cada PR para a main
├── docs/                    # imagens, evidências e documentos das entregas
├── scripts/                 # scripts de demonstração e testes de navegador
└── src/
    └── backend/             # aplicação Django (trabalhe aqui)
        ├── config/          # settings.py, urls.py, wsgi/asgi
        ├── demandas/        # app principal: models, views, forms, urls, testes
        │   └── migrations/  # migrações do banco
        ├── templates/demandas/  # telas (HTML)
        ├── static/demandas/     # CSS, JavaScript e imagens
        ├── manage.py
        ├── requirements.txt
        └── .env.example
```

> As pastas `src/frontend/` e `src/database/` contêm apenas arquivos vazios da estrutura inicial. As telas ficam em `src/backend/templates/`, e o banco é criado pelas migrações do Django.

## 8. Fluxo de contribuição

Cada história de usuário ou correção segue estes passos:

### 8.1. Escolha a tarefa

Pegue uma história ou issue no board ([Trello](https://trello.com/b/er7tMowp/visat)) ou nas [issues do GitHub](https://github.com/arrudacaua/AGENTE-DE-CAMPO-VISAT/issues) e mova o cartão para **Em Andamento**.

### 8.2. Crie uma branch a partir da `main` atualizada

```bash
git checkout main
git pull origin main
git checkout -b feature/us12-atribuir-fiscal
```

Nomes de branch usados no projeto:

| Tipo | Padrão | Exemplo |
| --- | --- | --- |
| Nova funcionalidade | `feature/usXX-descricao-curta` | `feature/us11-dashboard-indicadores` |
| Correção | `correcao/descricao-curta` | `correcao/logout-post` |
| Somente testes | `test/usXX-descricao-curta` | `test/us18-validacao-processo-sei` |

**Nunca faça commit direto na `main`.**

### 8.3. Implemente e teste

Faça a mudança, rode os testes da [seção 6](#6-rodando-os-testes) e abra o sistema no navegador para conferir a tela.

### 8.4. Faça commits pequenos e descritivos

```bash
git add <arquivos alterados>
git commit -m "feat(us12): permite atribuir fiscal à demanda"
```

O formato é `tipo(escopo): descrição no imperativo, em português`. Tipos mais usados:

| Tipo | Quando usar |
| --- | --- |
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `test` | Criação ou ajuste de testes |
| `docs` | Documentação |
| `style` | Visual ou formatação, sem mudar comportamento |
| `refactor` | Reorganização de código sem mudar comportamento |

### 8.5. Envie a branch e abra o pull request

```bash
git push -u origin feature/us12-atribuir-fiscal
```

No GitHub, abra um **pull request para a `main`** com:

- título com a história, como `US12 – Atribuir fiscal à demanda`;
- descrição do que foi feito e de como testar;
- prints ou vídeo quando houver mudança visual.

### 8.6. Revisão e merge

- O GitHub Actions roda os testes automaticamente. O PR só entra com os testes passando.
- Se aparecer **conflito com a `main`**, atualize sua branch (`git pull origin main`), resolva os conflitos, rode os testes de novo e envie.
- Outra pessoa do grupo revisa e faz o merge. Depois do merge, mova o cartão para **Concluído** e apague a branch.

## 9. Padrões de código

- **Idioma**: nomes de variáveis, funções, mensagens e textos da interface em português, seguindo o código existente.
- **Lógica nova em módulo próprio**: funcionalidades maiores ganham um arquivo em `demandas/`, como `relatorio_ia.py` e `indicadores.py`, em vez de crescer o `views.py`.
- **Banco de dados**: ao alterar `models.py`, gere a migração com `python manage.py makemigrations` e faça commit dela junto com a mudança. Não edite migrações que já estão na `main`.
- **Permissões**: toda view nova precisa de `@login_required` e precisa verificar o perfil (Gerência ou Fiscal), como as views existentes. Formulários que alteram dados usam `POST` com CSRF.
- **Visual**: reaproveite as classes de `static/demandas/css/app.css` (`panel`, `metric-card`, `bar-stack` e outras) para manter o mesmo padrão das telas.
- **Não versione**: `.env`, `db.sqlite3`, `.venv/`, `media/` e `staticfiles/`. Todos já estão no `.gitignore`.

## 10. Reportando bugs

Abra uma issue no GitHub usando o modelo **"Relato de bug VISAT"**. Informe a história de usuário, os passos para reproduzir, o resultado esperado e o observado, e anexe prints. Não inclua senhas nem dados pessoais.

## 11. Problemas comuns

| Problema | Solução |
| --- | --- |
| `python` não é reconhecido (Windows) | Use `py -3.13` no lugar de `python`, ou reinstale o Python marcando *Add Python to PATH*. |
| `No module named django` | O ambiente virtual não está ativado. Rode o comando de ativação da seção 3.2. |
| `no such table` ao abrir o sistema | Faltou rodar `python manage.py migrate`. |
| `DJANGO_SECRET_KEY precisa ser configurada` | Seu `.env` está com `DJANGO_DEBUG=False`. Mude para `True` em desenvolvimento. |
| A página redireciona para `https://` e não abre | Mesmo motivo: com `DJANGO_DEBUG=False`, o sistema força HTTPS. Use `True` localmente. |
| Ativar o `.venv` no PowerShell dá erro de permissão | Rode `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` uma vez e tente de novo. |
| Teste passa na sua máquina e falha no PR | Atualize sua branch com a `main` (`git pull origin main`) e rode os testes de novo: provavelmente outra mudança entrou antes. |

---

Dúvidas? Fale com o grupo ou abra uma issue.
