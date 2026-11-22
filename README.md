# Wiki Arcano & Airy

Cenário de RPG (3D&T Alpha), HQs e romances — mantido por Rodrigo Mataro.
Site: https://M4T4R0.github.io/wiki-arcano/

## Como funciona

```
fonte/ARCANO_Só_Cenário.json   ← documento de origem (única fonte de verdade)
build_wiki.py                  ← gera docs/ e mkdocs.yml a partir da fonte
pos_processamento.py           ← (chamado pelo build) tira personagens e guildas de dentro dos reinos
crosslink_seguro.py            ← (chamado pelo build) links cruzados que não alteram o texto
docs/                          ← páginas do site (GERADAS — não edite à mão)
_arquivo/                      ← material fora do site (só os scripts antigos)
```

Para atualizar a wiki:

1. Edite o texto em `fonte/ARCANO_Só_Cenário.json` (campo `content`) — ou troque o arquivo por uma versão nova.
2. `python build_wiki.py`
3. `mkdocs serve` para conferir, depois `git push` (o GitHub Actions publica).

**Atenção:** `build_wiki.py` apaga e recria `docs/` a cada execução. Edição manual em `docs/` se perde.
Se preferir editar as páginas direto, pare de rodar o script e trate `docs/` como a fonte.

Para mudar pastas, nomes ou ordem do menu, edite só a lista `ESTRUTURA` no início do `build_wiki.py`.

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
