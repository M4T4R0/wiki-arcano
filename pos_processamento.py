#!/usr/bin/env python3
"""
pos_processamento.py — organiza docs/ depois do build_wiki.py.

Faz duas coisas, sem reescrever nenhuma palavra do texto de origem:

  1. PERSONAGENS: tira os personagens de dentro de reinos, cidades, estados tampões etc. e cria
     uma aba "Personagens" (docs/personagens/<origem>/<personagem>.md). No lugar original fica só o
     nome, com link.
  2. GUILDAS: tira as guildas/facções com texto próprio de dentro dos reinos e cria uma seção para
     cada uma (docs/faccoes/guildas/<origem>/<guilda>.md). No lugar original fica só o nome, com link.

O texto movido é copiado linha a linha. As únicas linhas novas são: o título (H1) da página nova,
uma linha "Origem: ..." com link de volta, e os links que ficam no lugar do texto movido.

Quais trechos mover é decidido na tabela OPERACOES abaixo (por texto de título, não por número de linha).

    P(inicio, fim)  -> a partir da linha 'inicio' (que fica como rótulo) até 'fim' (exclusive; None = fim da
                       página): cada linha só em negrito (**Nome**) abre um personagem.
    G(inicio, fim)  -> bloco de guilda que COMEÇA na linha 'inicio' (o nome) e vai até 'fim' (exclusive).
"""
import re
import unicodedata
from collections import Counter
from pathlib import Path


# ---------------------------------------------------------------------------
# Tabela de operações (ordem = ordem em que aparecem na página)
# ---------------------------------------------------------------------------
def P(inicio, fim=None, **kw):
    return {"tipo": "P", "inicio": inicio, "fim": fim, **kw}


def G(inicio, fim=None, **kw):
    return {"tipo": "G", "inicio": inicio, "fim": fim, **kw}


SUB_VULCAZAR = ["Vulcazar Pré-Selamento", "Vulcazar Pós-Selamento", "Exército de Vulcazar", "OS HU’RARIER DE VULCAZAR"]
PERS = "Personalidades Notáveis"

OPERACOES = {
    # ---- Reinos vassalos -------------------------------------------------
    "imperio/reinos-vassalos/jurubatiba.md": [
        P("Yasmim", fim="Facções", sem_rotulo=True, rotulo=PERS),
        G("A Ordem dos Estafetas Imperiais", "A Ordem dos Raxaxin"),
        G("A Ordem dos Raxaxin", "CIDADES VASSALAS"),
    ],
    "imperio/reinos-vassalos/aiso.md": [G("Templários de Aisó", None)],
    "imperio/reinos-vassalos/aratama.md": [
        G("Rilícia", "Ás da Guilda"),
        P("Ás da Guilda", fim=PERS),
        P(PERS),
    ],
    "imperio/reinos-vassalos/moacuba.md": [
        G("A ordem dos Senhores do Escudo", PERS),
        P(PERS),
    ],
    "imperio/reinos-vassalos/camua.md": [
        G("Organização Mundial do Livre comércio", "Enclave do Ermo", prefixo=True),
        G("Enclave do Ermo", "Figuras Notáveis"),
        P("Figuras Notáveis", fim="União Airyana dos Mensageiros", facao="Enclave do Ermo"),
        G("União Airyana dos Mensageiros", PERS),
        P(PERS),
    ],
    "imperio/reinos-vassalos/kaluana.md": [
        G("Aliança dos Lordes", "Figuras Notáveis"),
        P("Figuras Notáveis", fim="Ordem da Manopla", facao="Aliança dos Lordes"),
        G("Ordem da Manopla", "Figuras Notáveis"),
        P("Figuras Notáveis", fim=PERS, facao="Ordem da Manopla"),
        P(PERS),
    ],
    "imperio/reinos-vassalos/kise.md": [G("A Era", PERS), P(PERS)],
    "imperio/reinos-vassalos/nambiquara.md": [
        G("A Guilda dos Supay", "A Rede das Trevas"),
        G("A Rede das Trevas", "Figuras Notáveis"),
        P("Figuras Notáveis", fim=PERS, facao="A Rede das Trevas"),
        P(PERS),
    ],
    "imperio/reinos-vassalos/poranga.md": [
        G("Guilda dos Caçadores", "B.O.T.E"),
        G("B.O.T.E", "A Maré Sombria"),
        G("A Maré Sombria", "OS AMERÊ"),
        G("OS AMERÊ", PERS),
        P(PERS),
    ],
    "imperio/reinos-vassalos/ypiturui.md": [
        G("A Guida dos Yaotzin", "Guarda Açã"),
        G("Guarda Açã", "Iviturui"),
        G("Iviturui", PERS, nome="Iviturui (facção)"),
        P(PERS),
    ],
    "imperio/reinos-vassalos/ypy.md": [
        G("A Guarda Real de Ypy", "Rede Telepática Imperial"),
        G("Rede Telepática Imperial", PERS),
        P(PERS),
    ],
    # ---- Estados tampões -------------------------------------------------
    "imperio/estados-tampoes/terra-de-ninguem.md": [P(PERS)],
    "imperio/estados-tampoes/terra-dos-pistoleiros.md": [P(PERS)],
    "imperio/estados-tampoes/territorio-pacificado.md": [P(PERS)],
    # ---- Reinos e cidades fora do Império ---------------------------------
    "reinos/acuba.md": [
        G("Ordem da Areia Escarlate", "Conclave da Água Vital"),
        G("Conclave da Água Vital", "Irmandade das Sombras do Véu"),
        P("Personalidades Importantes"),
    ],
    "reinos/anama.md": [P(PERS)],
    "reinos/andira.md": [
        G("Ordem dos Ferreiros Eternos", "Confraria dos Exploradores do Mundo Interior"),
        P(PERS),
    ],
    "reinos/elfin.md": [
        G("Purificadores", "Moldadores"),
        G("Moldadores", PERS),
        P(PERS),
    ],
    "reinos/fortuna.md": [
        G("Guilda Pirata Ondeies", "Irmandade da Água Negra"),
        G("Guilda dos Assassinos", "Irmandade da Água Negra"),
        P(PERS, fim="As Nações livres do Extremo Sul", renomear={"Capitão": "Capitão do Estafeta Voador"}),
    ],
    "reinos/reino-dos-piquira.md": [G("Guilda dos Navegantes Celestes", "Ordem dos Inventores Eternos"), P(PERS)],
    "reinos/reino-dos-abaquar.md": [
        G("Ordem dos Ventos Eternos", "Irmandade das Lâminas de Cristal"),
        G("Irmandade das Lâminas de Cristal", "Círculo Arcano de Araxá"),
        G("Círculo Arcano de Araxá", "Observadores dos Abismos"),
        G("Observadores dos Abismos", "Confraria dos Viajantes Celestes"),
        G("Confraria dos Viajantes Celestes", None),
    ],
    "reinos/mbae.md": [G("Círculo das Sombras", "Guarda da Areia", fim_prefixo=True)],
    "reinos/ybi.md": [
        G("Círculo de Karnos", "Guarda do Sol Escarlate", fim_prefixo=True),
        P("Personalidades Importantes", fim="Personagens Notáveis"),
        P("Personagens Notáveis"),
    ],
    "reinos/terras-dos-aucas.md": [P(PERS)],
    "reinos/magos-das-trevas-de-vul.md": [P("Uzir Wraek", sem_rotulo=True, rotulo=PERS)],
    # ---- Mundo -------------------------------------------------------------
    "mundo/mundo-interior.md": [P(PERS)],
    "mundo/terra-selvagem.md": [
        P(PERS, fim="Personalidades Independentes", sub=SUB_VULCAZAR),
        P("Personalidades Independentes", fim="Tuk Bárbaro Burro"),
    ],
    # ---- Facções -----------------------------------------------------------
    "faccoes/arcanos-imperiais/personalidades-notaveis.md": [P(None, pagina_inteira=True)],
}

# Nome mostrado para a origem (quando o título da página não serve)
ORIGEM_NOME = {"faccoes/arcanos-imperiais/personalidades-notaveis.md": "Ordem dos Arcanos Imperiais"}
ORIGEM_SLUG = {"faccoes/arcanos-imperiais/personalidades-notaveis.md": "arcanos-imperiais"}
# Link de volta para a origem (quando a origem é a própria página de personalidades, aponta para o índice da Ordem)
ORIGEM_LINK = {"faccoes/arcanos-imperiais/personalidades-notaveis.md": "faccoes/arcanos-imperiais/index.md"}


# ---------------------------------------------------------------------------
# utilidades
# ---------------------------------------------------------------------------
NEGRITO = re.compile(r"^\*\*[^*].*\*\*:?\s*$")


def norm(t):
    t = t.strip()
    t = re.sub(r"^\*+|\*+:?$", "", t.strip()).strip()
    t = re.sub(r"\\(.)", r"\1", t).strip().rstrip(":").strip()
    return unicodedata.normalize("NFC", t).casefold()


def limpa_nome(t):
    t = t.strip()
    t = re.sub(r"^\*+|\*+:?\s*$", "", t).strip()
    t = re.sub(r"\\(.)", r"\1", t)
    return re.sub(r"\s+", " ", t).strip().rstrip(":").strip()


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t.lower()).strip("-")
    return t or "item"


def acha(linhas, texto, a, prefixo=False):
    alvo = unicodedata.normalize("NFC", texto).casefold()
    for i in range(a, len(linhas)):
        n = norm(linhas[i])
        if n == alvo or (prefixo and n.startswith(alvo)):
            return i
    raise SystemExit(f"pos_processamento: âncora não encontrada: '{texto}' (a partir da linha {a + 1})")


def corta(linhas):
    ini, fim = 0, len(linhas)
    while ini < fim and not linhas[ini].strip():
        ini += 1
    while fim > ini and not linhas[fim - 1].strip():
        fim -= 1
    return linhas[ini:fim]


def rel(de_arquivo, para_arquivo):
    """link relativo entre dois arquivos de docs/ (caminhos posix relativos a docs/)"""
    import os
    return os.path.relpath(para_arquivo, start=os.path.dirname(de_arquivo)).replace(os.sep, "/")


# ---------------------------------------------------------------------------
def executa(docs: Path, ordem=None):
    """Aplica OPERACOES em docs/. Devolve dict com o que foi criado (para menu/índices).
    ordem: lista de páginas (relativas a docs/) na ordem do menu, para ordenar os índices."""
    personagens = []   # dict(origem_arq, origem_nome, origem_slug, nome, arq)
    guildas = []       # idem
    relatorio = []
    pendentes = []     # (arquivo_novo, linhas_corpo, origem_arq, facao)

    usados = {}        # (pasta, slug) -> n

    def slug_unico(pasta, nome):
        s = slug(nome)
        k = (pasta, s)
        usados[k] = usados.get(k, 0) + 1
        return s if usados[k] == 1 else f"{s}-{usados[k]}"

    resultado_paginas = {}
    titulos_trocados = {}

    pares = sorted(OPERACOES.items(), key=lambda kv: ordem.index(kv[0]) if ordem and kv[0] in ordem else 10**6)
    for arq, ops in pares:
        caminho = docs / arq
        orig = caminho.read_text(encoding="utf-8").split("\n")
        titulo_pagina = limpa_nome(orig[0].lstrip("# "))
        o_nome = ORIGEM_NOME.get(arq, titulo_pagina)
        o_slug = ORIGEM_SLUG.get(arq, Path(arq).stem)
        o_link_arq = ORIGEM_LINK.get(arq, arq)

        # 1) localizar todos os trechos (em ordem) -------------------------------------------------
        trechos = []  # (a, b, op)  [a, b) linhas substituídas/retiradas
        cursor = 0
        for op in ops:
            if op["tipo"] == "G":
                a = acha(orig, op["inicio"], cursor, op.get("prefixo", False))
                b = acha(orig, op["fim"], a + 1, op.get("fim_prefixo", False)) if op["fim"] else len(orig)
                trechos.append((a, b, op))
                cursor = a + 1
            else:  # P
                if op.get("pagina_inteira"):
                    a = 0  # título H1 fica; região começa na linha 1
                    b = len(orig)
                    trechos.append((a, b, op))
                    cursor = 1
                    continue
                a = acha(orig, op["inicio"], cursor)
                b = acha(orig, op["fim"], a + 1) if op["fim"] else len(orig)
                trechos.append((a, b, op))
                cursor = a + 1

        trocados = titulos_trocados.setdefault(arq, set())
        # 2) montar a página nova ------------------------------------------------------------------
        novo = []
        pos = 0
        for a, b, op in trechos:
            novo += orig[pos:a]
            if op["tipo"] == "G":
                nome = op.get("nome") or limpa_nome(orig[a])
                trocados.add(orig[a].strip())
                corpo = corta(orig[a + 1:b])
                pasta_novo = f"faccoes/guildas/{o_slug}"
                s = slug_unico(pasta_novo, nome)
                novo_arq = f"{pasta_novo}/{s}.md"
                guildas.append(dict(origem_arq=o_link_arq, origem_nome=o_nome, origem_slug=o_slug, nome=nome, arq=novo_arq))
                pendentes.append((novo_arq, nome, corpo, o_link_arq, o_nome, None, "guilda"))
                novo += ["", f"**[{nome}]({rel(arq, novo_arq)})**", ""]
                relatorio.append(("GUILDA", arq, nome, len(corpo)))
            else:
                inicio_regiao = (a if op.get("sem_rotulo") else a + 1) if not op.get("pagina_inteira") else 1
                regiao = orig[inicio_regiao:b]
                # rótulo
                if op.get("pagina_inteira"):
                    novo += orig[:1]
                elif op.get("sem_rotulo"):
                    novo += ["", f"**{op['rotulo']}**", ""]
                else:
                    novo += [orig[a]]
                # itens
                sub = {norm(x) for x in op.get("sub", [])}
                idx = [i for i, l in enumerate(regiao) if NEGRITO.match(l) and norm(l) not in sub]
                if not idx:
                    novo += regiao
                    pos = b
                    continue
                intro = corta(regiao[:idx[0]])
                if intro:
                    novo += [""] + intro
                for k, i in enumerate(idx):
                    j = idx[k + 1] if k + 1 < len(idx) else len(regiao)
                    nome = limpa_nome(regiao[i])
                    nome = op.get("renomear", {}).get(nome, nome)
                    trocados.add(regiao[i].strip())
                    corpo = corta(regiao[i + 1:j])
                    if not corpo:
                        # nome sem texto no livro: fica como está, sem página
                        novo += ["", regiao[i], ""]
                        relatorio.append(("SEM TEXTO", arq, nome, 0))
                        continue
                    pasta_novo = f"personagens/{o_slug}"
                    s = slug_unico(pasta_novo, nome)
                    novo_arq = f"{pasta_novo}/{s}.md"
                    personagens.append(dict(origem_arq=o_link_arq, origem_nome=o_nome, origem_slug=o_slug, nome=nome, arq=novo_arq))
                    pendentes.append((novo_arq, nome, corpo, o_link_arq, o_nome, op.get("facao"), "personagem"))
                    novo += ["", f"**[{nome}]({rel(arq, novo_arq)})**", ""]
                    relatorio.append(("PERSONAGEM", arq, nome, len(corpo)))
                # sobra depois do último item? (não há: o último item vai até o fim da região)
            pos = b
        novo += orig[pos:]
        # compacta linhas em branco repetidas
        saida, vazias = [], 0
        for l in novo:
            if l.strip() == "":
                vazias += 1
                if vazias > 1:
                    continue
            else:
                vazias = 0
            saida.append(l)
        resultado_paginas[arq] = ("\n".join(saida).rstrip() + "\n", orig)

    # 3) gravar páginas novas ----------------------------------------------------------------------
    guilda_por_nome = {(g["origem_slug"], g["nome"]): g for g in guildas}
    for novo_arq, nome, corpo, o_link_arq, o_nome, facao, tipo in pendentes:
        linhas = [f"# {nome}", ""]
        cab = f"*Origem: [{o_nome}]({rel(novo_arq, o_link_arq)})*"
        if facao:
            for (os_, gn), g in guilda_por_nome.items():
                if gn == facao and g["origem_arq"] == o_link_arq:
                    cab += f" · *Facção: [{facao}]({rel(novo_arq, g['arq'])})*"
                    break
        linhas += [cab, ""] + corpo + [""]
        dest = docs / novo_arq
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("\n".join(linhas), encoding="utf-8", newline="\n")

    # 4) conferir que nenhuma linha de texto se perdeu e gravar as páginas de origem ---------------------
    novos_por_origem = {}
    for novo_arq, nome, corpo, o_link_arq, o_nome, facao, tipo in pendentes:
        novos_por_origem.setdefault(o_link_arq, []).extend(corpo)
    for arq, (texto, orig) in resultado_paginas.items():
        o_link_arq = ORIGEM_LINK.get(arq, arq)
        corpos = []
        for novo_arq, nome, corpo, olink, *_ in pendentes:
            if olink == o_link_arq:
                corpos += corpo
        antes = Counter(l.strip() for l in orig if l.strip())
        depois = Counter(l.strip() for l in texto.split("\n") if l.strip())
        depois.update(l.strip() for l in corpos if l.strip())
        faltando = antes - depois
        # só podem "faltar" os títulos que viraram links/H1
        ruins = [l for l in faltando if l not in titulos_trocados.get(arq, set())]
        if ruins:
            raise SystemExit(f"pos_processamento: texto perdido em {arq}: {ruins[:5]}")
        (docs / arq).write_text(texto, encoding="utf-8", newline="\n")

    return {"personagens": personagens, "guildas": guildas, "relatorio": relatorio}


# ---------------------------------------------------------------------------
# índices e menu
# ---------------------------------------------------------------------------
def agrupa(itens):
    grupos = {}
    for it in itens:
        grupos.setdefault((it["origem_slug"], it["origem_nome"], it["origem_arq"]), []).append(it)
    return grupos


def escreve_indices(docs: Path, info):
    # --- Personagens ---
    L = ["# Personagens", "",
         "Personagens do cenário, reunidos por lugar de origem. Em cada reino, cidade ou região o nome aparece com link para cá.", ""]
    for (s, nome, arq), itens in agrupa(info["personagens"]).items():
        L += [f"## {nome}", "", f"*Origem: [{nome}]({rel('personagens/index.md', arq)})*", ""]
        L += [f"- [{it['nome']}]({rel('personagens/index.md', it['arq'])})" for it in itens]
        L += [""]
    ameacas = [("Misty As-La", "ameacas/misty-as-la.md"), ("Eligos, o Primeiro Duque do Inferno", "ameacas/eligos.md"),
              ("Vlad Dracul, o Mago das Trevas Vampiro", "ameacas/vlad-dracul.md")]
    if all((docs / a).exists() for _, a in ameacas):
        L += ["## Vilões com página própria em Ameaças", ""]
        L += [f"- [{n}]({rel('personagens/index.md', a)})" for n, a in ameacas]
        L += [""]
    (docs / "personagens").mkdir(exist_ok=True)
    (docs / "personagens" / "index.md").write_text("\n".join(L), encoding="utf-8", newline="\n")

    # --- Guildas ---
    L = ["# Guildas e Facções dos Reinos", "",
         "Guildas, ordens e facções com texto próprio, reunidas por lugar de origem. "
         "A lista de nomes avulsos está em [Outras Guildas e Facções](../outras-guildas.md).", ""]
    for (s, nome, arq), itens in agrupa(info["guildas"]).items():
        L += [f"## {nome}", "", f"*Origem: [{nome}]({rel('faccoes/guildas/index.md', arq)})*", ""]
        L += [f"- [{it['nome']}]({rel('faccoes/guildas/index.md', it['arq'])})" for it in itens]
        L += [""]
    (docs / "faccoes" / "guildas").mkdir(parents=True, exist_ok=True)
    (docs / "faccoes" / "guildas" / "index.md").write_text("\n".join(L), encoding="utf-8", newline="\n")


def nav_extra(info):
    """Estruturas de menu (formato do build_wiki: str | {titulo: str|lista})."""
    def secao(itens):
        out = []
        for (s, nome, arq), grp in agrupa(itens).items():
            out.append({nome: [{it["nome"]: it["arq"]} for it in grp]})
        return out

    nav_pers = ["personagens/index.md"] + secao(info["personagens"])
    nav_guil = ["faccoes/guildas/index.md"] + secao(info["guildas"])
    return nav_pers, nav_guil
