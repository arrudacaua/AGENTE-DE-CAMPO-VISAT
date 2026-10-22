# Alterações US02–US05

## Backend

- Querysets limitados ao fiscal logado; outra demanda retorna 404.
- Gerência mantém visão global e validação de conclusão.
- Cadastro força status inicial Em aberto, mesmo com status forjado no POST.
- Fiscais elegíveis excluem contas inativas, staff, superusuários e grupo Gerencia.
- POST com CSRF para iniciar/concluir/homologar/vincular.
- Checklist e evidências só editáveis Em andamento e sem homologação.
- Conclusão exige os seis itens padrão, todas as respostas válidas e confirmação.
- Checklist validado inteiro antes da gravação; item estrangeiro, múltiplas respostas
  e valores inválidos são rejeitados sem salvar parcialmente.
- Revisão otimista retorna 409 para formulário antigo, evitando sobrescrita silenciosa.
- Demandas são salvas por transação com os respectivos itens.

## Interface

- OS, bairro e prioridade presentes em tabela e cartões.
- Busca no servidor, filtro explícito e paginação de 20 registros.
- Prazo mais próximo apresentado com ano.
- Detalhe e lista toleram fiscal ausente.
- Mapa ampliado em diálogo com fechamento e retorno de foco; endereço visível
  mesmo quando o serviço externo não carrega.
- Checklist usa grupos de duas opções, aviso de alterações não salvas e confirmação
  após salvar; respostas sem seleção continuam pendentes.
- Iniciar/Continuar abre checklist. Conclusão/homologação têm mensagens distintas.

## Fora do escopo

Executável, upload de fotos, IA, sincronização offline e integração real com SEI.
O relatório demonstrativo mantém seu conteúdo original, sem inclusão de evidências.

## Validação

17 testes automatizados aprovados; verificação Django sem problemas; nenhuma migration
pendente de geração. Migração de cópia do SQLite original preservou seus dados.
Não foi possível executar a verificação visual em navegador nesta entrega.
