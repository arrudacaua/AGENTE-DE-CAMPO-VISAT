# Entrega 05 — Qualidade, testes e colaboração

## 3. Qualidade e testes

### 3.1. Testes automatizados Django

Foram ampliados os testes automatizados do backend Django, contemplando regras de negócio, permissões, revisão de relatórios, assinatura, sincronização offline e gerenciamento de evidências.

**Resultado da execução:**

- Total de testes executados: 86
- Testes aprovados: 86
- Falhas: 0
- Erros: 0
- Verificação do sistema Django: nenhum problema identificado.

**Resultado:** todos os 86 testes foram executados com sucesso.

### 3.2. Testes de interface com Playwright

Foi implementada uma suíte de testes de interface utilizando Playwright, com preparação automatizada de dados fictícios e execução dos principais fluxos das histórias.

**Resultado da execução local:**

| História | Cenário | Resultado |
|---|---|---|
| US06 | Registrar evidências da fiscalização | PASSOU |
| US08 | Gerar rascunho do relatório | PASSOU |
| US09 | Revisar relatório antes da assinatura | PASSOU |
| US10 | Assinar e concluir fiscalização | PASSOU |
| US11 | Consultar indicadores do dashboard | PASSOU |
| US12 | Atribuir fiscal à demanda | PASSOU |
| US18 | Cadastrar nova demanda | PASSOU |

**Resultado:** 7 de 7 cenários aprovados.

Os testes são executados pelo script `scripts/entrega05/testar_historias.py`.

As evidências de execução são armazenadas em `evidencias-entrega05/`.

### 3.3. Teste de operação offline — US07

O script `scripts/us07/testar_foto_offline.py` foi adaptado para aceitar parâmetros de URL, demanda, usuário e diretório de evidências, preservando os valores padrão utilizados anteriormente pela Entrega 03.

A execução específica da US07 offline está prevista no workflow automatizado da Entrega 05.

**Situação:** script adaptado; execução específica da US07 ainda pendente de validação no workflow.

### 3.4. Integração contínua

Foi criado o workflow `.github/workflows/entrega05-testes.yml`, destinado à execução automatizada das verificações da entrega.

O workflow contempla:

- Instalação das dependências Python e Playwright.
- Instalação do Chromium.
- Verificação da configuração Django.
- Migração de banco SQLite isolado.
- Preparação dos dados fictícios.
- Execução dos testes automatizados Django.
- Execução dos testes E2E das histórias.
- Execução do teste offline da US07.
- Armazenamento dos resultados e evidências como artefatos.

O workflow possui gatilhos para execução manual, push e pull request.

**Situação:** arquivo criado; execução no GitHub Actions ainda pendente de confirmação.

### 3.5. Validações complementares

**Inicializador da aplicação**

- Verificação das migrações do banco de dados.
- Criação de novo usuário administrador.
- Verificação da autenticação.
- Preservação das credenciais existentes.
- Realização de backup do banco de dados.
- Verificação do bloqueio de execução simultânea.
- Inicialização do servidor HTTP local.
- Verificação do funcionamento da aplicação e do Django Admin.
- Encerramento do servidor.

**Resultado registrado anteriormente:** PASS.

**Arquivos estáticos**

Foi executado o comando `collectstatic --noinput`, com o seguinte resultado registrado:

- 130 arquivos copiados.
- 390 arquivos pós-processados.
- Arquivo `staticfiles/staticfiles.json` verificado.

### 3.6. Cobertura e limitações

Os resultados confirmados nesta etapa são:

- 86 testes automatizados Django aprovados.
- 7 cenários E2E Playwright aprovados.

Não foi realizada medição específica de cobertura de código.

A execução offline da US07 e a validação do workflow no GitHub Actions permanecem pendentes de confirmação.

## 4. Colaboração e evidências

### 4.1. Organização e acompanhamento

As atividades de qualidade e validação estão organizadas por meio dos cartões do Trello, relacionados às histórias de usuário e à Entrega 05.

As evidências devem ser centralizadas no cartão **Testes automatizados e validação funcional — Entrega 05**, além dos cartões individuais das histórias correspondentes.

### 4.2. Evidências das execuções

As evidências produzidas e previstas incluem:

- Resultado dos 86 testes Django.
- Capturas de tela dos cenários E2E aprovados.
- Diretório local `evidencias-entrega05/`.
- Vídeo e registros da execução offline da US07.
- Artefatos gerados pelo GitHub Actions.
- Registros das validações funcionais.
- Links de commits e alterações relacionadas à entrega.

**Situação:** os sete cenários E2E foram aprovados localmente. Ainda é necessário conferir e anexar as evidências aos cartões do Trello e validar a execução completa do workflow remoto.

### 4.3. Histórico de alterações

- Commit `8aee501` — `docs: atualiza evidências dos testes Django`.
- Commit `30fb9c5` — renomeação do script de inicialização para `verificar_inicializador.py`.
- Commit `4b6d7cf` — `test(entrega05): ampliar cobertura dos testes Django`.
- Issue #19 — registro relacionado às atividades do projeto.

### 4.4. Checklist da entrega

- [x] Executar os testes automatizados Django — 86 aprovados.
- [x] Ampliar a cobertura dos testes de regras de negócio.
- [x] Implementar os testes E2E com Playwright.
- [x] Executar os cenários US06, US08, US09, US10, US11, US12 e US18.
- [x] Aprovar os sete cenários E2E.
- [x] Adaptar o script de teste offline da US07.
- [x] Criar o workflow de integração contínua da Entrega 05.
- [ ] Executar e validar o teste offline US07.
- [ ] Confirmar a execução do workflow no GitHub Actions.
- [ ] Conferir e anexar as evidências aos cartões do Trello.
- [ ] Atualizar os registros de evidências Django no Trello.
- [ ] Registrar os links finais das alterações e da entrega.

**Observação:** os itens pendentes devem ser marcados como concluídos somente após a respectiva validação e disponibilização das evidências.
## 4.5. Relato de colaboração entre pares

As histórias foram organizadas em quatro duplas, com duas histórias atribuídas a cada uma. A divisão das atividades e as contribuições foram registradas considerando o histórico de commits e as informações fornecidas pelos integrantes.

| Dupla | História | Relato de contribuição |
|---|---|---|
| Cauã e Vinícius | US06 | Cauã desenvolveu a funcionalidade de registro de evidências de campo. Vinícius realizou melhorias posteriores. |
| Cauã e Vinícius | US12 | Vinícius desenvolveu a funcionalidade de atribuição de fiscal à demanda. |
| João Paulo e Isabelly | US07 | Isabelly desenvolveu o registro offline de fotos e a sincronização. João Paulo prestou auxílio por fora, sem commits identificados. |
| João Paulo e Isabelly | US18 | João Paulo e Isabelly trabalharam juntos na história. Os commits identificados no Git são de Isabelly. |
| Sofia e João Gabriel | US08 | João Gabriel desenvolveu a história com auxílio de Sofia, que colaborou por fora. |
| Sofia e João Gabriel | US11 | João Gabriel desenvolveu a história com auxílio de Sofia, que colaborou por fora. |
| Letícia e Suri | US09 | Suri desenvolveu a funcionalidade de revisão do relatório antes da assinatura. |
| Letícia e Suri | US10 | Letícia desenvolveu a funcionalidade de assinatura e conclusão da inspeção. |

### Contribuições na integração

Além das atividades realizadas nas histórias, Cauã ficou responsável pela revisão de todas as pull requests do projeto e pela resolução dos conflitos de integração encontrados durante o processo de merge.

O histórico do Git foi utilizado para identificar as alterações e os respectivos autores. Nos casos de colaboração realizada por fora, sem commits individuais, o relato considera as informações fornecidas pelos integrantes, sem atribuir a eles alterações que não estejam registradas no repositório.
