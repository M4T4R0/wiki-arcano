#!/usr/bin/env python3
"""
Populate NPC wiki pages from ARCANO_COMPLETO.md
Extracts NPC sections and transforms them into wiki format with 3D&T stats.
"""

import re
from pathlib import Path

ARCANO_PATH = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/ARCANO_COMPLETO.md")
WIKI_NPCS_DIR = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/npcs/individual")

# NPC mapping: search_name -> {wiki_file, display_name, title, race, class, location, faction}
NPCS = {
    "imperador-deziel-áureo.md": {
        "search": ["Deziel Áureo", "Imperador Deziel", "Deziel"],
        "display": "Deziel Áureo",
        "title": "Imperador do Império Aba",
        "race": "Humano Aba",
        "class": "Aristocrata + Guerreiro",
        "location": "Ypy",
        "faction": "Império de Aba",
        "priority": "Alta",
    },
    "áureo-i-fundador-do-império.md": {
        "search": ["Áureo I", "Áureo I, fundador"],
        "display": "Áureo I",
        "title": "Fundador do Império Aba",
        "race": "Humano Aba",
        "class": "Guerreiro + Líder",
        "location": "Ypy (falecido)",
        "faction": "Império de Aba",
        "priority": "Baixa",
    },
    "arthur-áureo-general-imperador.md": {
        "search": ["Arthur Áureo", "Áureo II", "Arthur Áureo II"],
        "display": "Arthur Áureo",
        "title": "General / Imperador Jovem",
        "race": "Humano Aba (possível clone)",
        "class": "Guerreiro + Aristocrata",
        "location": "Ypy",
        "faction": "Império de Aba",
        "priority": "Média",
    },
    "sidius-acemira-dos-auçá.md": {
        "search": ["Sidius", "Sidius Acemira", "Acemira", "General Auçá"],
        "display": "Sidius (Acemira)",
        "title": "Líder Auçá / Acemira",
        "race": "Auçá",
        "class": "Guerreiro + Arauto da Força",
        "location": "Terras dos Auçá / Naur'Ush",
        "faction": "Auçá Imperiais",
        "priority": "Alta",
    },
    "sidius-acemira-auçá.md": {
        "search": ["Sidius", "Acemira"],  # Duplicate - will skip
        "display": "Sidius (Acemira Auçá)",
        "title": "Líder Auçá (duplicata)",
        "race": "Auçá",
        "class": "Guerreiro + Arauto da Força",
        "location": "Terras dos Auçá",
        "faction": "Auçá Imperiais",
        "priority": "Alta",
    },
    "rei-mictian-auçá.md": {
        "search": ["Mictian", "Rei Mictian", "Mictian Guerra"],
        "display": "Mictian (Auçá)",
        "title": "Rei Auçá / General",
        "race": "Auçá",
        "class": "Guerreiro + Aristocrata",
        "location": "Ypiturui",
        "faction": "Auçá Imperiais",
        "priority": "Média",
    },
    "sucelus.md": {
        "search": ["Sucelus"],
        "display": "Sucelus",
        "title": "Guerreiro / Criminoso",
        "race": "Humano",
        "class": "Guerreiro + Ladrão",
        "location": "Moacuba / Nambiquara",
        "faction": "Rilícia / Independente",
        "priority": "Baixa",
    },
    "elros-palantír-mago-glacial-abaré.md": {
        "search": ["Elros", "Palantír", "Elros Palantír"],
        "display": "Elros Palantír",
        "title": "Mago Glacial Abaré",
        "race": "Elfo Abaré (Meio-Elfo)",
        "class": "Mago (Gelo)",
        "location": "Elfin / Jurubatiba",
        "faction": "Abaré / Academia",
        "priority": "Média",
    },
    "escuridão-entidade-da-infestação.md": {
        "search": ["Escuridão", "Entidade da Infestação", "Mestre do Templo"],
        "display": "Escuridão",
        "title": "Entidade da Infestação / Mestre do Templo",
        "race": "Espectro / Morto-Vivo (ex-Humano)",
        "class": "Mago + Guerreiro (Lendário)",
        "location": "Templo do Conhecimento (Floresta Proibida)",
        "faction": "Infestação / Trevas",
        "priority": "Alta",
    },
    "mal-mago-da-torre-de-obsidiana.md": {
        "search": ["Mal", "Mago da Torre de Obsidiana", "MAL"],
        "display": "Mal",
        "title": "Big Bad / Criador da Infestação",
        "race": "Desconhecido (possivelmente Misty As-La)",
        "class": "Mago das Trevas (Lendário)",
        "location": "Torre de Obsidiana (Irundyna / Área Infestada)",
        "faction": "Trevas / Infestação",
        "priority": "Alta",
    },
    "misty-as-la-arquimago-possível-mal.md": {
        "search": ["Misty As-La", "Misty As La"],
        "display": "Misty As-La",
        "title": "Arquimago / Possível Mal / Criador da Infestação",
        "race": "Humano (ex-Arcano Imperial)",
        "class": "Arquimago / Mago das Trevas",
        "location": "Irundyna / Torre de Obsidiana",
        "faction": "Arcanos Imperiais (ex) / Trevas",
        "priority": "Alta",
    },
    "belero-leroy-oráculo-de-moá-mago-vampiro.md": {
        "search": ["Belero", "Leroy", "Belero Leroy", "Oráculo de Moá"],
        "display": "Belero Leroy",
        "title": "Oráculo de Moá / Mago Vampiro",
        "race": "Vampiro (ex-Humano)",
        "class": "Mago + Vampiro / Oráculo",
        "location": "Moacuba",
        "faction": "Oráculo de Moá / Moacuba",
        "priority": "Média",
    },
    "purpleskull-arc-mestre-das-sombras.md": {
        "search": ["Purpleskull", "Purpleskull Arc", "Mestre das Sombras"],
        "display": "Purpleskull Arc",
        "title": "Mestre das Sombras / Fundador de Nambiquara",
        "race": "Humano",
        "class": "Ladino / Assassino / Espião Mestre",
        "location": "Nambiquara",
        "faction": "Nambiquara / Guilda dos Supay",
        "priority": "Média",
    },
    "dragnovith-uller-arquimago-imperial.md": {
        "search": ["Dragnovith", "Uller", "Dragnovith Uller"],
        "display": "Dragnovith Uller",
        "title": "Arquimago Imperial / Fundador de Jurubatiba",
        "race": "Humano",
        "class": "Arquimago",
        "location": "Jurubatiba",
        "faction": "Arcanos Imperiais / Academia Dragonovith",
        "priority": "Baixa",
    },
    "huck-hor-comandante-da-cavalaria.md": {
        "search": ["Huck Hor", "Huck", "Comandante da Cavalaria"],
        "display": "Huck Hor",
        "title": "Comandante da Cavalaria / Fundador de Kaluana",
        "race": "Humano",
        "class": "Guerreiro (Cavaleiro) + Comandante",
        "location": "Kaluana",
        "faction": "Kaluana / Império",
        "priority": "Baixa",
    },
    "baley-ell-curandeiro-do-imperador.md": {
        "search": ["Baley", "Ell", "Baley Ell", "Curandeiro do Imperador"],
        "display": "Baley Ell",
        "title": "Curandeiro do Imperador / Fundador de Aisó",
        "race": "Humano",
        "class": "Curandeiro / Clérigo + Mago",
        "location": "Aisó",
        "faction": "Aisó / Ordem dos Paladinos",
        "priority": "Baixa",
    },
    "stigin-nato-taverneiro-fundador.md": {
        "search": ["Stigin", "Nato", "Stigin Nato", "Taverneiro"],
        "display": "Stigin Nato",
        "title": "Taverneiro Herói / Fundador de Camuá",
        "race": "Humano",
        "class": "Mascate / Herói Popular",
        "location": "Camuá",
        "faction": "Camuá / Organização Livre Comércio",
        "priority": "Baixa",
    },
    "karnos-minor-arquimago-faraó-de-ybi.md": {
        "search": ["Karnos Minor", "Karnos", "Faraó de Ybi", "Primeiro Múmia-Viva"],
        "display": "Karnos Minor",
        "title": "Arquimago / Faraó Eterno de Ybi",
        "race": "Múmia-Viva (ex-Humano)",
        "class": "Arquimago / Necromante Ritualístico",
        "location": "Ybi (Deserto Leste)",
        "faction": "Ybi / Faraós",
        "priority": "Baixa",
    },
    "karnos-minor-arquimago-de-ybi.md": {
        "search": ["Karnos Minor"],  # Duplicate
        "display": "Karnos Minor (duplicata)",
        "title": "Arquimago de Ybi",
        "race": "Múmia-Viva",
        "class": "Arquimago",
        "location": "Ybi",
        "faction": "Ybi",
        "priority": "Baixa",
    },
    "ror-general-auçá-fundador-de-naurush.md": {
        "search": ["Ror", "General Ror", "Ror Auçá"],
        "display": "Ror",
        "title": "General Auçá / Fundador de Naur'Ush",
        "race": "Auçá (Ressureito consciente)",
        "class": "Guerreiro + General + Mago",
        "location": "Naur'Ush / Kisé",
        "faction": "Auçá Livres / Auçá Imperiais",
        "priority": "Média",
    },
    "luna-lin-amazona.md": {
        "search": ["Luna Lin", "Luna", "Amazona", "Amante de Áureo"],
        "display": "Luna Lin",
        "title": "Amazona / Mãe de Arthur Áureo / Fundadora de Poranga",
        "race": "Humana (Amazona)",
        "class": "Guerreira (Arqueira) + Líder",
        "location": "Poranga / Deserto Leste",
        "faction": "Independente / Amazona",
        "priority": "Baixa",
    },
    "vlad-dracul.md": {
        "search": ["Vlad Dracul", "Vlad", "Dracul", "Primeiro Vampiro"],
        "display": "Vlad Dracul",
        "title": "Primeiro Vampiro de Airy / Mago das Trevas",
        "race": "Vampiro (ex-Humano Aba)",
        "class": "Mago das Trevas / Vampiro Lorde",
        "location": "Desconhecido / Moacuba (rumores)",
        "faction": "Seita de Dracul / Trevas",
        "priority": "Baixa",
    },
    "homem-leão.md": {
        "search": ["Homem Leão", "Líder dos Yawara"],
        "display": "Homem Leão",
        "title": "Líder dos Yawara (Kemonos)",
        "race": "Yawara (Kemono Leão)",
        "class": "Líder / Guerreiro",
        "location": "Acag (Arquipélago Yawara)",
        "faction": "Yawara / Acag",
        "priority": "Baixa",
    },
    "faraós-de-ybi.md": {
        "search": ["Faraós de Ybi", "Faraós", "Dinastia dos Faraós"],
        "display": "Faraós de Ybi",
        "title": "Dinastia dos Faraós (Múmias-Vivas)",
        "race": "Múmias-Vivas (Humanos rituais)",
        "class": "Arquimagos / Necromantes",
        "location": "Ybi (Deserto Leste)",
        "faction": "Ybi / Faraós",
        "priority": "Baixa",
    },
    "paladinos-de-aisó.md": {
        "search": ["Paladinos de Aisó", "Ordem dos Paladinos", "Templários de Aisó"],
        "display": "Paladinos de Aisó",
        "title": "Ordem Religiosa/Militar de Aisó",
        "race": "Humanos (maioria)",
        "class": "Paladinos / Cavaleiros Sagrados",
        "location": "Aisó",
        "faction": "Aisó / Ordem da Luz nas Sombras",
        "priority": "Baixa",
    },
    "guarda-açã.md": {
        "search": ["Guarda Açã", "Guarda Açá", "Condenados da Muralha"],
        "display": "Guarda Açã",
        "title": "Guarda da Grande Muralha (Condenados/Exilados)",
        "race": "Auçá / Humanos / Diversos",
        "class": "Guerreiros / Penal",
        "location": "Ypiturui / Grande Muralha",
        "faction": "Ypiturui / Império",
        "priority": "Baixa",
    },
    "casa-agar.md": {
        "search": ["Casa Agar", "Agar", "Nobreza de Kisé"],
        "display": "Casa Agar",
        "title": "Casa Nobre de Kisé (Parte Nova)",
        "race": "Humanos Aba",
        "class": "Aristocratas / Políticos / Manipuladores",
        "location": "Kisé (Parte Nova)",
        "faction": "Kisé / Nobreza Imperial",
        "priority": "Baixa",
    },
    "casa-kalan.md": {
        "search": ["Casa Kalan", "Kalan", "Comércio Aba-Auçá"],
        "display": "Casa Kalan",
        "title": "Casa Comercial Aba-Auçá / Espiões",
        "race": "Humanos / Auçá (misto)",
        "class": "Mercadores / Espiões / Chantagistas",
        "location": "Kisé / Ypy / Rotas Comerciais",
        "faction": "Independente / Nobreza",
        "priority": "Baixa",
    },
    "alquimistaarquimago-misty-as-la.md": {
        "search": ["Misty As-La"],  # Duplicate of misty-as-la
        "display": "Misty As-La (Alquimista/Arquimago)",
        "title": "Arquimago Alquimista",
        "race": "Humano",
        "class": "Arquimago / Alquimista",
        "location": "Irundyna",
        "faction": "Arcanos Imperiais",
        "priority": "Alta",
    },
    "meio-elfos-caçadores-de-magos-arcanos-imperiais.md": {
        "search": ["Meio-Elfos Caçadores", "Caçadores de Magos"],
        "display": "Meio-Elfos Caçadores de Magos",
        "title": "Kit: Caçadores de Magos Arcanos Imperiais",
        "race": "Meio-Elfos",
        "class": "Caçador / Arqueiro + Anti-Mago",
        "location": "Jurubatiba / Elfin",
        "faction": "Abaré / Meio-Elfos",
        "priority": "Média",
    },
}

def load_arcano():
    """Load ARCANO_COMPLETO.md."""
    return ARCANO_PATH.read_text(encoding='utf-8')

def find_npc_section(content, search_terms):
    """Find the section in ARCANO that contains NPC info."""
    # Split by major headings
    sections = re.split(r'\n(?=# \*\*[^*]+\*\*)', content)
    
    best_section = ""
    best_score = 0
    
    for section in sections:
        score = 0
        section_lower = section.lower()
        for term in search_terms:
            if term.lower() in section_lower:
                score += section_lower.count(term.lower()) * len(term)
        if score > best_score:
            best_score = score
            best_section = section
    
    # Also search in the full text for specific NPC mentions
    if best_score < 10:
        # Try to find paragraphs mentioning the NPC
        paragraphs = re.split(r'\n\n+', content)
        for para in paragraphs:
            score = 0
            para_lower = para.lower()
            for term in search_terms:
                if term.lower() in para_lower:
                    score += para_lower.count(term.lower()) * len(term)
            if score > best_score:
                best_score = score
                best_section = para
    
    return best_section if best_score > 0 else ""

def extract_lore(content, search_terms):
    """Extract relevant lore paragraphs for the NPC."""
    paragraphs = re.split(r'\n\n+', content)
    relevant = []
    for para in paragraphs:
        para_lower = para.lower()
        for term in search_terms:
            if term.lower() in para_lower:
                # Clean up
                clean = para.strip()
                if len(clean) > 50:  # Only substantial paragraphs
                    relevant.append(clean)
                break
    return relevant[:8]  # Max 8 paragraphs

def build_npc_page(wiki_file, npc_data, arcano_content):
    """Build a comprehensive NPC wiki page."""
    
    search_terms = npc_data["search"]
    display = npc_data["display"]
    title = npc_data["title"]
    race = npc_data["race"]
    class_ = npc_data["class"]
    location = npc_data["location"]
    faction = npc_data["faction"]
    priority = npc_data["priority"]
    
    # Skip duplicates
    if "duplicata" in display.lower() or "duplicate" in display.lower():
        return None
    
    # Find content in ARCANO
    section = find_npc_section(arcano_content, search_terms)
    lore_paragraphs = extract_lore(arcano_content, search_terms)
    
    lines = []
    lines.append(f"# {display}")
    lines.append("")
    lines.append(f"> **{title}** — {race} | {class_} | {location} | {faction}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Ficha 3D&T Sugerida
    lines.append("## ⚔️ Ficha 3D&T Alpha Sugerida")
    lines.append("")
    
    # Determine kit based on class
    kit = determine_kit(class_, race, priority)
    lines.append(f"**Kit Base**: {kit}")
    lines.append("")
    
    # Atributos sugeridos
    attrs = suggest_attributes(class_, race, priority)
    lines.append("### Atributos Base (Sugeridos)")
    lines.append("")
    lines.append("| Atributo | Valor |")
    lines.append("|----------|-------|")
    for attr, val in attrs.items():
        lines.append(f"| **{attr}** | {val} |")
    lines.append("")
    
    # Vantagens/Desvantagens
    vantagens, desvantagens = suggest_vantagens_desvantagens(class_, race, priority)
    if vantagens:
        lines.append("### Vantagens Sugeridas")
        lines.append("")
        for v in vantagens:
            lines.append(f"- **{v}**")
        lines.append("")
    
    if desvantagens:
        lines.append("### Desvantagens Sugeridas")
        lines.append("")
        for d in desvantagens:
            lines.append(f"- **{d}**")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Lore
    lines.append("## 📜 Lore e História")
    lines.append("")
    if lore_paragraphs:
        for para in lore_paragraphs[:5]:
            # Clean up
            clean = re.sub(r'\s+', ' ', para).strip()
            if len(clean) > 30:
                lines.append(clean)
                lines.append("")
    else:
        lines.append(f"*Detalhes a extrair do ARCANO_COMPLETO.md para {display}.*")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Conexões e Relacionamentos
    lines.append("## 🔗 Conexões e Relacionamentos")
    lines.append("")
    connections = suggest_connections(display, faction, location, search_terms)
    for conn in connections:
        lines.append(f"- **{conn[0]}**: {conn[1]}")
    lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Ganchos de Aventura
    lines.append("## 🎯 Ganchos de Aventura")
    lines.append("")
    hooks = suggest_hooks(display, class_, faction, priority)
    for i, hook in enumerate(hooks, 1):
        lines.append(f"{i}. **{hook}**")
    lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Equipamento/Itens Notáveis
    lines.append("## 🎒 Equipamento e Itens Notáveis")
    lines.append("")
    items = suggest_items(class_, race, priority, display)
    for item in items:
        lines.append(f"- **{item[0]}**: {item[1]}")
    lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Links Relacionados - only to existing pages
    lines.append("## 🔗 Links Relacionados")
    lines.append("")
    lines.append(f"- [Índice de NPCs](index.md) — Volta ao índice")
    
    # Check existing faction pages
    base = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs")
    # Faction pages (from npcs/individual/ -> ../../factions/)
    faction_files = {
        "império de aba": "../../factions/imperio-aba.md",
        "imperio de aba": "../../factions/imperio-aba.md",
        "arcanos imperiais": "../../factions/ordem-arcanos-imperiais.md",
        "ordem dos senhores do escudo": "../../factions/ordem-senhores-escudo.md",
        "guilda era": "../../factions/guilda-era.md",
        "estados tampões": "../../factions/estados-tampoees.md",
        "trevas": "../../factions/ordem-arcanos-imperiais.md",  # closest
        "infestação": "../../geografia/area-infestada.md",
        "auçá imperiais": "../../factions/ordem-arcanos-imperiais.md",
        "auçá livres": "../../factions/reinos/naurush.md",
        "oráculo de moá": "../../factions/reinos/moacuba.md",
        "nambiquara": "../../factions/reinos/nambiquara.md",
        "ybi": "../../factions/reinos/ybi.md",
        "faróis": "../../factions/reinos/ybi.md",
        "ypiturui": "../../factions/reinos/ypiturui.md",
        "grande muralha": "../../geografia/mapa-mundi.md",
        "irundyna": "../../factions/reinos/irundyna.md",
        "torre de obsidiana": "../../factions/reinos/irundyna.md",
        "guilda dos supay": "../../factions/reinos/nambiquara.md",
        "yawara": "../../factions/reinos/acag.md",
        "acag": "../../factions/reinos/acag.md",
        "seita de dracul": "../../factions/reinos/moacuba.md",
        "ordem da luz nas sombras": "../../factions/reinos/aiso.md",
        "aisó": "../../factions/reinos/aiso.md",
        "camuá": "../../factions/reinos/camua.md",
        "organização livre comércio": "../../factions/reinos/camua.md",
        "abaré": "../../factions/reinos/elfin.md",
        "meio-elfos": "../../factions/reinos/elfin.md",
        "jurubatiba": "../../factions/reinos/jurubatiba.md",
        "academia dragonovith": "../../factions/reinos/jurubatiba.md",
        "kaluana": "../../factions/reinos/kaluana.md",
        "moacuba": "../../factions/reinos/moacuba.md",
        "elfin": "../../factions/reinos/elfin.md",
        "naur'ush": "../../factions/reinos/naurush.md",
        "kisé": "../../factions/reinos/kise.md",
        "ypy": "../../factions/reinos/ypy.md",
        "terra dos auçá": "../../factions/reinos/terras-auca.md",
        "terras selvagens": "../../factions/reinos/terra-selvagem.md",
        "vil dracul": "../../factions/reinos/moacuba.md",
    }
    
    faction_lower = faction.lower()
    if faction_lower in faction_files:
        lines.append(f"- [{faction}]({faction_files[faction_lower]}) — Facção principal")
    else:
        # Try partial match
        matched = False
        for key, path in faction_files.items():
            if key in faction_lower or faction_lower in key:
                lines.append(f"- [{faction}]({path}) — Facção relacionada")
                matched = True
                break
        if not matched:
            lines.append(f"- *Facção: {faction} (página a criar)*")
    
    # Location (reinos)
    location_files = {
        "ypy": "../../factions/reinos/ypy.md",
        "kisé": "../../factions/reinos/kise.md",
        "irundyna": "../../factions/reinos/irundyna.md",
        "moacuba": "../../factions/reinos/moacuba.md",
        "nambiquara": "../../factions/reinos/nambiquara.md",
        "naur'ush": "../../factions/reinos/naurush.md",
        "naurush": "../../factions/reinos/naurush.md",
        "terras dos auçá": "../../factions/reinos/terras-auca.md",
        "terras-auca": "../../factions/reinos/terras-auca.md",
        "ybi": "../../factions/reinos/ybi.md",
        "ypiturui": "../../factions/reinos/ypiturui.md",
        "kaluana": "../../factions/reinos/kaluana.md",
        "camuá": "../../factions/reinos/camua.md",
        "camua": "../../factions/reinos/camua.md",
        "aisó": "../../factions/reinos/aiso.md",
        "aiso": "../../factions/reinos/aiso.md",
        "elfin": "../../factions/reinos/elfin.md",
        "jurubatiba": "../../factions/reinos/jurubatiba.md",
        "arani": "../../factions/reinos/arani.md",
        "acag": "../../factions/reinos/acag.md",
        "yawara": "../../factions/reinos/acag.md",
        "fortuna": "../../factions/reinos/fortuna.md",
        "sam-mael": "../../factions/reinos/sam-mael.md",
        "tiba": "../../factions/reinos/tiba.md",
        "yu": "../../factions/reinos/yu.md",
        "ybytu": "../../factions/reinos/ybytu.md",
        "araxá": "../../factions/reinos/araxa.md",
        "araxa": "../../factions/reinos/araxa.md",
        "avista": "../../factions/reinos/avista.md",
        "mbaê": "../../factions/reinos/mbae.md",
        "mbae": "../../factions/reinos/mbae.md",
        "landé": "../../factions/reinos/lande.md",
        "lande": "../../factions/reinos/lande.md",
        "yby": "../../factions/reinos/yby.md",
        "anama": "../../factions/reinos/anama.md",
        "andirá": "../../factions/reinos/andira.md",
        "andira": "../../factions/reinos/andira.md",
        "terra selvagem": "../../factions/reinos/terra-selvagem.md",
        "terra-selvagem": "../../factions/reinos/terra-selvagem.md",
        "poranga": "../../factions/reinos/poranga.md",  # doesn't exist yet
    }
    
    location_lower = location.lower()
    if location_lower in location_files:
        lines.append(f"- [{location}]({location_files[location_lower]}) — Localização")
    else:
        # Try partial match
        matched = False
        for key, path in location_files.items():
            if key in location_lower or location_lower in key:
                if "poranga" not in key:  # skip non-existent
                    lines.append(f"- [{location}]({path}) — Localização relacionada")
                matched = True
                break
        if not matched and location != "Desconhecido":
            lines.append(f"- *Localização: {location} (página a criar)*")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"> *Página populada a partir do ARCANO_COMPLETO.md — revise e complete (Prioridade: {priority})*")
    
    return '\n'.join(lines)

def determine_kit(class_, race, priority):
    """Determine 3D&T kit based on class/race."""
    class_lower = class_.lower()
    if "aristocrata" in class_lower and "guerreiro" in class_lower:
        return "Aristocrata Completo + Guerreiro Armadura Completa"
    elif "arquimago" in class_lower or "mago" in class_lower:
        return "Mago Completo (Escola: conforme lore) + Aristocrata (se nobre)"
    elif "guerreiro" in class_lower and "cavaleiro" in class_lower:
        return "Guerreiro Armadura Completa + Cavaleiro"
    elif "ladino" in class_lower or "assassino" in class_lower or "espião" in class_lower:
        return "Ladino Completo + Assassino"
    elif "curandeiro" in class_lower or "clérigo" in class_lower:
        return "Curandeiro Completo + Mago (Escola: Cura/Luz)"
    elif "paladino" in class_lower:
        return "Paladino Completo (Crenças: conforme fé)"
    elif "general" in class_lower or "comandante" in class_lower:
        return "Guerreiro Armadura Completa + Aristocrata (Comando)"
    elif "vampiro" in class_lower:
        return "Vampiro (Maldição) + Mago (Trevas/Sangue)"
    elif "múmia" in class_lower or "faraó" in class_lower:
        return "Mago Completo (Necromancia Ritual) + Aristocrata"
    elif "espectro" in class_lower or "morto-vivo" in class_lower:
        return "Mago Completo (Trevas/Necromancia) + Guerreiro (Lendário)"
    else:
        return "Kit Personalizado (conforme conceito)"

def suggest_attributes(class_, race, priority):
    """Suggest base attributes."""
    base = {"Força": "2", "Habilidade": "2", "Resistência": "2", "Armadura": "1", "Poder de Fogo": "2"}
    
    class_lower = class_.lower()
    if "guerreiro" in class_lower or "general" in class_lower or "cavaleiro" in class_lower:
        base["Força"] = "3"
        base["Resistência"] = "3"
        base["Armadura"] = "2"
    elif "mago" in class_lower or "arquimago" in class_lower:
        base["Poder de Fogo"] = "4"
        base["Habilidade"] = "3"
    elif "ladino" in class_lower or "assassino" in class_lower:
        base["Habilidade"] = "4"
        base["Força"] = "2"
    elif "aristocrata" in class_lower or "líder" in class_lower:
        base["Habilidade"] = "3"
        base["Poder de Fogo"] = "3"
    
    if priority == "Alta":
        # Legendary NPCs get +1 across board
        for k in base:
            base[k] = str(int(base[k]) + 1)
    
    return base

def suggest_vantagens_desvantagens(class_, race, priority):
    """Suggest advantages/disadvantages."""
    vantagens = []
    desvantagens = []
    
    class_lower = class_.lower()
    race_lower = race.lower()
    
    # Race-based
    if "auçá" in race_lower:
        vantagens.extend(["Exoesqueleto Natural (Armadura +2)", "Regeneração 1 PV/rodada", "Imune a Infestação"])
        desvantagens.append("Fraqueza: Obsidiana (anula regeneração)")
    elif "elfo" in race_lower or "abaré" in race_lower:
        vantagens.extend(["Visão Aguçada", "Natureza Mística", "Código de Honra"])
        desvantagens.append("Fracote (-1 Força)")
    elif "anão" in race_lower or "akitã" in race_lower:
        vantagens.extend(["Abascanto", "Infravisão", "Incansável"])
        desvantagens.extend(["Código (Honra Anã)", "Tapado"])
    elif "vampiro" in race_lower:
        vantagens.extend(["Imortalidade", "Regeneração (Sangue)", "Sentidos Aguçados"])
        desvantagens.extend(["Fraqueza: Sol/Luz", "Sede de Sangue", "Vulnerável a Prata/Madeira"])
    elif "múmia" in race_lower or "faraó" in race_lower:
        vantagens.extend(["Imortalidade Ritual", "Não envelhece", "Comando sobre Mortos-Vivos"])
        desvantagens.extend(["Lento", "Vulnerável a Fogo", "Ligado ao Sarcófago"])
    elif "espectro" in race_lower or "morto-vivo" in race_lower:
        vantagens.extend(["Incorporeidade", "Imune a Veneno/Doença", "Visão nas Trevas"])
        desvantagens.extend(["Ligado ao Local", "Fraqueza: Luz/Purificação", "Não cura naturalmente"])
    
    # Class-based
    if "aristocrata" in class_lower:
        vantagens.extend(["Riqueza", "Posição Social", "Contatos Nobres"])
    if "guerreiro" in class_lower or "general" in class_lower:
        vantagens.extend(["Armadura Extra", "Golpe Poderoso", "Comando"])
    if "mago" in class_lower or "arquimago" in class_lower:
        vantagens.extend(["Mana Extra", "Escola de Magia", "Concentração"])
    if "ladino" in class_lower or "assassino" in class_lower:
        vantagens.extend(["Furtividade", "Ataque Furtivo", "Contatos Criminosos"])
    if "curandeiro" in class_lower:
        vantagens.extend(["Cura Mágica", "Bênção", "Impor as Mãos"])
    if "paladino" in class_lower:
        vantagens.extend(["Detectar Mal", "Aura de Coragem", "Golpe Sagrado"])
    
    # Priority-based
    if priority == "Alta":
        vantagens.append("Lendário (atributos +1, PV extra)")
    
    # Remove duplicates
    vantagens = list(dict.fromkeys(vantagens))
    desvantagens = list(dict.fromkeys(desvantagens))
    
    return vantagens[:10], desvantagens[:6]

def suggest_connections(display, faction, location, search_terms):
    """Suggest NPC connections."""
    connections = []
    
    # Faction leader
    connections.append((f"Líder de {faction}", "Relacionamento direto com a hierarquia"))
    
    # Location
    if location != "Desconhecido":
        connections.append((location, f"Base de operações / Origem"))
    
    # Specific known connections from index
    known = {
        "Deziel Áureo": [("Arthur Áureo", "Filho/Clone (sucessor)"), ("Senado Imperial", "Controlado/Manipulado"), ("Arcanos Imperiais", "Polícia secreta leal")],
        "Áureo I": [("Arthur Áureo", "Filho/Clone"), ("Luna Lin", "Amante/Mãe de Arthur"), ("Dragnovith Uller", "Arquimago do exército"), ("Huck Hor", "Comandante da Cavalaria"), ("Baley Ell", "Curandeiro pessoal"), ("Stigin Nato", "Amigo/Taverneiro"), ("Purpleskull Arc", "Espião especialista")],
        "Arthur Áureo": [("Deziel Áureo", "Pai/Original"), ("Luna Lin", "Mãe"), ("Generais Imperiais", "Comando militar")],
        "Sidius": [("Mictian", "Rei/Superior"), ("Ror", "General subordinado"), ("Auçá Livres", "Inimigos ideológicos")],
        "Mictian": [("Sidius", "Acemira/Subordinado"), ("Ror", "General/Fundador de Naur'Ush"), ("Kaluana", "Fundada por Huck Hor")],
        "Escuridão": [("Andus", "Ex-melhor amigo (morto)"), ("Templo do Conhecimento", "Prisão/Lar"), ("Infestação", "Mestre/Entidade")],
        "Mal": [("Misty As-La", "Possível identidade"), ("Irundyna", "Torre de Obsidiana"), ("Infestação", "Criador")],
        "Misty As-La": [("Mal", "Possível identidade"), ("Arcanos Imperiais", "Ex-colegas"), ("Infestação", "Criadora")],
        "Belero Leroy": [("Moacuba", "Oráculo"), ("Vampirismo", "Segredo"), ("Rainha Morrigan", "Possível conexão")],
        "Purpleskull Arc": [("Nambiquara", "Fundador/Governante"), ("Áureo I", "Ganhou em aposta"), ("Guilda dos Supay", "Líder")],
        "Dragnovith Uller": [("Jurubatiba", "Fundador"), ("Academia Imperial", "Diretor"), ("Áureo I", "Arquimago do exército")],
        "Huck Hor": [("Kaluana", "Fundador"), ("Áureo I", "Comandante da Cavalaria")],
        "Baley Ell": [("Aisó", "Fundador"), ("Áureo I", "Curandeiro pessoal"), ("Paladinos de Aisó", "Inspiração")],
        "Stigin Nato": [("Camuá", "Fundador"), ("Áureo I", "Amigo/Salvou a vida")],
        "Karnos Minor": [("Ybi", "Faraó Eterno"), ("Faraós de Ybi", "Ensinou imortalidade"), ("Vlad Dracul", "Contemporâneo")],
        "Ror": [("Naur'Ush", "Fundador"), ("Kisé", "Salvou no cerco"), ("Auçá Livres", "Líder")],
        "Luna Lin": [("Arthur Áureo", "Mãe"), ("Áureo I", "Amante"), ("Poranga", "Fundadora")],
        "Vlad Dracul": [("Karnos Minor", "Contemporâneo imortalidade"), ("Moacuba", "Seita/rumores"), ("Primeiro Vampiro", "Pacto demoníaco")],
        "Homem Leão": [("Acag", "Líder"), ("Yawara", "Espécie")],
    }
    
    if display in known:
        for name, rel in known[display]:
            connections.append((name, rel))
    
    return connections[:6]

def suggest_hooks(display, class_, faction, priority):
    """Suggest adventure hooks."""
    hooks = []
    
    class_lower = class_.lower()
    
    if priority == "Alta":
        hooks.append(f"Confrontar/Alinhar com {display} — NPC central da campanha")
        hooks.append(f"Descobrir a verdade sobre {display} — segredo que muda o cenário")
    
    if "imperador" in display.lower() or "rei" in display.lower() or "líder" in class_lower:
        hooks.append(f"Sucessão/Usurpação — {display} morre/desaparece; PCs decidem o futuro")
        hooks.append(f"Conspiração Interna — Facção tenta remover {display}; PCs investigam/protegem")
    
    if "mago" in class_lower or "arquimago" in class_lower:
        hooks.append(f"Artefato Perdido — {display} procura item poderoso; PCs recuperam/roubam")
        hooks.append(f"Magia Proibida — {display} usa Trevas; Arcanos Imperiais caçam; PCs escolhem lado")
    
    if "guerreiro" in class_lower or "general" in class_lower:
        hooks.append(f"Cerco/Batalha — {display} lidera exército; PCs são oficiais/espiões/sobreviventes")
        hooks.append(f"Rivalidade Militar — Outro general desafia {display}; duelo ou guerra civil")
    
    if "vampiro" in class_lower or "morto-vivo" in class_lower:
        hooks.append(f"Caça ao Vampiro — {display} se alimenta de inocentes; PCs caçam ou negociam")
        hooks.append(f"Pacto Sombrio — {display} oferece poder imortal; preço: alma/serviço")
    
    if "ladino" in class_lower or "assassino" in class_lower or "espião" in class_lower:
        hooks.append(f"Golpe Político — {display} manipula sucessão; PCs expõem ou auxiliam")
        hooks.append(f"Roubo Lendário — {display} rouba item chave; PCs recuperam antes que use")
    
    if "curandeiro" in class_lower or "paladino" in class_lower:
        hooks.append(f"Praga/Maldição — {display} é única cura; sequestrado/corrompido; PCs resgatam")
        hooks.append(f"Fé Testada — {display} questiona sua divindade; PCs restauram ou destroem")
    
    # Generic
    hooks.extend([
        f"Encontro Casual — PCs cruzam com {display} em {faction}; conversa revela segredo",
        f"Missão de {display} — NPC contrata PCs para tarefa perigosa; recompensa única",
        f"Legado de {display} — Após morte/desaparecimento, herança/segredo cai nas mãos dos PCs",
    ])
    
    return hooks[:5]

def suggest_items(class_, race, priority, display=""):
    """Suggest notable equipment."""
    items = []
    
    class_lower = class_.lower()
    race_lower = race.lower()
    display_lower = display.lower()
    
    if "imperador" in display_lower or "rei" in display_lower:
        items.append(("Coroa/Insígnia Imperial", "Símbolo de autoridade; +1 Manipulação/Liderança"))
        items.append(("Espada Cerimonial", "Arma lendária da dinastia; pode ser +2 ou mágica"))
    
    if "mago" in class_lower or "arquimago" in class_lower:
        items.append(("Grimório Pessoal", "Contém magias exclusivas; valor inestimável"))
        items.append(("Foco Arcano (Cajado/Orbe)", "+1 PdF; reduz custo de PM de uma escola"))
    
    if "guerreiro" in class_lower or "general" in class_lower:
        items.append(("Armadura de Placas Mestra", "Armadura +3; sem penalidade de Movimento"))
        items.append(("Arma de Família/Lendária", "Espada/Machado +2; propriedade única (ex: Acerto Crítico)"))
    
    if "vampiro" in race_lower:
        items.append(("Anel de Proteção Solar", "Permite andar ao sol por 1 hora/dia"))
        items.append(("Adaga de Prata/Madeira", "Dano dobrado contra vampiros; arma de último recurso"))
    
    if "auçá" in race_lower:
        items.append(("Exoesqueleto Natural", "Já incluso; Armadura +2, Regeneração"))
        items.append(("Arma Biológica", "Parte do corpo; não pode ser desarmado"))
    
    if "ladino" in class_lower or "assassino" in class_lower:
        items.append(("Adagas Ocultas (par)", "Furtividade +2; Ataque Furtivo +1d"))
        items.append(("Kit de Arrombamento/Disfarce", "Ferramentas mestras; +2 testes"))
    
    if priority == "Alta":
        items.append(("Artefato Lendário Único", "Item que define o NPC; poder de campanha"))
    
    # Default
    if not items:
        items.append(("Equipamento Padrão da Classe", "Conforme kit 3D&T sugerido"))
    
    return items[:5]

def main():
    print("Loading ARCANO_COMPLETO.md...")
    arcano_content = load_arcano()
    print(f"Loaded {len(arcano_content)} characters")
    
    for wiki_file, npc_data in NPCS.items():
        # Skip duplicates
        if "duplicata" in npc_data["display"].lower() or "duplicate" in npc_data["display"].lower():
            print(f"Skipping {wiki_file} (duplicate)")
            continue
        
        print(f"Generating {wiki_file} ({npc_data['display']})...")
        page_content = build_npc_page(wiki_file, npc_data, arcano_content)
        if page_content:
            file_path = WIKI_NPCS_DIR / wiki_file
            file_path.write_text(page_content, encoding='utf-8')
            print(f"  Written: {file_path} ({len(page_content)} chars)")
        else:
            print(f"  Skipped (no content)")
    
    print("\nDone!")

if __name__ == "__main__":
    main()