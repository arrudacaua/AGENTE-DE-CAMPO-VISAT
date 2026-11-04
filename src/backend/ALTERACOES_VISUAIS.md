> Histórico da edição visual anterior. Para esta atualização e seus testes, consulte ALTERACOES_US02_US05.md.

# O que foi alterado na interface

Referência visual: vídeo de demonstração do Agente de Campo VISAT enviado pelo usuário.

| Tela | Redesign |
|---|---|
| Login | layout escuro com gradiente, apresentação e formulário em cartão |
| Gerência | métricas, donuts de status, barras por distrito, chips de prioridade |
| Fiscal | destaque de atividades, métricas e acesso às demandas |
| Lista | tabela no desktop, cartões no celular, busca e filtros locais |
| Detalhes | capa de demanda, status, ações, checklist, evidências e progresso |
| Cadastro | campos em grade no desktop e coluna no celular |
| Checklist | opções de resposta em cartões selecionáveis por toque |
| Relatório | página clara semelhante a documento para impressão |
| Navegação | sidebar no computador, drawer e navegação inferior no celular |

**Arquivos de frontend:** `templates/demandas/*.html`, `static/demandas/css/app.css`, `static/demandas/js/app.js`.

**Alterações mínimas no Python:** contexto de indicadores percentuais em `views.py`, sinalização dos formulários/papéis para os templates e tamanho/placeholder de campos em `forms.py`. Modelos, rotas e migrações foram preservados.

### O que o vídeo mostra mas o projeto ainda não executa

O visual não simula como reais recursos inexistentes. GPS, evidências em arquivo, IA, modo offline, SEI e PDF servidor **ainda necessitam de desenvolvimento**.

### Responsividade

Sem frameworks de CSS externos. Pontos de quebra em 1250, 1100, 800, 640 e 380 px. Botões acessíveis ao toque, safe area no menu do celular, campos com larguras fluidas, tabela alternativa para dispositivos estreitos.
