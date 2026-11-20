"""US08 - Rascunho do relatório técnico gerado automaticamente.

O rascunho é montado a partir do que o fiscal já registrou na fiscalização
(checklist, evidências e anotações). Não há chamada a serviço externo de IA:
o texto é produzido localmente, de forma determinística, e sempre marcado como
RASCUNHO. A revisão pelo fiscal (US09) e a assinatura (US10) continuam
obrigatórias antes de qualquer uso oficial.
"""

TITULO = "RELATÓRIO TÉCNICO SANITÁRIO"
SELO_RASCUNHO = "RASCUNHO GERADO AUTOMATICAMENTE - REVISÃO OBRIGATÓRIA"
RODAPE = (
    "Rascunho gerado automaticamente a partir dos registros da fiscalização. "
    "Deve ser revisado pelo fiscal responsável antes da assinatura. "
    "Nenhuma integração real com o SEI foi realizada."
)

NAO_INFORMADO = "Não informado"


def _data(valor):
    return valor.strftime("%d/%m/%Y") if valor else NAO_INFORMADO


def _coordenadas(registro):
    if registro.latitude is not None and registro.longitude is not None:
        return f"{registro.latitude}, {registro.longitude}"
    return ""


def _identificacao(demanda):
    os_ = demanda.numero_os or NAO_INFORMADO
    return [
        f"Demanda: {demanda.numero}",
        f"Número da OS: {os_}",
        f"Processo SEI: {demanda.processo_sei}",
        f"Fiscal responsável: {demanda.fiscal_nome}",
        f"Local: {demanda.endereco}, {demanda.bairro} - {demanda.distrito}",
        f"Data de recebimento: {_data(demanda.data_recebimento)}",
        f"Prazo: {_data(demanda.prazo)}",
        f"Descrição da demanda: {demanda.descricao}",
    ]


def _fatos_constatados(itens):
    """Resume o checklist: conformes, não conformes e itens sem resposta."""
    conformes = [i.item for i in itens if i.resposta == "conforme"]
    nao_conformes = [i.item for i in itens if i.resposta == "nao_conforme"]
    pendentes = [i.item for i in itens if not i.resposta]

    linhas = [
        f"Itens verificados: {len(conformes) + len(nao_conformes)} de {len(itens)}.",
    ]
    if nao_conformes:
        linhas.append("Não conformidades constatadas:")
        linhas += [f"- {item}" for item in nao_conformes]
    else:
        linhas.append("Nenhuma não conformidade registrada no checklist.")
    if conformes:
        linhas.append("Itens em conformidade: " + "; ".join(conformes) + ".")
    if pendentes:
        linhas.append("Itens sem resposta (completar antes de concluir): " + "; ".join(pendentes) + ".")
    return linhas, nao_conformes


def _evidencias(evidencias):
    if not evidencias:
        return ["Nenhuma evidência registrada até o momento."]
    linhas = [f"Total de evidências registradas: {len(evidencias)}."]
    for ev in evidencias:
        partes = [ev.get_tipo_display()]
        if ev.criada_em:
            partes.append(ev.criada_em.strftime("%d/%m/%Y %H:%M"))
        gps = _coordenadas(ev)
        if gps:
            partes.append(f"GPS {gps}")
        texto = " | ".join(partes)
        descricao = (ev.descricao or "").strip()
        linhas.append(f"- {texto}" + (f": {descricao}" if descricao else ""))
    return linhas


def _anotacoes(demanda):
    texto = (demanda.anotacoes or "").strip()
    return [texto] if texto else ["Sem anotações do fiscal."]


def _recomendacoes(nao_conformes, pendentes):
    if nao_conformes:
        linhas = [
            "Recomenda-se notificar o responsável pelo estabelecimento para "
            "regularizar os itens não conformes listados acima e definir prazo "
            "para nova verificação."
        ]
    else:
        linhas = [
            "Com base nos registros, não foram constatadas não conformidades. "
            "Recomenda-se o arquivamento após a homologação pela Gerência VISAT."
        ]
    if pendentes:
        linhas.append("Há itens do checklist sem resposta; conclua-os antes de assinar.")
    linhas.append("Conclusão sujeita à revisão do fiscal e à homologação da Gerência VISAT.")
    return linhas


def montar_rascunho(demanda):
    """Devolve o texto do rascunho para a demanda informada."""
    itens = list(demanda.itens_checklist.order_by("id"))
    evidencias = list(demanda.evidencias.order_by("criada_em"))

    fatos, nao_conformes = _fatos_constatados(itens)
    pendentes = [i for i in itens if not i.resposta]

    secoes = [
        (TITULO, [SELO_RASCUNHO]),
        ("1. Identificação", _identificacao(demanda)),
        ("2. Fatos constatados", fatos),
        ("3. Evidências", _evidencias(evidencias)),
        ("4. Anotações do fiscal", _anotacoes(demanda)),
        ("5. Recomendações e conclusão", _recomendacoes(nao_conformes, pendentes)),
    ]
    blocos = ["\n".join([titulo, *linhas]) for titulo, linhas in secoes]
    return "\n\n".join(blocos) + f"\n\n{RODAPE}"
