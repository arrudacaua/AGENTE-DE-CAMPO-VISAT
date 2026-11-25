# Entrega 05 — Qualidade, testes e colaboração

## 3. Qualidade e testes

### 3.1. Testes automatizados

Foram executados os testes automatizados do backend Django, contemplando as funcionalidades implementadas no projeto.

**Resultado da execução:**

- Total de testes executados: 61
- Testes aprovados: 61
- Falhas: 0
- Erros: 0
- Verificação do sistema Django: nenhum problema identificado
- Tempo de execução: 16,807 segundos

**Resultado:** todos os 61 testes foram executados com sucesso.

O registro da execução está disponível no arquivo `src/backend/evidencias_testes_django.txt`.

### 3.2. Testes de interface e validação funcional

A próxima etapa consiste na implementação e execução de testes automatizados de interface utilizando Playwright, contemplando as histórias de usuário concluídas na Sprint 03:

- US06 — Registrar evidências da fiscalização.
- US07 — Registrar dados sem conexão.
- US08 — Gerar rascunho do relatório com IA.
- US09 — Revisar o relatório antes da assinatura.
- US10 — Assinar e concluir a fiscalização.
- US11 — Acompanhar indicadores no dashboard.
- US12 — Atribuir fiscal à demanda.

Os testes deverão verificar os principais fluxos das funcionalidades, incluindo as interações do usuário e os resultados esperados no sistema.

**Situação:** pendente de implementação e execução.

As gravações das execuções automatizadas serão anexadas aos respectivos cartões do Trello após a realização dos testes.

### 3.3. Validações complementares

Além dos testes automatizados do Django, foram realizadas verificações complementares:

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

**Resultado:** PASS.

**Arquivos estáticos**

Foi executado o comando `collectstatic --noinput`, com o seguinte resultado:

- 130 arquivos copiados.
- 390 arquivos pós-processados.
- Arquivo `staticfiles/staticfiles.json` verificado.

### 3.4. Cobertura e limitações

A execução dos 61 testes Django comprova que os testes automatizados existentes foram aprovados. Entretanto, ainda é necessário implementar e executar os testes de interface com Playwright.

A cobertura de código deverá ser registrada caso seja realizada uma medição específica.

A US18 permanece pendente e não faz parte da validação das histórias concluídas da Sprint 03.

## 4. Colaboração e evidências

### 4.1. Organização e acompanhamento

As atividades de qualidade e validação estão sendo organizadas por meio dos cartões do Trello, relacionados às histórias de usuário da Sprint 03.

As evidências são centralizadas no cartão **Testes automatizados e validação funcional — Entrega 05**, além dos cartões individuais das histórias US06 a US12.

### 4.2. Evidências das execuções

As evidências previstas para esta entrega incluem:

- Arquivo TXT com a saída atualizada dos 61 testes Django.
- Captura de tela da execução atualizada dos testes Django.
- Vídeo atualizado da execução dos testes no GitHub Actions.
- Vídeos das execuções automatizadas com Playwright para as histórias US06 a US12.
- Registros das validações funcionais realizadas.
- Links de commits e demais alterações relacionadas à entrega.

**Situação das evidências:** as evidências Django precisam ser atualizadas no Trello para refletir os 61 testes. O vídeo atual do GitHub Actions também deverá ser substituído por uma nova gravação. As evidências do Playwright serão adicionadas após sua execução.

### 4.3. Histórico de alterações

- Commit `8aee501` — `docs: atualiza evidências dos testes Django`.
- Commit `30fb9c5` — renomeação do script de inicialização para `verificar_inicializador.py`.
- Issue #19 — registro relacionado às atividades do projeto.

### 4.4. Checklist da entrega

- [x] Executar os testes automatizados Django.
- [x] Registrar o resultado dos 61 testes aprovados.
- [x] Validar o inicializador da aplicação.
- [x] Verificar os arquivos estáticos.
- [ ] Atualizar as evidências Django no Trello.
- [ ] Gravar e anexar o novo vídeo do GitHub Actions.
- [ ] Implementar e executar os testes automatizados com Playwright.
- [ ] Gravar e anexar os vídeos das execuções do Playwright.
- [ ] Registrar as validações funcionais das histórias US06 a US12.

**Observação:** esta documentação será atualizada conforme as atividades pendentes forem executadas e suas respectivas evidências forem produzidas.