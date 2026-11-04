# Agente de Campo — VISAT

Atualização US02–US05, mantendo Django, SQLite e a interface existente.

Comece por **LEIA_PRIMEIRO_ATUALIZACAO.txt** para atualizar uma instalação no Windows
sem substituir seu banco ou perder sua conta. Este pacote não inclui banco, senhas,
ambiente virtual nem dados de demonstração.

## Entregue

- US02: painel com ativas e prazo mais próximo, lista isolada por fiscal, OS,
  SEI, prioridade, status, distrito, bairro e prazo; pesquisa no servidor e paginação.
- US03: detalhe completo, ausência de fiscal tratada, coordenadas opcionais validadas,
  edição da localização pela gerência e mapa ampliado OpenStreetMap.
- US04: iniciar via POST protegido por CSRF, redirecionamento ao checklist, retomada,
  bloqueio no servidor fora do estado Em andamento e situação da homologação.
- US05: seis itens, duas respostas possíveis por item, gravação explícita,
  persistência, validação atômica e detecção de formulário desatualizado.

Número da OS é um identificador opcional separado do número automático da demanda.
Coordenadas antigas ficam vazias. Não há geocodificação automática nem coleta da
localização do dispositivo. A gerência informa as coordenadas do local.

## Instalação nova (Windows, Python 3.13)

```bat
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py createsuperuser
.venv\Scripts\python.exe manage.py runserver
```

Abra http://127.0.0.1:8000. Em instalação existente, preserve o banco e a .venv e
siga o guia; não é necessário criar outro superusuário.

## Testes

```bat
.venv\Scripts\python.exe manage.py test demandas
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

17 testes cobrem o fluxo, acesso por usuário, validações, salvamento e migração de
registros anteriores. A migração também foi aplicada sobre cópia do banco enviado,
com comparação das colunas originais e dos dados de usuários e sessões.
Veja o guia para limitações de verificação visual e do ambiente Windows.

## Banco e compatibilidade

- 0002 adiciona OS, latitude, longitude e revisão sem substituir tabelas de usuários.
- 0003 completa os seis itens ausentes apenas em demandas ativas e não homologadas,
  preservando respostas existentes e fiscalizações encerradas.
- Os itens de demandas novas são criados uma única vez, junto do cadastro.
- Conteúdo antigo adicional do checklist é preservado e também deve ser respondido.
- No admin, status e validações do fluxo ficam somente para consulta; fiscalizações
  encerradas ficam com campos somente para leitura. Usuários continuam gerenciáveis.

## Limites

Evidências permanecem textuais. Relatórios e vínculo com SEI continuam demonstrativos.
Mapas exigem internet e usam serviço externo. O núcleo local não usa CDN.
DEBUG e demais configurações originais são de desenvolvimento; esta entrega não é
uma configuração de produção nem um inicializador executável Windows.
