# Regras Estritas do Repositório (MkDocs Material)
1. Todos os arquivos Markdown (.md) e imagens DEVEM ficar exclusivamente dentro da pasta `docs/`. Nunca crie pastas de conteúdo na raiz.
2. No arquivo `mkdocs.yml` (seção `nav`), os caminhos são sempre relativos à pasta `docs/`. Nunca comece um caminho com `docs/`.
3. Use sempre barras normais (`/`) em todos os links e caminhos, nunca barras invertidas (`\`).
4. Nunca duplique arquivos ou pastas do repositório dentro de subpastas.
5. Antes de alterar o `mkdocs.yml`, verifique o nome exato dos arquivos existentes na pasta `docs/`.

## 🚫 PROIBIÇÃO ESTRITA DE CRIAÇÃO DE REGRAS E CONTEÚDO (CANON ONLY)
1. **NUNCA crie, invente ou adapte regras de RPG** (custos em pontos, vantagens, desvantagens, perícias, magias, estatísticas de combate, bônus numéricos, equipamentos iniciais ou fichas de 3D&T Alpha / Victory / GETA / D&D).
2. **NUNCA escreva seções como "Uso em Jogo", "Mecânicas", "Ficha" ou "Equipamento Inicial"**, a menos que o usuário forneça o texto exato da regra no prompt.
3. **Trabalhe exclusivamente com o texto-fonte fornecido** pelo usuário ou já existente nos arquivos do repositório (especialmente `fonte/ARCANO_Só_Cenário.json`).
4. **Se faltar informação** sobre lore, história ou mecânica para preencher uma página, **deixe a seção em branco ou insira apenas `[A DEFINIR]`** e pergunte ao usuário. Nunca preencha lacunas inventando conteúdo por conta própria.
5. **Seu papel é apenas estruturar, organizar, formatar em Markdown e criar links** entre os textos existentes do autor (Rodrigo Mataro).
6. Antes de editar o `mkdocs.yml`, leia o arquivo atual do disco; nunca sobrescreva o `mkdocs.yml` inteiro usando versões em cache/memória.
7. Nunca execute `python build_wiki.py` sem autorização explícita do usuário, pois o script apaga e recria toda a pasta `docs/`.
