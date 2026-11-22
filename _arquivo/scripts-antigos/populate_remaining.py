#!/usr/bin/env python3
"""
Populate remaining kingdom wiki pages from ARCANO_COMPLETO.md geography section.
These kingdoms are mentioned but don't have dedicated sections.
"""

import re
from pathlib import Path

ARCANO_PATH = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/ARCANO_COMPLETO.md")
WIKI_REINOS_DIR = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/factions/reinos")

# Kingdoms mentioned in geography section but without dedicated sections
REMAINING_KINGDOMS = {
    "lande.md": {
        "nome": "Landé",
        "regiao": "Deserto Leste",
        "tipo": "Reino Portuário",
        "descricao": "Reino portuário no deserto leste, porta de entrada marítima para as terras áridas. Conhecido pelo comércio marítimo e como ponto de passagem para o interior do deserto.",
        "cultura": "Comerciante e adaptada ao deserto. A vida gira em torno do porto, das rotas de caravanas e do comércio de especiarias, tecidos e água.",
        "recursos": "Abundância: Comércio marítimo, sal, peixes, rotas de caravanas. Escassez: Água doce, terras aráveis.",
        "vantagem": "Comércio Marítimo (+1 Negociação; conhece rotas e taxas portuárias)",
        "npcs": ["Governador Portuário", "Mestre de Caravanas"],
        "pontos": ["Porto Principal", "Mercado das Caravanas", "Farol do Deserto"],
    },
    "yby.md": {
        "nome": "Yby",
        "regiao": "Deserto Leste",
        "tipo": "Reino dos Magos (Fogo/Terra)",
        "descricao": "Reino especializado em magia elemental de Fogo e Terra, situado no deserto leste. Seus magos controlam o clima árido e extraem recursos do solo.",
        "cultura": "Erudita e elemental. A sociedade é organizada em torno de torres de magia onde se estuda e pratica piromancia e terramancia.",
        "recursos": "Abundância: Minérios, cristais de mana, conhecimento elemental. Escassez: Água, alimentos (importados).",
        "vantagem": "Domínio Elemental (+1 em testes de Magia de Fogo/Terra; resistência a calor extremo)",
        "npcs": ["Arquimago do Fogo", "Mestre da Terra"],
        "pontos": ["Torre de Obsidiana", "Forja Elemental", "Biblioteca de Cinzas"],
    },
    "araxa.md": {
        "nome": "Araxá",
        "regiao": "Cordilheiras Atã",
        "tipo": "Reino dos Abaquar (Ilhas Voadoras)",
        "descricao": "Cidade mítica situada em ilhas voadoras ligadas por escadas de corda. Território neutro onde povos em guerra convivem pacificamente sob a vigilância de Arquimagos poderosos.",
        "cultura": "Neutra, elevada e mágica. A vida ocorre nas alturas, entre pontes de corda e ilhas flutuantes. Brigas entre etnias são punidas com exílio permanente.",
        "recursos": "Abundância: Magia avançada, Aço Diamante, pedras Atã, conhecimento arcano. Escassez: Metais comuns, terras baixas.",
        "vantagem": "Voo Natural (imune a quedas; +1 Acrobacia; acesso a rotas aéreas)",
        "npcs": ["Arquimago Guardião", "Mestre das Pontes"],
        "pontos": ["Ilha Central", "Escadas de Corda", "Conselho dos Arquimagos", "Barreiras Mágicas"],
    },
    "avista.md": {
        "nome": "Avista",
        "regiao": "Cordilheiras Atã",
        "tipo": "Cidade dos Piquira / Gnomos (Tecnologia)",
        "descricao": "Cidade flutuante envolta em poderosa ilusão que combina tecnologia e magia. A mais avançada tecnologicamente em Airy. Cultua o Deus Máquina.",
        "cultura": "Tecnocrática e secreta. Acesso apenas com guia gnomo e Aiship. Inovação constante, tecnomagia, construções inteligentes.",
        "recursos": "Abundância: Tecnologia avançada, tecnomagia, ilusões, engenharia. Escassez: Recursos naturais brutos, contato externo.",
        "vantagem": "Tecnologia Pura (+1 Engenharia/Tecnomagia; imune a ilusões simples; acesso a equipamentos ERA-1)",
        "npcs": ["Arquiteto Chefe", "Mestre da Ilusão", "Sacerdote do Deus Máquina"],
        "pontos": ["Forja Central", "Núcleo de Ilusão", "Hangar de Aiships", "Laboratório do Deus Máquina"],
    },
    "naurush.md": {
        "nome": "Naur'Ush",
        "regiao": "Pântanos Sudoeste (Terra Selvagem)",
        "tipo": "Auçá Livres (Subterrânea)",
        "descricao": "Cidade subterrânea dos Auçá Livres nos pântanos a sudoeste da Infestação. População Auçá que rompeu com o Império mas mantém o dever de conter a Infestação.",
        "cultura": "Militarista e independente. Vivem em túneis e cavernas, organizados em clãs guerreiros. Leais apenas a si mesmos e ao dever sagrado.",
        "recursos": "Abundância: Ferro de pântano, venenos, conhecimento de túneis. Escassez: Luz solar, comércio externo, aliados.",
        "vantagem": "Subterrâneo Nato (Infravisão; +1 Furtividade em túneis; imune a gases de pântano)",
        "npcs": ["General dos Livres", "Mestre dos Túneis", "Xamã do Pântano"],
        "pontos": ["O Poço (Capital)", "Túneis de Defesa", "Fábrica de Armas", "Altar da Liberdade"],
    },
    "terras-auca.md": {
        "nome": "Terras dos Auçá",
        "regiao": "Além da Infestação (Oeste)",
        "tipo": "Auçá Imperiais / Nação Militarista",
        "descricao": "Terras a oeste da Infestação, concedidas aos Auçá pelo tratado de paz do Ano 392. Nação de homens com exoesqueleto natural, extremamente militaristas, que continuam defendendo o mundo civilizado na Grande Muralha.",
        "cultura": "Totalmente militarizada. Sociedade organizada em castas de guerra. Dever sagrado: conter a Infestação. Crescimento populacional explosivo (maior espécie de Airy).",
        "recursos": "Abundância: Guerreiros, exoesqueleto natural, minérios, armas. Escassez: Diplomacia, magia arcana, liberdade civil.",
        "vantagem": "Exoesqueleto Natural (Armadura +2 natural; Regeneração 1 PV/rodada; imune a Infestação; Fraqueza: Obsidiana)",
        "npcs": ["Comandante Supremo", "Mestre da Muralha", "Rainha das Ninhadas"],
        "pontos": ["Grande Muralha", "O Poço", "Ninhadas Centrais", "Fábricas de Guerra", "Campos de Treinamento"],
    },
    "tiba.md": {
        "nome": "Tiba",
        "regiao": "Oeste/Além-mar (Ilha)",
        "tipo": "Ilha dos Gigantes (Cataclisma)",
        "descricao": "Ilha criada pelo Primeiro Cataclisma (ritual mágico que deu errado). Antigas cidades dos Gigantes arrancadas do continente. Habitada por gigantes primitivos e ruínas de civilização avançada.",
        "cultura": "Primitiva e monumental. Gigantes vivem entre ruínas de sua antiga glória. Poucos gigantes não-primitivos restam, escondidos.",
        "recursos": "Abundância: Ruínas gigantescas, artefatos antigos, magia primordial. Escassez: População, tecnologia atual, contato pacífico.",
        "vantagem": "Sangue de Gigante (Força +2; Tamanho Grande; intimidação natural; movimento custoso)",
        "npcs": ["Ancião das Ruínas", "Guardião do Cataclisma"],
        "pontos": ["Cidades Arrancadas", "Ritual Falho", "Monumentos dos Gigantes", "Portal Fechado"],
    },
    "acag.md": {
        "nome": "Acag",
        "regiao": "Noroeste (Arquipélago)",
        "tipo": "Arquipélago Yawara / Kemonos",
        "descricao": "Arquipélago a noroeste de Airy, lar dos Yawara (Kemonos) - humanóides com traços animais. Sociedade organizada, cidades bem estruturadas, isolada do continente principal. Liderados pelo Homem Leão.",
        "cultura": "Diversa e animalística. Variedade de sub-espécies (coelhos, raposas, felinos, etc.). Governo, cidades, ocupações similares aos humanos mas com traços animais marcantes.",
        "recursos": "Abundância: Diversidade biológica, sentidos aguçados, adaptabilidade. Escassez: Contato com Airy, tecnologia imperial, metais.",
        "vantagem": "Herança Animal (Escolha: +1 Ágil/Carismático/Forte/Gênio/Resoluto/Vigoroso; Percepção Apurada; Cacoete animal)",
        "npcs": ["Homem Leão (Líder)", "Conselho das Matilhas", "Xamã das Feras"],
        "pontos": ["Capital das Matilhas", "Templo da Caça", "Porto das Marés", "Arena de Provação"],
    },
}

def build_wiki_page(wiki_file, data):
    """Build a wiki page from structured data."""
    nome = data["nome"]
    
    lines = []
    lines.append(f"# {nome}")
    lines.append("")
    lines.append(f"> **Região**: {data['regiao']} | **Fundação**: Antiga/Variada | **Clima**: Variado")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Localização
    lines.append("## 📍 Localização")
    lines.append(f"- **Região**: {data['regiao']}")
    lines.append(f"- **Tipo**: {data['tipo']}")
    lines.append(f"- **Descrição**: {data['descricao']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Governo
    lines.append("## 🏛️ Governo e Política")
    lines.append(f"- **Tipo**: {data['tipo']}")
    lines.append(f"- **Lealdade**: Variada (Império, Independente, ou própria facção)")
    lines.append(f"- **Estrutura**: Governança adaptada à cultura local")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Cidade/Assentamento
    lines.append("## 🏙️ Cidade/Assentamento")
    for line in data['cultura'].split('. '):
        if line.strip():
            lines.append(f"- {line.strip()}.")
    lines.append("- **Layout**: Adaptado ao terreno e cultura")
    lines.append("- **Atmosfera**: Única à região e povo")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Economia
    lines.append("## 💰 Economia e Recursos")
    lines.append(data['recursos'])
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Vantagem Regional
    lines.append("## 🌟 Vantagem Regional")
    lines.append(f"> **Personagens nascidos em [{nome.lower()}]({wiki_file})**: *{data['vantagem']}*.")
    lines.append(f"> *Nascer aqui molda corpo e mente conforme a terra.*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # NPCs Notáveis
    lines.append("## 👥 NPCs Notáveis")
    lines.append("| Nome | Papel | Detalhes |")
    lines.append("|------|-------|----------|")
    for npc in data['npcs']:
        lines.append(f"| **{npc}** | Papel-chave | Detalhes a extrair do ARCANO_COMPLETO.md |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Pontos de Interesse
    lines.append("## 🗺️ Pontos de Interesse")
    lines.append("| Local | Descrição |")
    lines.append("|-------|-----------|")
    for ponto in data['pontos']:
        lines.append(f"| **{ponto}** | Característica única da região |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Ganchos de Aventura
    lines.append("## 🎯 Ganchos de Aventura")
    hooks = [
        "1. **Conflito Local** — Tensão política/racial/recursos na região",
        "2. **Ameaça Externa** — Inimigo se aproxima (Infestação, Abaité, Império, etc.)",
        "3. **Segredo Antigo** — Ruína/artefato/mistério descoberto na área",
        "4. **Sucessão/Disputa** — Poder em jogo; facções disputam controle",
        "5. **Recurso Vital** — Algo essencial (água, minério, magia) em risco",
    ]
    for hook in hooks:
        lines.append(hook)
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # História Recente
    lines.append("## 📜 História Recente")
    lines.append("- **Fundação/Origem**: Antiga ou expansão imperial")
    lines.append("- **Eventos-chave**: Guerras, tratados, cataclismos, mudanças de poder")
    lines.append("- **Atual**: Situação política/militar atual; tensões ativas")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Vantagem Regional (repeated)
    lines.append("## 🌟 Vantagem Regional")
    lines.append(f"> **Personagens nascidos em [{nome.lower()}]({wiki_file})**: *{data['vantagem']}*.")
    lines.append(f"> *Nascer aqui molda corpo e mente conforme a terra.*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Links Relacionados
    lines.append("## 🔗 Links Relacionados")
    lines.append(f"- [Índice dos Reinos](index.md) — Volta ao índice mestre")
    lines.append(f"- [Império de Aba](../imperio-aba.md) — Contexto imperial (se aplica)")
    lines.append(f"- [Região: {data['regiao']}](../geografia/regioes/index.md) — Contexto geográfico maior")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"> *Página base — complete com detalhes do ARCANO_COMPLETO.md*")
    
    return '\n'.join(lines)

def main():
    print("Generating remaining kingdom pages...")
    for wiki_file, data in REMAINING_KINGDOMS.items():
        print(f"Generating {wiki_file}...")
        page_content = build_wiki_page(wiki_file, data)
        file_path = WIKI_REINOS_DIR / wiki_file
        file_path.write_text(page_content, encoding='utf-8')
        print(f"  Written: {file_path}")
    print("\nDone!")

if __name__ == "__main__":
    main()