# Entrega 03 — Sprint 01 (VISAT)

## Situação do repositório
Esta branch prepara a integração do protótipo funcional em Django. O código-fonte completo ainda precisa ser enviado para `src/backend/` e validado antes de abrir um Pull Request como implementação concluída.

## Organização planejada
- `docs/`: backlog, board, protótipos e evidências reais dos testes.
- `src/backend/`: projeto Django, aplicativo `demandas`, templates, arquivos estáticos, migrações e testes.
- `requirements.txt`: dependências para executar o sistema.
- `.gitignore`: exclusão de banco local, segredos, ambiente virtual e arquivos gerados.

## Histórias da Sprint 01
- **US01:** autenticação e acesso conforme o perfil.
- **US02:** consultar demandas atribuídas ao fiscal.
- **US03:** visualizar detalhes de uma demanda.
- **US04:** iniciar ou continuar fiscalização.
- **US05:** preencher e salvar checklist.

## Verificação e evidências necessárias
1. Executar `python manage.py check` e `python manage.py test demandas` a partir de `src/backend/`.
2. Testar cada história com perfis distintos e registrar o resultado.
3. Anexar screencasts reais aos cards do Trello; não declarar testes não realizados.
4. Registrar bugs encontrados em issues do GitHub e relacioná-los às histórias.
5. Atualizar o board da Sprint 01 e documentar colaboração e programação em pares realizadas.
6. Abrir Pull Request para revisão da equipe antes de integrar à `main`.

## Limitações
O protótipo usa SQLite local; não publicar `db.sqlite3`. O número do processo SEI é registrado no sistema, sem integração automática com o SEI. Não alterar datas de commits para simular frequência de trabalho.
