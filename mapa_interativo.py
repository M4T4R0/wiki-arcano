#!/usr/bin/env python3
"""
mapa_interativo.py — mapa de Airy com os nomes clicáveis.

Dados: fonte/mapa-interativo.json  (nome, 'alvo' = título da seção no ARCANO.md e 'caixa' em pixels).
Usado por:
  * build_wiki.py   -> coloca o mapa na página inicial do site (links para as páginas)
  * gera_indice.py  -> coloca o mapa no topo do ARCANO.md (links para as seções do próprio arquivo)

O mapa é um <div> com a imagem e uma área <a> sobre cada nome, posicionada em porcentagem:
por isso acompanha o tamanho da tela (celular, tablet, desktop).
"""
import json
from html import escape
from pathlib import Path

ARQ = Path(__file__).parent / "fonte" / "mapa-interativo.json"


def carrega():
    return json.loads(ARQ.read_text(encoding="utf-8"))


def html_mapa(href_de, prefixo_imagem="imagens/", alt="Mapa de Airy"):
    """href_de(alvo) -> link da área clicável. Sem linhas em branco (senão o Markdown quebra o bloco)."""
    d = carrega()
    W, H = d["largura"], d["altura"]
    L = [
        "<style>.mapa-airy a:hover,.mapa-airy a:focus-visible{background:rgba(255,193,7,.38);"
        "outline:2px solid #e69500}</style>",
        '<div class="mapa-airy" style="position:relative;max-width:984px;margin:1rem auto">',
        f'<img src="{prefixo_imagem}{d["imagem"]}" alt="{escape(alt)}" style="display:block;width:100%;height:auto">',
    ]
    for r in d["regioes"]:
        x1, y1, x2, y2 = r["caixa"]
        L.append(
            f'<a href="{escape(href_de(r["alvo"]))}" title="{escape(r["nome"])}" aria-label="{escape(r["nome"])}" '
            f'style="position:absolute;display:block;border-radius:4px;'
            f'left:{x1 / W * 100:.2f}%;top:{y1 / H * 100:.2f}%;'
            f'width:{(x2 - x1) / W * 100:.2f}%;height:{(y2 - y1) / H * 100:.2f}%"></a>'
        )
    L.append("</div>")
    return "\n".join(L)
