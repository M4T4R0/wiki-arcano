#!/usr/bin/env python3
"""
crosslink_seguro.py — links cruzados que NÃO mexem no conteúdo.

O que faz
---------
Procura, no texto corrido das páginas de docs/, nomes de reinos, cidades, personagens, guildas,
vilões e povos que têm página própria, e envolve a PRIMEIRA ocorrência de cada um (por página) em
um link:   Ypy   ->   [Ypy](../reinos/ypy.md)

O que garante (diferente do auto_crosslink.py antigo)
-----------------------------------------------------
  * Só acrescenta "[" e "](caminho)" em volta de um texto que já existia. Nenhuma palavra é
    inserida, trocada ou apagada.
  * Só linka para arquivos que EXISTEM em docs/ (o alvo é lido do disco, nunca inventado).
  * Maiúsculas/minúsculas exatas e palavra inteira ("Ypy" não casa dentro de "Ypyano").
  * Nome ambíguo (serve para mais de uma página) não é linkado.
  * Nunca mexe em: títulos (#), linhas só em negrito (rótulos), tabelas, blocos recolhíveis
    (prompts de arte), código, links que já existem, URLs.
  * Não linka uma página para ela mesma, nem para um alvo que a página já linka.
  * VERIFICA no fim: se tirar os links inseridos, o arquivo tem de ficar idêntico ao original;
    senão aborta sem gravar nada.

Uso
---
    python crosslink_seguro.py              # aplica em docs/
    python crosslink_seguro.py --dry-run    # só mostra o que faria
É idempotente: rodar duas vezes não duplica links.
"""
import os
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).parent
DOCS = RAIZ / "docs"

LINK = re.compile(r"!?\[[^\]\n]*\]\([^)\n]*\)")
PROTEGIDO = re.compile(r"!?\[[^\]\n]*\]\([^)\n]*\)|`[^`\n]*`|<[^>\n]+>|https?://\S+")
NEGRITO_SO = re.compile(r"^\s*\*\*[^*].*\*\*:?\s*$")
ARTIGO = re.compile(r"^(?:A|O|As|Os)\s+")

# Palavras genéricas demais para virar link (mesmo sendo nome de página)
STOP = {"Imperador", "Capitão", "Charles", "Joane", "Murilo", "Fortuna", "Cavaleiros", "Magia", "Mundo", "O Mundo", "Rocca"}

# Pastas cujos H1 viram alvos
PASTAS_LUGARES = ["reinos", "imperio/reinos-vassalos", "imperio/estados-tampoes"]
PASTAS_MUNDO = ["mundo"]
POVOS_ARTIGO_OK = True  # povos só pelo título completo com 2+ palavras


def h1(arq: Path):
    for l in arq.read_text(encoding="utf-8").split("\n"):
        if l.startswith("# "):
            return l[2:].strip()
    return None


def sem_artigo(t):
    return ARTIGO.sub("", t)


def palavras(t):
    return len(t.split())


def coleta_alvos(docs: Path):
    """alias -> set(caminhos relativos a docs/)"""
    alvos = {}

    def add(alias, caminho, personagem=False):
        alias = alias.strip()
        if not alias or alias in STOP:
            return
        if palavras(alias) == 1 and len(alias) < (5 if personagem else 3):
            return
        if palavras(alias) > 1 and len(alias) < 6:
            return
        alvos.setdefault(alias, {})[caminho] = personagem

    def rel_docs(p):
        return p.relative_to(docs).as_posix()

    # lugares
    for pasta in PASTAS_LUGARES + PASTAS_MUNDO:
        for f in sorted((docs / pasta).glob("*.md")):
            if f.name == "index.md":
                continue
            t = h1(f)
            if not t:
                continue
            add(t, rel_docs(f))
            s = sem_artigo(t)
            if s != t and (palavras(s) >= 2 or pasta in PASTAS_LUGARES):
                add(s, rel_docs(f))
    # povos: só título completo com 2+ palavras
    for f in sorted((docs / "povos").glob("*.md")):
        if f.name == "index.md":
            continue
        t = h1(f)
        if t and palavras(t) >= 2:
            add(t, rel_docs(f))
    # vilões (Ameaças com nome próprio)
    for nome, arq in [("Misty As-La", "ameacas/misty-as-la.md"), ("Eligos", "ameacas/eligos.md"),
                      ("Vlad Dracul", "ameacas/vlad-dracul.md")]:
        if (docs / arq).exists():
            add(nome, arq)
    # ordens principais
    for nome, arq in [("Ordem dos Arcanos Imperiais", "faccoes/arcanos-imperiais/index.md"),
                      ("Arcanos Imperiais", "faccoes/arcanos-imperiais/index.md")]:
        if (docs / arq).exists():
            add(nome, arq)
    # guildas extraídas
    for f in sorted((docs / "faccoes" / "guildas").glob("*/*.md")):
        t = h1(f)
        if not t:
            continue
        add(t, rel_docs(f))
        s = sem_artigo(t)
        if s != t and palavras(s) >= 2:
            add(s, rel_docs(f))
    # personagens extraídos
    for f in sorted((docs / "personagens").glob("*/*.md")):
        t = h1(f)
        if not t:
            continue
        add(t, rel_docs(f), True)
        base = re.split(r"\s*[,(“\"]", t)[0].strip()
        add(base, rel_docs(f), True)
        sem_romano = re.sub(r"\s+[IVXL]+$", "", base)
        if sem_romano != base:
            add(sem_romano, rel_docs(f), True)
    # remove ambiguidades: alias que serve para mais de uma página
    final = {}
    for alias, d in alvos.items():
        if len(d) == 1:
            (c, pers), = d.items()
            final[alias] = (c, pers)
    return final


def monta_regex(alvos):
    aliases = sorted(alvos, key=lambda a: (-len(a), a))
    corpo = "|".join(re.escape(a) for a in aliases)
    return re.compile(r"(?<![\w\-])(" + corpo + r")(?![\w\-])")


def linhas_puladas(l, em_bloco):
    s = l.strip()
    if not s:
        return False
    if s.startswith("#") or s.startswith("|") or s.startswith("???") or l.startswith("    ") or l.startswith("\t"):
        return True
    if s.startswith("---") or s.startswith("```"):
        return True
    if s.startswith("![") or "<img" in s:
        return True
    if NEGRITO_SO.match(l):
        return True
    return False


def processa(texto, arq, alvos, regex):
    """Devolve (novo_texto, lista_de_links_inseridos)."""
    ja = set()
    # alvos já linkados nesta página (resolvidos a caminhos de docs/)
    base = os.path.dirname(arq)
    for m in re.finditer(r"\]\(([^)\s#]+\.md)(?:#[^)]*)?\)", texto):
        ja.add(os.path.normpath(os.path.join(base, m.group(1))).replace(os.sep, "/"))
    ja.add(arq)

    novas, inseridos = [], []
    em_codigo = False
    for l in texto.split("\n"):
        if l.strip().startswith("```"):
            em_codigo = not em_codigo
        if em_codigo or linhas_puladas(l, False):
            novas.append(l)
            continue
        protegidos = [m.span() for m in PROTEGIDO.finditer(l)]
        trocas = []
        for m in regex.finditer(l):
            a, b = m.span(1)
            alias = m.group(1)
            alvo, pers = alvos[alias]
            if alvo in ja:
                continue
            if any(pa < b and a < pb for pa, pb in protegidos):
                continue
            if pers and palavras(alias) == 1:
                # nome solto de personagem: não linka se vier colado a outro nome próprio
                ant = re.search(r"([A-ZÀ-Ý][\wà-ÿ’']*)\s$", l[:a])
                prox = re.match(r"\s([A-ZÀ-Ý][\wà-ÿ’']*)", l[b:])
                if ant or prox:
                    continue
            trocas.append((a, b, alias, alvo))
            ja.add(alvo)
        if trocas:
            partes, pos = [], 0
            for a, b, alias, alvo in trocas:
                url = os.path.relpath(alvo, start=base or ".").replace(os.sep, "/")
                partes.append(l[pos:a])
                partes.append(f"[{alias}]({url})")
                pos = b
                inseridos.append((alias, alvo))
            partes.append(l[pos:])
            l = "".join(partes)
        novas.append(l)
    return "\n".join(novas), inseridos


def verifica(orig, novo):
    """Tirando só os links inseridos, o texto tem de voltar ao original."""
    antigos = Counter(m.group(0) for m in LINK.finditer(orig))

    def volta(m):
        s = m.group(0)
        if antigos[s] > 0:
            antigos[s] -= 1
            return s
        return m.group(0)[1:m.group(0).index("](")]

    return LINK.sub(volta, novo) == orig


def executa(docs: Path = DOCS, dry_run=False, verboso=True):
    alvos = coleta_alvos(docs)
    regex = monta_regex(alvos)
    total, por_alvo, paginas = 0, Counter(), 0
    pendentes = []
    for f in sorted(docs.rglob("*.md")):
        arq = f.relative_to(docs).as_posix()
        orig = f.read_text(encoding="utf-8")
        novo, ins = processa(orig, arq, alvos, regex)
        if not ins:
            continue
        if not verifica(orig, novo):
            raise SystemExit(f"crosslink_seguro: verificação falhou em {arq}; nada foi gravado.")
        pendentes.append((f, novo, ins))
    for f, novo, ins in pendentes:
        paginas += 1
        total += len(ins)
        por_alvo.update(a for a, _ in ins)
        if not dry_run:
            f.write_text(novo, encoding="utf-8", newline="\n")
    if verboso:
        modo = "SIMULAÇÃO — nada gravado" if dry_run else "gravado"
        print(f"crosslink_seguro: {total} links em {paginas} páginas ({modo}); {len(alvos)} nomes monitorados.")
        top = ", ".join(f"{a} ({n})" for a, n in por_alvo.most_common(8))
        if top:
            print("  mais linkados:", top)
    return total


if __name__ == "__main__":
    executa(DOCS, dry_run="--dry-run" in sys.argv)
