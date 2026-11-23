#!/usr/bin/env python3
"""
mapa_ajuda.py — ajuda a manter as áreas clicáveis do mapa quando a imagem muda.

    python mapa_ajuda.py conferir   # compara fonte/mapa-interativo.json com a imagem atual
    python mapa_ajuda.py numerar    # numera todos os nomes que existem no mapa e mostra as coordenadas

Precisa de:  pip install pillow numpy opencv-python-headless
Funciona porque os nomes do mapa são preto puro com contorno branco: o script acha esses textos sozinho.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

RAIZ = Path(__file__).parent
JSON = RAIZ / "fonte" / "mapa-interativo.json"


def detecta(img_path):
    """Retorna as caixas [x1,y1,x2,y2] de cada linha de texto do mapa."""
    im = np.array(Image.open(img_path).convert("L"))
    txt = (im <= 8).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(txt, connectivity=8)
    limpo = np.zeros_like(txt)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 6:
            limpo[lab == i] = 1
    d = cv2.dilate(limpo, cv2.getStructuringElement(cv2.MORPH_RECT, (11, 5)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(d, connectivity=8)
    caixas = [[int(x), int(y), int(x + w), int(y + h)] for i in range(1, n) for x, y, w, h, _a in [st[i]]
              if w >= 14 and h >= 8]
    return sorted(caixas, key=lambda b: (b[1] // 30, b[0]))


def centro(b):
    return (b[0] + b[2]) / 2, (b[1] + b[3]) / 2


def dentro(ponto, caixa):
    return caixa[0] <= ponto[0] <= caixa[2] and caixa[1] <= ponto[1] <= caixa[3]


def desenha(img_path, caixas, rotulos, saida, cor):
    im = cv2.imread(str(img_path))
    for b, r in zip(caixas, rotulos):
        cv2.rectangle(im, (b[0], b[1]), (b[2], b[3]), cor, 2)
        cv2.putText(im, str(r), (b[0], max(12, b[1] - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 1)
    cv2.imwrite(str(saida), im)


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "conferir"
    dados = json.loads(JSON.read_text(encoding="utf-8"))
    img = RAIZ / "fonte" / "imagens" / dados["imagem"]
    if Image.open(img).size != (dados["largura"], dados["altura"]):
        sys.exit(f"A imagem tem tamanho diferente de {dados['largura']}x{dados['altura']}: "
                 "atualize 'largura' e 'altura' no JSON e confira tudo de novo.")
    achadas = detecta(img)

    if modo == "numerar":
        desenha(img, achadas, range(len(achadas)), RAIZ / "mapa-numerado.png", (0, 0, 255))
        for i, b in enumerate(achadas):
            print(f"{i:3d}  {b}")
        print("\nImagem gerada: mapa-numerado.png  (cada linha de texto do mapa, com número e coordenadas)")
        return

    regioes = dados["regioes"]
    sem_texto = [r for r in regioes if not any(dentro(centro(b), r["caixa"]) for b in achadas)]
    sem_area = [b for b in achadas if not any(dentro(centro(b), r["caixa"]) for r in regioes)]
    desenha(img, [r["caixa"] for r in regioes], [r["nome"] for r in regioes], RAIZ / "mapa-conferencia.png", (0, 160, 0))
    for b in sem_area:
        cv2_img = cv2.imread(str(RAIZ / "mapa-conferencia.png"))
        cv2.rectangle(cv2_img, (b[0], b[1]), (b[2], b[3]), (0, 0, 255), 2)
        cv2.imwrite(str(RAIZ / "mapa-conferencia.png"), cv2_img)

    print(f"{len(regioes)} áreas clicáveis no JSON; {len(achadas)} linhas de texto no mapa.\n")
    if sem_texto:
        print("ATENÇÃO — áreas que não cobrem mais nenhum texto (o nome mudou de lugar ou saiu do mapa):")
        for r in sem_texto:
            print(f"   {r['nome']}: {r['caixa']}")
    else:
        print("Todas as áreas do JSON ainda cobrem um nome do mapa.")
    if sem_area:
        print("\nTextos do mapa SEM área clicável (se quiser link, adicione no JSON; se não, tudo bem):")
        for b in sem_area:
            print(f"   {b}")
    print("\nImagem gerada: mapa-conferencia.png  (verde = áreas do JSON, vermelho = texto sem área)")


if __name__ == "__main__":
    main()
