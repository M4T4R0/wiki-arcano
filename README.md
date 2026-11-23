# Wiki Arcano & Airy

Cenário de RPG (3D&T Alpha), HQs e romances — mantido por Rodrigo Mataro.
Site: https://M4T4R0.github.io/wiki-arcano/

## Como funciona

```
fonte/ARCANO.md                ← documento de origem (única fonte de verdade)
gera_indice.py                 ← refaz o índice (com links) no topo do ARCANO.md
mapa_ajuda.py                  ← confere/numera os nomes do mapa clicável
fonte/imagens/                 ← imagens do ARCANO.md (o build copia para docs/imagens/)
build_wiki.py                  ← gera docs/ e mkdocs.yml a partir da fonte
pos_processamento.py           ← (chamado pelo build) tira personagens e guildas de dentro dos reinos
crosslink_seguro.py            ← (chamado pelo build) links cruzados que não alteram o texto
docs/                          ← páginas do site (GERADAS — não edite à mão)
_arquivo/                      ← material fora do site (só os scripts antigos)
```

Para atualizar a wiki:

1. Edite o texto em `fonte/ARCANO.md` — ou troque o arquivo por uma versão nova (exportada do Google Docs, por exemplo).
2. `python gera_indice.py` (refaz o índice do topo do ARCANO.md e deixa os links funcionando)
3. `python build_wiki.py`
4. `mkdocs serve` para conferir, depois `git push` (o GitHub Actions publica).

**Atenção:** `build_wiki.py` apaga e recria `docs/` a cada execução. Edição manual em `docs/` se perde.
Se preferir editar as páginas direto, pare de rodar o script e trate `docs/` como a fonte.

Para mudar pastas, nomes ou ordem do menu, edite só a lista `ESTRUTURA` no início do `build_wiki.py`.

## Imagens

1. Coloque o arquivo em `fonte/imagens/` (nomes sem espaço e sem acento).
2. No `ARCANO.md`, escreva `![descrição](imagens/arquivo.png)` onde ela deve aparecer (o preview do VS Code já mostra).
3. `python build_wiki.py` copia a pasta para `docs/imagens/` e acerta o caminho em cada página. Nunca coloque imagens direto em `docs/`: o build apaga a pasta.

## Mapa clicável

O mapa da página inicial (e do topo do `ARCANO.md`) usa `fonte/imagens/Mapa_de_Airy_2025.png` e as áreas de
`fonte/mapa-interativo.json`. Cada área tem `nome`, `alvo` (título da seção no ARCANO.md) e `caixa`
`[x1, y1, x2, y2]` em pixels da imagem.

**Quando o mapa mudar (nome trocado de lugar, nome novo, imagem nova):**
1. Substitua o arquivo em `fonte/imagens/` (mesmo nome, mesmo tamanho).
2. `python mapa_ajuda.py conferir` — diz quais áreas não cobrem mais nenhum nome e quais nomes do mapa estão sem
   área. Gera `mapa-conferencia.png` (verde = área do JSON, vermelho = nome sem área).
3. `python mapa_ajuda.py numerar` — gera `mapa-numerado.png` com todos os nomes numerados e imprime as coordenadas
   de cada um. Copie as coordenadas para o JSON (some 3 pixels de folga em cada lado).
4. Repita o passo 2 até não aparecer mais ATENÇÃO, depois `python gera_indice.py` e `python build_wiki.py`.

Dois nomes na mesma linha do mapa (ex.: "Deserto" / "Açu") viram uma área só: use o menor x1/y1 e o maior x2/y2.
O mesmo `alvo` pode aparecer em várias áreas (ex.: as duas pontas da muralha de Ybi).
Precisa de `pip install pillow numpy opencv-python-headless` (só para o `mapa_ajuda.py`).

## Seções

Lore e Cosmologia · O Mundo · História · Povos · O Império (reinos vassalos e estados tampões) ·
Reinos e Cidades fora do Império · Facções (Arcanos Imperiais, Cavaleiros, Guildas e Facções dos Reinos) ·
**Personagens** · Ameaças · Artefatos · Magia

## Personagens e guildas em páginas próprias

`pos_processamento.py` move o texto (sem reescrever) para:

- `docs/personagens/<origem>/<personagem>.md` — um arquivo por personagem, listados na aba **Personagens**;
- `docs/faccoes/guildas/<origem>/<guilda>.md` — uma página por guilda/facção com texto próprio.

No lugar original ficam só o nome e o link. O que mover é definido na tabela `OPERACOES` do início do
`pos_processamento.py` (por título de seção, não por número de linha). Para tirar mais um personagem ou guilda
de uma página, acrescente uma linha lá e rode o build. O próprio script confere que nenhuma linha do texto se perdeu.

Guildas de uma linha só (listas como "Nome: descrição" em Ybytu, Tamaya, Tibá, Sobá etc.) continuam na página
de origem: não têm texto suficiente para uma página.

## Links cruzados

`crosslink_seguro.py` só envolve em link a primeira ocorrência de nomes que têm página (reinos, personagens,
guildas, vilões). Não insere, troca nem apaga palavras, e verifica isso antes de gravar. Para só ver o que faria:
`python crosslink_seguro.py --dry-run`. Nomes genéricos ou ambíguos ficam de fora (lista `STOP` no script).

## Conteúdo descartado

A seção `IDEIAS` da fonte (descrições de cargo, fora do cenário) e o conteúdo não canônico gerado por scripts
(Guilda ERA, Relíquias, Armas Lendárias, Tecnologias Proibidas, Meio-Anão, regras 3D&T, fichas resumidas)
foram removidos do projeto.
