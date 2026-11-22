#!/usr/bin/env python3
"""
gera_indice.py — recria o índice do topo de fonte/ARCANO.md com links que funcionam.

O que faz (e só isso):
  1. Troca o sumário antigo do Google Docs (links "#heading=" quebrados) por um índice novo,
     organizado como a wiki (Lore, Mundo, História, Povos, Império, Reinos, Facções, Ameaças...).
  2. Tira dos títulos o sufixo "{#id}" do Google Docs, que impede o link de funcionar no GitHub/VS Code,
     junta espaços duplicados dentro do título e remove os títulos vazios ("# " sozinho).
  O texto do cenário NÃO é alterado.

Uso:
    python gera_indice.py                 # usa fonte/ARCANO.md
    python gera_indice.py outro/arquivo.md

Pode rodar de novo sempre que editar o ARCANO.md: o bloco entre
<!-- INDICE:INICIO --> e <!-- INDICE:FIM --> é refeito a cada execução.
Depois, rode `python build_wiki.py` para atualizar a wiki.
"""
import re
import sys
import unicodedata
from pathlib import Path

import build_wiki as B

RAIZ = Path(__file__).parent
INI, FIM = "<!-- INDICE:INICIO -->", "<!-- INDICE:FIM -->"

# Divisórias da fonte (título sem texto próprio) e seção descartada: entram no índice na posição do documento
ANTES_DE = {"O MUNDO": "GEOGRAFIA", "O Reino Submerso": "AS ILHAS", "AS RUÍNAS DE RATANABA": "CIDADES PERDIDAS"}
FORA_DA_WIKI = "IDEIAS"
NOME_DIVISORIA = {"GEOGRAFIA": "Geografia", "AS ILHAS": "As Ilhas", "CIDADES PERDIDAS": "Cidades Perdidas"}


def slug_github(titulo, vistos):
    """Âncora no padrão do GitHub / VS Code (mantém acentos; repete com -1, -2 se o título se repetir)."""
    t = B.limpa_titulo(titulo)
    t = re.sub(r"[^\w\- ]", "", t.lower()).replace(" ", "-")
    n = vistos.get(t, 0)
    vistos[t] = n + 1
    return t if n == 0 else f"{t}-{n}"


def limpa_cabecalhos(linhas):
    """Tira '{#id}' dos títulos e descarta títulos vazios. Não mexe em mais nada."""
    out = []
    for l in linhas:
        m = re.match(r"^(#{1,6})\s(.*)$", l)
        if m:
            resto = re.sub(r"\s*\{#[^}]*\}\s*$", "", m.group(2)).strip()
            resto = re.sub(r"[ \t]{2,}", " ", resto)  # espaço duplo no título gera âncoras diferentes em cada leitor
            if not resto:
                continue
            l = f"{m.group(1)} {resto}"
        out.append(l)
    return out


def coleta(corpo):
    secs, vistos = [], {}
    for i, l in enumerate(corpo):
        m = re.match(r"^(#{1,6}) (.*)$", l)
        if m:
            secs.append({"titulo": B.limpa_titulo(m.group(2)), "ancora": slug_github(m.group(2), vistos),
                         "linha": i, "usada": False})
    return secs


def link(secs, alvo, texto=None):
    s = B.acha(secs, alvo)
    s["usada"] = True
    return f"[{texto or s['titulo']}](#{s['ancora']})"


def monta_indice(secs):
    L = []
    add = lambda nivel, txt: L.append("  " * nivel + "- " + txt)

    add(0, link(secs, "ARCANO", "Arcano & Airy — Início"))
    add(0, link(secs, "Introdução"))

    grupos = {pasta: (nome, itens) for nome, pasta, itens in B.ESTRUTURA}

    def itens_do_grupo(pasta, nivel):
        nome, itens = grupos[pasta]
        indice = next((it for it in itens if it[1] == "index"), None)
        if indice:
            fonte = indice[0] if isinstance(indice[0], str) else indice[0][0]
            rotulo = f"**{link(secs, fonte, nome)}**"
        else:
            rotulo = f"**{nome}**"
        add(nivel, rotulo)
        if indice and not isinstance(indice[0], str):
            for extra in indice[0][1:]:
                add(nivel + 1, link(secs, extra))
        for fonte, arq, titulo in itens:
            if arq == "index":
                continue
            lista = fonte if isinstance(fonte, list) else [fonte]
            if lista[0] in ANTES_DE:
                add(nivel + 1, link(secs, ANTES_DE[lista[0]], NOME_DIVISORIA[ANTES_DE[lista[0]]]))
            add(nivel + 1, link(secs, lista[0], titulo))
            for filho in lista[1:]:
                add(nivel + 2, link(secs, filho))
        # subgrupos diretos (ex.: imperio/reinos-vassalos dentro de imperio)
        for p in grupos:
            if p.startswith(pasta + "/") and p.count("/") == pasta.count("/") + 1:
                itens_do_grupo(p, nivel + 1)

    topo = [p for p in grupos if "/" not in p]
    for p in topo:
        itens_do_grupo(p, 0)

    # divisórias que ficaram de fora do agrupamento acima + material fora do cenário
    restantes = [s for s in secs if not s["usada"] and s["titulo"] != FORA_DA_WIKI]
    if restantes:
        add(0, "**Outros títulos do documento**")
        for s in restantes:
            s["usada"] = True
            add(1, f"[{s['titulo']}](#{s['ancora']})")
    fora = next((s for s in secs if s["titulo"] == FORA_DA_WIKI), None)
    if fora:
        fora["usada"] = True
        add(0, "**Fora da wiki** (material de apoio, não publicado no site)")
        add(1, f"[{fora['titulo']}](#{fora['ancora']})")
    return L


def main():
    arq = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "fonte" / "ARCANO.md"
    linhas = arq.read_text(encoding="utf-8-sig").replace("\r\n", "\n").split("\n")

    # onde começa o corpo: depois do bloco de índice atual (se já existe) ou no título "ARCANO"
    if FIM in linhas:
        ini = linhas.index(FIM) + 1
    else:
        ini = next(i for i, l in enumerate(linhas)
                   if (m := re.match(r"^# (.*)$", l)) and B.limpa_titulo(m.group(1)) == "ARCANO")
    corpo = limpa_cabecalhos(linhas[ini:])
    while corpo and not corpo[0].strip():
        corpo.pop(0)

    secs = coleta(corpo)
    indice = monta_indice(secs)

    # conferências: todo título com texto está no índice, e todo link aponta para um título
    ancoras = {s["ancora"] for s in secs}
    usados = re.findall(r"\]\(#([^)]*)\)", "\n".join(indice))
    assert all(a in ancoras for a in usados), "link do índice sem título correspondente"
    faltam = [s["titulo"] for s in secs if not s["usada"]]
    assert not faltam, f"títulos fora do índice: {faltam}"
    assert len(usados) == len(set(usados)), "título repetido no índice"

    topo = ["# Índice", "", INI, "", *indice, "", FIM, ""]
    arq.write_text("\n".join(topo + corpo), encoding="utf-8", newline="\n")
    print(f"OK: índice com {len(usados)} links gravado em {arq}")


if __name__ == "__main__":
    main()
