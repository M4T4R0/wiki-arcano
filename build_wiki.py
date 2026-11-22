#!/usr/bin/env python3
"""
build_wiki.py — reconstrói a Wiki Arcano & Airy a partir do documento de origem.

Fonte única de verdade: fonte/ARCANO.md
Saída: docs/  (páginas .md)  +  mkdocs.yml

Rode sempre que o documento de origem mudar:
    python build_wiki.py

Depois de gerar as páginas, o script ainda roda duas etapas (ver os módulos):
  * pos_processamento.py  -> tira personagens e guildas de dentro dos reinos e cria a aba "Personagens"
                             e a seção "Guildas e Facções dos Reinos" (no lugar fica só nome + link)
  * crosslink_seguro.py   -> links cruzados que não alteram o texto

Regras:
  * O texto da fonte NUNCA é reescrito; só se ajusta marcação (títulos, caracteres de controle).
  * Uma página por seção da fonte. Nada de arquivos duplicados nem páginas só com template.
  * Para mudar a organização (pastas, nomes, ordem), edite apenas ESTRUTURA abaixo.
"""
import os, re, shutil, sys, unicodedata
from pathlib import Path

import crosslink_seguro
import mapa_interativo
import pos_processamento

RAIZ = Path(__file__).parent
FONTE = RAIZ / "fonte" / "ARCANO.md"
DOCS = RAIZ / "docs"
MARCADOR_MAPA = "<!--MAPA-INTERATIVO-->"   # na home; vira o mapa clicável depois dos links cruzados
IMAGENS = RAIZ / "fonte" / "imagens"   # imagens do ARCANO.md: ![descrição](imagens/arquivo.png)

# ---------------------------------------------------------------------------
# ESTRUTURA — (título na fonte, arquivo, título no menu)
#   arquivo "index"  -> página de abertura da pasta
#   título na fonte como lista -> várias seções da fonte viram UMA página
# ---------------------------------------------------------------------------
ESTRUTURA = [
    ("Lore e Cosmologia", "lore", [
        ("O MITO DA CRIAÇÃO", "criacao", "O Mito da Criação"),
        ("OS PLANOS DE EXISTÊNCIA", "planos-de-existencia", "Os Planos de Existência"),
    ]),
    ("O Mundo", "mundo", [
        ("O MUNDO", "o-mundo", "O Mundo"),
        ("LOCAIS DE INTERESSE NO MUNDO", "locais-de-interesse", "Locais de Interesse"),
        ("O Templo do Conhecimento", "templo-do-conhecimento", "O Templo do Conhecimento"),
        ("FLORESTA KA’AQWY", "floresta-kaaqwy", "Floresta Ka’aqwy"),
        ("MUNDO INTERIOR", "mundo-interior", "Mundo Interior"),
        ("DESERTO AÇU", "deserto-acu", "Deserto Açu"),
        ("Montes Brancos", "montes-brancos", "Montes Brancos"),
        ("Terra dos Kaapora", "terra-dos-kaapora", "Terra dos Kaapora"),
        ("TERRA SELVAGEM", "terra-selvagem", "Terra Selvagem"),
        ("O Reino Submerso", "reino-submerso", "O Reino Submerso"),
        ("AS RUÍNAS DE RATANABA", "ruinas-de-ratanaba", "As Ruínas de Ratanaba"),
    ]),
    ("História", "historia", [
        ("A ERA DO ESQUECIMENTO", "era-do-esquecimento", "A Era do Esquecimento"),
        ("A INVENÇÃO DE ARTHUR ÁUREO", "invencao-de-arthur-aureo", "A Invenção de Arthur Áureo"),
        (["A Linha do Tempo de Airy", "A Era dos Deuses", "A Era dos Demônios", "A Era dos Gigantes",
          "Era dos Akitã e Abaré", "A Era dos Aba"], "linha-do-tempo-de-airy", "Linha do Tempo de Airy"),
        ("A ERA DO IMPÉRIO", "era-do-imperio", "A Era do Império"),
        ("LINHA DO TEMPO DE ASLARETH", "linha-do-tempo-de-aslareth", "Linha do Tempo de Aslareth"),
    ]),
    ("Povos", "povos", [
        ("OS POVOS", "index", "Os Povos"),
        ("Os Humanos Aba", "humanos-aba", "Humanos Aba"),
        ("Os Elfos Abaré", "elfos-abare", "Elfos Abaré"),
        ("Meio-Elfos", "meio-elfos", "Meio-Elfos"),
        ("Os Anões Akitã", "anoes-akita", "Anões Akitã"),
        ("Os Halflings Kaapora", "halflings-kaapora", "Halflings Kaapora"),
        ("Os Gnomos Piquira", "gnomos-piquira", "Gnomos Piquira"),
        ("Os Kemonos Yawara", "kemonos-yawara", "Kemonos Yawara"),
        ("Os Orcs Abaité", "orcs-abaite", "Orcs Abaité"),
        ("Meio-Orc", "meio-orc", "Meio-Orc"),
        ("Licantropos", "licantropos", "Licantropos"),
        ("Os Meio-Gigantes Anaiti", "meio-gigantes-anaiti", "Meio-Gigantes Anaiti"),
        ("Os Auçá", "auca", "Auçá"),
        ("Os Abaquar", "abaquar", "Abaquar"),
        ("As Icamiabas", "icamiabas", "Icamiabas"),
        ("Reptantes", "reptantes", "Reptantes"),
        ("Minotauros", "minotauros", "Minotauros"),
        ("Gnól", "gnol", "Gnól"),
        ("Goblinoides", "goblinoides", "Goblinoides"),
    ]),
    ("O Império", "imperio", [
        ("IMPÉRIO", "index", "O Império"),
        ("Os Símbolos Imperiais", "simbolos-imperiais", "Os Símbolos Imperiais"),
        ("A História do Império", "historia-do-imperio", "A História do Império"),
        ("Organização Política", "organizacao-politica", "Organização Política"),
        ("O Imperador", "o-imperador", "O Imperador"),
        ("A Corte", "a-corte", "A Corte"),
        ("Relação dos Nobres com a política", "nobres-e-politica", "Relação dos Nobres com a Política"),
        ("Democracia", "democracia", "Democracia"),
        ("Ministérios", "ministerios", "Ministérios"),
        ("Política do Império", "politica-do-imperio", "Política do Império"),
        ("O Senado", "o-senado", "O Senado"),
        ("O Plenário do Senado Imperial", "plenario-do-senado", "O Plenário do Senado Imperial"),
        ("O Paralelo Histórico", "paralelo-historico", "O Paralelo Histórico"),
        ("A Máquina de Propaganda Estatal", "maquina-de-propaganda", "A Máquina de Propaganda Estatal"),
        ("Cargos Públicos mais Importantes", "cargos-publicos", "Cargos Públicos mais Importantes"),
        ("O Trabalho no Império", "trabalho", "O Trabalho no Império"),
        ("A Educação no Império", "educacao", "A Educação no Império"),
    ]),
    ("Reinos Vassalos", "imperio/reinos-vassalos", [
        ("Reinos Vassalos", "index", "Reinos Vassalos"),
        ("Ypy", "ypy", "Ypy"),
        ("Kisé", "kise", "Kisé"),
        ("Moacuba", "moacuba", "Moacuba"),
        ("Aratama", "aratama", "Aratama"),
        ("Aisó", "aiso", "Aisó"),
        ("Camuá", "camua", "Camuá"),
        ("Jurubatiba", "jurubatiba", "Jurubatiba"),
        ("Kaluana", "kaluana", "Kaluana"),
        ("Nambiquara", "nambiquara", "Nambiquara"),
        ("Poranga", "poranga", "Poranga"),
        ("Ypiturui", "ypiturui", "Ypiturui"),
    ]),
    ("Estados Tampões", "imperio/estados-tampoes", [
        ("ESTADOS TAMPÕES DO IMPÉRIO", "index", "Estados Tampões do Império"),
        ("A Área da Infestação", "area-da-infestacao", "A Área da Infestação"),
        ("A Terra dos Pistoleiros", "terra-dos-pistoleiros", "A Terra dos Pistoleiros"),
        ("A Terra de Ninguém", "terra-de-ninguem", "A Terra de Ninguém"),
        ("Território Pacificado", "territorio-pacificado", "Território Pacificado"),
        ("Vale dos Condenados", "vale-dos-condenados", "Vale dos Condenados"),
    ]),
    ("Reinos e Cidades fora do Império", "reinos", [
        ("IMPÉRIO, QUAL IMPÉRIO?", "index", "Império, Qual Império?"),
        ("Reino dos Abaré", "reino-dos-abare", "Reino dos Abaré"),
        ("Elfin", "elfin", "Elfin"),
        ("Reino dos Abaquar", "reino-dos-abaquar", "Reino dos Abaquar"),
        ("Reino dos Piquira", "reino-dos-piquira", "Reino dos Piquira"),
        ("Andirá", "andira", "Andirá"),
        ("Aslareth", "aslareth", "Aslareth"),
        ("AS CIDADES LIVRES", "as-cidades-livres", "As Cidades Livres"),
        ("Vul", "vul", "Vul"),
        ("Os Magos das Trevas de Vul", "magos-das-trevas-de-vul", "Os Magos das Trevas de Vul"),
        ("Fortuna", "fortuna", "Fortuna"),
        ("Ybytu", "ybytu", "Ybytu"),
        ("Arani", "arani", "Arani"),
        ("Tamaya", "tamaya", "Tamaya"),
        ("Mbaê", "mbae", "Mbaê"),
        ("Ybi", "ybi", "Ybi"),
        ("Acuba", "acuba", "Acuba"),
        ("Anama", "anama", "Anama"),
        ("As Terras dos Auçás", "terras-dos-aucas", "As Terras dos Auçás"),
        ("Lauré", "laure", "Lauré"),
        ("Tupãsununga", "tupasununga", "Tupãsununga"),
        ("Yu", "yu", "Yu"),
        ("Tibá", "tiba", "Tibá"),
        ("Sobá", "soba", "Sobá"),
    ]),
    ("Facções", "faccoes", [
        ("Facções", "outras-guildas", "Outras Guildas e Facções"),
    ]),
    ("Ordem dos Arcanos Imperiais", "faccoes/arcanos-imperiais", [
        ("A Ordem dos Arcanos Imperiais", "index", "A Ordem dos Arcanos Imperiais"),
        ("Cargos da Organização", "cargos", "Cargos da Organização"),
        ("Títulos Honorários", "titulos-honorarios", "Títulos Honorários"),
        ("Sam-Mael", "sam-mael", "Sam-Mael, o Quartel General"),
        ("Locais Notáveis", "locais-notaveis", "Locais Notáveis"),
        ("Personalidades Notáveis", "personalidades-notaveis", "Personalidades Notáveis"),
    ]),
    ("Os Cavaleiros", "faccoes/cavaleiros", [
        ("Os Cavaleiros", "index", "Os Cavaleiros"),
        ("Origens e Propósito", "origens-e-proposito", "Origens e Propósito"),
        ("2. Rito do Selo da Alma", "rito-do-selo-da-alma", "Rito do Selo da Alma"),
        ("Regimento da Vigília Escarlate", "vigilia-escarlate", "Regimento da Vigília Escarlate"),
        ("Regimento da Ossaria", "ossaria-silenciosa", "Regimento da Ossaria Silenciosa"),
        ("Regimento Cavaleiros do Fôlego Infernal", "folego-infernal", "Regimento do Fôlego Infernal"),
        ("Regimento Cavaleiros do Limiar Abissal", "limiar-abissal", "Regimento do Limiar Abissal"),
        ("Regimento Cavaleiros da Aurora", "aurora-fendida", "Regimento da Aurora Fendida"),
        ("Regimento dos Intendentes", "intendentes-de-ossavermelha", "Regimento dos Intendentes de Ossavermelha"),
        ("Treinamento dos Cavaleiros", "treinamento", "Treinamento dos Cavaleiros"),
    ]),
    ("Ameaças", "ameacas", [
        ("AMEAÇAS DE ARCANO", "index", "Ameaças de Arcano"),
        ("MISTY AS-LA", "misty-as-la", "Misty As-La"),
        ("ELIGOS O PRIMEIRO DUQUE DO INFERNO", "eligos", "Eligos, o Primeiro Duque do Inferno"),
        ("VLAD DRACUL O MAGO DAS TREVAS VAMPIRO", "vlad-dracul", "Vlad Dracul, o Mago das Trevas Vampiro"),
        ("PERIGOS REGIONAIS", "perigos-regionais", "Perigos Regionais"),
        ("A LEGIÃO GOBLINÓIDE", "legiao-goblinoide", "A Legião Goblinóide"),
        ("A HORDA DE ORCS", "horda-de-orcs", "A Horda de Orcs"),
        ("O LEVANTE TÁURICO", "levante-taurico", "O Levante Táurico"),
        ("A ALCATÉIA GNÓL", "alcateia-gnol", "A Alcatéia Gnól"),
        ("Fauna de Airy", "fauna-de-airy", "Fauna de Airy"),
    ]),
    ("Artefatos", "artefatos", [
        ("ARTEFATOS DE ARCANO", "index", "Artefatos de Arcano"),
        ("Aliados Conjurados", "aliados-conjurados", "Aliados Conjurados"),
        ("As Armaduras Lendárias", "armaduras-lendarias", "As Armaduras Lendárias"),
        ("Veículos", "veiculos", "Veículos"),
    ]),
    ("Magia", "magia", [
        (["LISTA DE MAGIAS", "Magias"], "index", "Lista de Magias"),
        (["Escola Física", "K / X — Impacto, ação direta e manipulação física", "EN / ON — Movimento e fluxo", "KUN — Explosões", "IR — Persistentes/Sustentados"], "escola-fisica", "Escola Física"),
        (["Escola Alquímica", "ETH — Transformação", "ESH — Conjuração e manifestação"], "escola-alquimica", "Escola Alquímica"),
        (["Escola Natural", "AYA — Vida, biologia e regeneração", "VOK — Invocações"], "escola-natural", "Escola Natural"),
        (["Escola Abstrata", "ECH — Ondas, informação e mente", "Vhaurechaya", "OR — Espaço e deslocamento", "EL — Ilusão e percepção", "THAR — Tempo"], "escola-abstrata", "Escola Abstrata"),
        ("Anti-Fonemas", "anti-fonemas", "Anti-Fonemas"),
        ("Novas Magias", "novas-magias", "Novas Magias"),
    ]),
]

# Seções que existem na fonte mas NÃO pertencem ao cenário (descartadas: não entram no site nem são gravadas)
DESCARTADAS = {"IDEIAS"}
# Divisórias da fonte sem texto próprio (só um título) — viram agrupamentos no menu
DIVISORIAS = {"GEOGRAFIA", "AS ILHAS", "CIDADES PERDIDAS", ""}


# ---------------------------------------------------------------------------
def chave(t):
    t = unicodedata.normalize("NFKD", t).casefold()
    return re.sub(r"[\W_]+", "", t)


def limpa_titulo(t):
    t = re.sub(r"\s*\{#[^}]*\}\s*$", "", t)
    t = t.replace("**", "").replace("*", "")
    t = re.sub(r"\\(.)", r"\1", t)
    return t.strip().rstrip(":").strip()


def limpa_corpo(txt):
    # \x0b (tab vertical, vindo do Google Docs): dentro de tabela = quebra de linha HTML
    linhas = []
    for l in txt.split("\n"):
        if "\x0b" in l:
            l = l.replace("\x0b", "<br>") if l.lstrip().startswith("|") else l.replace("\x0b", "  \n")
        linhas.append(l.rstrip())
    return "\n".join(linhas)


def prompts_de_arte(txt):
    """Tabelas de 1 célula com prompt de geração de imagem -> bloco recolhível (conteúdo preservado)."""
    out, i, L = [], 0, txt.split("\n")
    while i < len(L):
        l = L[i]
        if (l.startswith("|") and i + 1 < len(L) and re.fullmatch(r"\|\s*:?-+:?\s*\|", L[i + 1].strip())
                and ("magic the gathering" in l.lower() or "full body pose" in l.lower())):
            celula = l.strip().strip("|").strip().replace("<br>", " ")
            out += ['??? note "Prompt de arte"', "    " + celula, ""]
            i += 2
            continue
        out.append(l)
        i += 1
    return "\n".join(out)


def parse_secoes(content):
    L = content.replace("\r\n", "\n").split("\n")
    heads = []
    for i, l in enumerate(L):
        m = re.match(r"^(#{1,6}) (.*)$", l)
        if m:
            heads.append((i, len(m.group(1)), limpa_titulo(m.group(2))))
    ini = next(k for k, h in enumerate(heads) if h[2] == "ARCANO")  # pula o sumário do Google Docs
    heads = heads[ini:]
    secs = []
    for k, (i, nivel, titulo) in enumerate(heads):
        fim = heads[k + 1][0] if k + 1 < len(heads) else len(L)
        corpo = "\n".join(L[i + 1:fim]).strip("\n")
        secs.append({"titulo": titulo, "nivel": nivel, "corpo": limpa_corpo(corpo), "usada": False})
    return secs


def acha(secs, alvo):
    k = chave(alvo)
    exatas = [s for s in secs if chave(s["titulo"]) == k]
    cand = exatas or [s for s in secs if chave(s["titulo"]).startswith(k)]
    cand = [s for s in cand if not s["usada"]] or cand
    if len(cand) != 1:
        sys.exit(f"ERRO: '{alvo}' casou com {len(cand)} seções: {[c['titulo'] for c in cand]}")
    return cand[0]


def monta_pagina(secs, fontes, titulo_menu):
    fontes = [fontes] if isinstance(fontes, str) else fontes
    partes = []
    for n, f in enumerate(fontes):
        s = acha(secs, f)
        s["usada"] = True
        corpo = prompts_de_arte(s["corpo"])
        if len(fontes) == 1:
            partes.append(f"# {titulo_menu}\n\n{corpo}".rstrip() + "\n")
        elif n == 0:
            partes.append(f"# {titulo_menu}\n\n{corpo}".rstrip() + "\n")
        else:
            # seções agrupadas: título original vira subtítulo
            if corpo.strip():
                partes.append(f"## {s['titulo']}\n\n{corpo}".rstrip() + "\n")
    return "\n".join(partes)


def insere_mapa(docs, paginas_por_alvo):
    """Troca o marcador da home pelo mapa clicável (links para as páginas do site)."""
    home = docs / "index.md"
    txt = home.read_text(encoding="utf-8")
    if MARCADOR_MAPA not in txt:
        return 0

    def href_de(alvo):
        rel = paginas_por_alvo.get(chave(alvo))
        if rel is None or not (docs / rel).exists():
            sys.exit(f"ERRO (mapa interativo): '{alvo}' não corresponde a nenhuma página da wiki")
        # use_directory_urls: reinos/elfin.md -> reinos/elfin/ ; imperio/index.md -> imperio/
        return rel[:-len("index.md")] if rel.endswith("/index.md") else rel[:-3] + "/"

    legenda = "*Clique no nome de um reino ou região para abrir a página.*"
    bloco = mapa_interativo.html_mapa(href_de, "imagens/") + "\n\n" + legenda
    home.write_text(txt.replace(MARCADOR_MAPA, bloco), encoding="utf-8", newline="\n")
    return len(mapa_interativo.carrega()["regioes"])


def ajusta_imagens(docs):
    """Copia fonte/imagens/ para docs/imagens/ e acerta o caminho das imagens em cada página.

    No ARCANO.md a imagem é escrita como  ![texto](imagens/arquivo.png)  (caminho relativo ao próprio
    ARCANO.md, que é como o preview do VS Code a encontra). Cada página do site fica numa profundidade
    diferente de docs/, então o prefixo "../" é calculado página a página, no resultado final.
    """
    if IMAGENS.exists():
        shutil.copytree(IMAGENS, docs / "imagens")
    padrao = re.compile(r'(\]\(|src=")imagens/')
    faltando = set()
    for arq in docs.rglob("*.md"):
        rel = os.path.relpath(docs / "imagens", arq.parent).replace("\\", "/")
        txt = arq.read_text(encoding="utf-8")
        novo = padrao.sub(lambda m: f"{m.group(1)}{rel}/", txt)
        if novo != txt:
            arq.write_text(novo, encoding="utf-8", newline="\n")
        for nome in re.findall(r'(?:\]\(|src=")[./]*imagens/([^)"\s]+)', novo):
            if not (docs / "imagens" / nome).exists():
                faltando.add(nome)
    if faltando:
        print(f"AVISO: imagens citadas no ARCANO.md que não existem em fonte/imagens/: {sorted(faltando)}")
    return len(list((docs / "imagens").rglob("*"))) if (docs / "imagens").exists() else 0


def main():
    if not FONTE.exists():
        sys.exit(f"Fonte não encontrada: {FONTE}")
    secs = parse_secoes(FONTE.read_text(encoding="utf-8-sig"))

    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)

    # ---- páginas -----------------------------------------------------------
    paginas = []  # (pasta, arquivo, titulo_menu)
    for nome_grupo, pasta, itens in ESTRUTURA:
        for fonte, arq, titulo in itens:
            md = monta_pagina(secs, fonte, titulo)
            dest = DOCS / pasta / f"{arq}.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(md, encoding="utf-8", newline="\n")
            paginas.append((pasta, arq, titulo))

    # ---- fora do cenário: descartado ------------------------------------------
    for s in secs:
        if s["titulo"] in DESCARTADAS:
            s["usada"] = True

    # ---- introdução / home --------------------------------------------------
    arcano = acha(secs, "ARCANO"); arcano["usada"] = True
    intro = acha(secs, "Introdução"); intro["usada"] = True
    (DOCS / "introducao.md").write_text(f"# Introdução\n\n{intro['corpo']}\n", encoding="utf-8", newline="\n")

    # ---- confere que nada com texto ficou de fora ---------------------------
    sobras = [s["titulo"] for s in secs if not s["usada"] and s["titulo"] not in DIVISORIAS and s["corpo"].strip()]
    if sobras:
        sys.exit(f"ERRO: seções com texto sem destino: {sobras}")

    # ---- índices de pasta: lista de páginas filhas --------------------------
    por_pasta = {}
    for pasta, arq, titulo in paginas:
        por_pasta.setdefault(pasta, []).append((arq, titulo))
    for pasta, itens in por_pasta.items():
        filhos = [(a, t) for a, t in itens if a != "index"]
        idx = DOCS / pasta / "index.md"
        if not idx.exists():
            titulo_pasta = next(n for n, p, _ in ESTRUTURA if p == pasta)
            idx.write_text(f"# {titulo_pasta}\n", encoding="utf-8", newline="\n")
        # subpastas diretas (ex.: imperio/reinos-vassalos dentro de imperio)
        subs = sorted({p for p in por_pasta if p.startswith(pasta + "/") and p.count("/") == pasta.count("/") + 1})
        lista = [f"- [{t}]({a}.md)" for a, t in filhos]
        for sp in subs:
            nome = next(n for n, p, _ in ESTRUTURA if p == sp)
            lista.append(f"- [{nome}]({sp.split('/')[-1]}/index.md)")
        if lista:
            with idx.open("a", encoding="utf-8", newline="\n") as f:
                f.write("\n---\n\n**Nesta seção**\n\n" + "\n".join(lista) + "\n")

    # ---- personagens e guildas saem de dentro dos reinos -----------------------
    ordem = [f"{pasta}/{arq}.md" for pasta, arq, _ in paginas]
    info = pos_processamento.executa(DOCS, ordem)
    pos_processamento.escreve_indices(DOCS, info)
    fidx0 = DOCS / "faccoes" / "index.md"
    if fidx0.exists() and "guildas/index.md" not in fidx0.read_text(encoding="utf-8"):
        with fidx0.open("a", encoding="utf-8", newline="\n") as f:
            f.write("- [Guildas e Facções dos Reinos](guildas/index.md)\n")
    nav_pers, nav_guil = pos_processamento.nav_extra(info)

    # ---- home ---------------------------------------------------------------
    topo = [("Lore e Cosmologia", "lore"), ("O Mundo", "mundo"), ("História", "historia"), ("Povos", "povos"),
            ("O Império", "imperio"), ("Reinos e Cidades fora do Império", "reinos"), ("Facções", "faccoes"),
            ("Personagens", "personagens"), ("Ameaças", "ameacas"), ("Artefatos", "artefatos"), ("Magia", "magia")]
    home = ["# Wiki Arcano & Airy\n", arcano["corpo"], "\n" + MARCADOR_MAPA + "\n", "\n---\n", "[Introdução](introducao.md)\n"]
    for nome, pasta in topo:
        destino = f"{pasta}/index.md" if (DOCS / pasta / "index.md").exists() else f"{pasta}/"
        home.append(f"- [{nome}]({destino})")
    (DOCS / "index.md").write_text("\n".join(home) + "\n", encoding="utf-8", newline="\n")

    # ---- facções: pasta tem 'outras-guildas' + subpastas --------------------
    fidx = DOCS / "faccoes" / "index.md"
    if fidx.exists():
        txt = fidx.read_text(encoding="utf-8")
        extra = ("\n- [A Ordem dos Arcanos Imperiais](arcanos-imperiais/index.md)\n- [Os Cavaleiros](cavaleiros/index.md)"
                 "\n- [Guildas e Facções dos Reinos](guildas/index.md)\n")
        if "arcanos-imperiais" not in txt:
            fidx.write_text(txt.rstrip() + extra, encoding="utf-8", newline="\n")

    # ---- mkdocs.yml ---------------------------------------------------------
    def nav_pasta(pasta):
        itens = []
        if (DOCS / pasta / "index.md").exists():
            itens.append(f"{pasta}/index.md")
        for a, t in por_pasta.get(pasta, []):
            if a != "index":
                itens.append({t: f"{pasta}/{a}.md"})
        for sp in sorted(p for p in por_pasta if p.startswith(pasta + "/") and p.count("/") == pasta.count("/") + 1):
            nome = next(n for n, p, _ in ESTRUTURA if p == sp)
            itens.append({nome: nav_pasta(sp)})
        return itens

    nav = [{"Início": "index.md"}, {"Introdução": "introducao.md"}]
    for nome, pasta in topo:
        if pasta == "personagens":
            nav.append({nome: nav_pers})
        elif pasta == "faccoes":
            nav.append({nome: nav_pasta(pasta) + [{"Guildas e Facções dos Reinos": nav_guil}]})
        else:
            nav.append({nome: nav_pasta(pasta)})

    def yaml_nav(items, nivel=1):
        out = []
        pad = "  " * nivel
        for it in items:
            if isinstance(it, str):
                out.append(f"{pad}- {it}")
            else:
                (k, v), = it.items()
                k = k.replace("\\", "\\\\").replace('"', '\\"')
                if isinstance(v, str):
                    out.append(f'{pad}- "{k}": {v}')
                else:
                    out.append(f'{pad}- "{k}":')
                    out += yaml_nav(v, nivel + 1)
        return out

    cfg = """site_name: Wiki Arcano & Airy
site_description: Cenário de RPG, HQs e romances — Arcano & Airy, por Rodrigo Mataro
site_url: https://M4T4R0.github.io/wiki-arcano/
docs_dir: docs
theme:
  name: material
  language: pt-BR
  palette:
    - scheme: default
      primary: indigo
      toggle: {icon: material/weather-night, name: Modo escuro}
    - scheme: slate
      primary: indigo
      toggle: {icon: material/weather-sunny, name: Modo claro}
  features:
    - navigation.tabs
    - navigation.indexes
    - navigation.top
    - navigation.path
    - search.highlight
    - search.suggest
    - toc.follow
    - content.code.copy
plugins:
  - search
markdown_extensions:
  - admonition
  - pymdownx.details
  - tables
  - toc:
      permalink: true
nav:
"""
    (RAIZ / "mkdocs.yml").write_text(cfg + "\n".join(yaml_nav(nav)) + "\n", encoding="utf-8", newline="\n")

    # ---- links cruzados (seguros: só envolvem texto existente em link) ----------
    crosslink_seguro.executa(DOCS)

    # ---- mapa clicável na home (depois dos links cruzados, para não mexerem no HTML) -----
    por_alvo = {}
    for _n, pasta, itens in ESTRUTURA:
        for fonte, arq, _t in itens:
            primeiro = fonte if isinstance(fonte, str) else fonte[0]
            por_alvo[chave(primeiro)] = f"{pasta}/{arq}.md"
    n_mapa = insere_mapa(DOCS, por_alvo)

    # ---- imagens (por último, para o caminho refletir o lugar final de cada página) ---
    n_img = ajusta_imagens(DOCS)

    n = sum(1 for _ in DOCS.rglob("*.md"))
    print(f"OK: {n} páginas geradas em docs/ a partir de {len(secs)} seções da fonte ({n_img} imagens copiadas, {n_mapa} áreas clicáveis no mapa).")


if __name__ == "__main__":
    main()
