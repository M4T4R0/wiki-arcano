#!/usr/bin/env python3
"""
Populate kingdom wiki pages from ARCANO_COMPLETO.md
Extracts kingdom sections and transforms them into wiki format.
"""

import re
from pathlib import Path

ARCANO_PATH = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/ARCANO_COMPLETO.md")
WIKI_REINOS_DIR = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/factions/reinos")

# Mapping: kingdom_name_in_arcano -> wiki_filename
KINGDOM_MAP = {
    "Ypy": "ypy.md",
    "Kisé": "kise.md", 
    "Moacuba": "moacuba.md",
    "Aratama": "aratama.md",
    "Aisó": "aiso.md",
    "Camuá": "camua.md",
    "Jurubatiba": "jurubatiba.md",
    "Kaluana": "kaluana.md",
    "Nambiquara": "nambiquara.md",
    "Ypiturui": "ypiturui.md",
    "Sam-Mael": "sam-mael.md",
    "Elfin": "elfin.md",
    "Andirá": "andira.md",
    "Fortuna": "fortuna.md",
    "Ybytu": "ybytu.md",
    "Arani": "arani.md",
    "Mbaê": "mbae.md",
    "Ybi": "ybi.md",
    "Anama": "anama.md",  # "Terra dos Kaapora" section
    "Terra Selvagem": "terra-selvagem.md",
    "Yu": "yu.md",
    "Terra dos Auçás": "terras-auca.md",
    "Landé": "lande.md",
    "Yby": "yby.md",
    "Irundyna": "irundyna.md",
    "Araxá": "araxa.md",
    "Avista": "avista.md",
    "Naur'ush": "naurush.md",
    "Tiba": "tiba.md",
    "Acag": "acag.md",
}

def load_arcano():
    """Load and parse ARCANO_COMPLETO.md into sections."""
    content = ARCANO_PATH.read_text(encoding='utf-8')
    
    # Split by major headings: # **Title**
    sections = re.split(r'\n(?=# \*\*[^*]+\*\*)', content)
    
    kingdom_content = {}
    for section in sections:
        match = re.match(r'# \*\*([^*]+)\*\*', section)
        if match:
            title = match.group(1).strip()
            for arcano_name, wiki_file in KINGDOM_MAP.items():
                if arcano_name.lower() in title.lower():
                    kingdom_content[wiki_file] = section
                    break
    
    return kingdom_content

def extract_field(section, field_name, patterns=None):
    """Extract a field value from the section."""
    if patterns is None:
        patterns = [
            rf'\*\*{field_name}:\*\*\s*([^\n]+)',
            rf'{field_name}:\s*([^\n]+)',
        ]
    
    for pattern in patterns:
        match = re.search(pattern, section, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extract_section_content(section, header_keywords):
    """Extract content under a specific header (### or **)."""
    for header in header_keywords:
        # Try ### Header
        pattern = rf'###\s*{re.escape(header)}\s*\n(.*?)(?=\n###|\n\*\*|\n# |\Z)'
        match = re.search(pattern, section, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Try **Header**
        pattern = rf'\*\*{re.escape(header)}\*\*\s*\n(.*?)(?=\n\*\*|\n###|\n# |\Z)'
        match = re.search(pattern, section, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Try numbered sections like **1. Pessoas (Cultura e Recursos)**
        pattern = rf'\*\*\d+\.\s*{re.escape(header)}[^*]*\*\*\s*\n(.*?)(?=\n\*\*\d+\.|\n\*\*|\n###|\n# |\Z)'
        match = re.search(pattern, section, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None

def clean_markdown(text):
    """Clean up extracted markdown."""
    if not text:
        return ""
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text

def build_wiki_page(wiki_file, section):
    """Build a wiki page from ARCANO section."""
    
    # Extract basic info
    nome_map = {
        'ypy': 'Ypy', 'kise': 'Kisé', 'mbae': 'Mbaê', 'ybi': 'Ybi',
        'yby': 'Yby', 'ybytu': 'Ybytu', 'terras-auca': 'Terras dos Auçá',
        'terra-selvagem': 'Terra Selvagem', 'sam-mael': 'Sam-Mael',
        'naurush': "Naur'Ush", 'ypiturui': 'Ypiturui', 'landé': 'Landé',
        'irundyna': 'Irundyna', 'araxa': 'Araxá', 'avista': 'Avista',
        'tiba': 'Tiba', 'acag': 'Acag',
    }
    base_name = wiki_file.replace('.md', '')
    nome = nome_map.get(base_name, base_name.replace('-', ' ').title())
    
    regiao = extract_field(section, 'Região') or extract_field(section, 'Localização')
    fundacao = extract_field(section, 'Fundação')
    populacao = extract_field(section, 'População')
    especies = extract_field(section, 'Espécies') or extract_field(section, 'Espécie')
    gentilic = extract_field(section, 'Gentílico')
    capital = extract_field(section, 'Capital')
    governo = extract_field(section, 'Governo') or extract_field(section, 'Tipo')
    regente = extract_field(section, 'Regente') or extract_field(section, 'Líder')
    simbolo = extract_field(section, 'Símbolo') or extract_field(section, 'Simbolo')
    clima = extract_field(section, 'Clima')
    terreno = extract_field(section, 'Terreno Dominante')
    
    # Extract main sections
    cultura_recursos = extract_section_content(section, [
        'Pessoas (Cultura e Recursos)', 'Cultura e Recursos', '1. Pessoas'
    ])
    
    faccoes = extract_section_content(section, [
        'Facções Dominantes', '2. Facções', 'Facções'
    ])
    
    topografia = extract_section_content(section, [
        'Topografia e Marcos', '3. Topografia', 'Topografia', 'Marcos'
    ])
    
    historia = extract_section_content(section, [
        'História', 'História Recente', '4. História'
    ])
    
    # Build the page
    lines = []
    lines.append(f"# {nome}")
    lines.append("")
    
    # Header info
    header_parts = []
    if regiao:
        header_parts.append(f"**Região**: {regiao}")
    if fundacao:
        header_parts.append(f"**Fundação**: {fundacao}")
    if clima:
        header_parts.append(f"**Clima**: {clima}")
    lines.append(f"> {' | '.join(header_parts)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Localização
    lines.append("## 📍 Localização")
    if regiao:
        lines.append(f"- **Região**: {regiao}")
    if capital:
        lines.append(f"- **Capital**: {capital}")
    if clima:
        lines.append(f"- **Clima**: {clima}")
    if terreno:
        lines.append(f"- **Terreno**: {terreno}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Governo
    lines.append("## 🏛️ Governo e Política")
    gov_lines = []
    if governo:
        gov_lines.append(f"- **Tipo**: {governo}")
    if regente:
        gov_lines.append(f"- **Regente**: {regente}")
    if gentilic:
        gov_lines.append(f"- **Gentílico**: {gentilic}")
    if simbolo:
        gov_lines.append(f"- **Símbolo**: {simbolo}")
    if populacao:
        gov_lines.append(f"- **População**: {populacao}")
    if especies:
        gov_lines.append(f"- **Espécies**: {especies}")
    lines.extend(gov_lines)
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Cidade/Assentamento - use cultura_recursos content
    lines.append("## 🏙️ Cidade/Assentamento")
    if cultura_recursos:
        # Extract culture description (first part before **Recursos:**)
        cultura_part = re.split(r'\*\*Recursos:\*\*', cultura_recursos)[0]
        cultura_clean = clean_markdown(cultura_part)
        for line in cultura_clean.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                lines.append(f"- {line}")
    else:
        lines.append(f"- **Características**: {nome} — cultura única moldada pela geografia e história")
        lines.append(f"- **Layout**: Adaptado ao terreno e cultura local")
        lines.append(f"- **Atmosfera**: Única à região e povo")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Economia
    lines.append("## 💰 Economia e Recursos")
    if cultura_recursos:
        recursos_match = re.search(r'\*\*Recursos:\*\*(.*?)(?=\*\*|\n###|\n# |\Z)', cultura_recursos, re.DOTALL)
        if recursos_match:
            recursos_text = clean_markdown(recursos_match.group(1))
            lines.append(recursos_text)
        else:
            lines.append(f"- **Base**: Economia adaptada à geografia local")
            lines.append(f"- **Especializações**: Conforme cultura e recursos naturais")
    else:
        lines.append(f"- **Base**: Adaptada à geografia local (comércio, mineração, agricultura, magia, guerra)")
        lines.append(f"- **Especializações**: Conforme cultura e recursos naturais")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Vantagem Regional
    lines.append("## 🌟 Vantagem Regional")
    lines.append(f"> **Personagens nascidos em [{nome.lower()}]({wiki_file})**: *Vantagem Regional* (detalhes a extrair do ARCANO_COMPLETO.md).")
    lines.append(f"> *Nascer aqui molda corpo e mente conforme a terra.*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # NPCs Notáveis
    lines.append("## 👥 NPCs Notáveis")
    lines.append("| Nome | Papel | Detalhes |")
    lines.append("|------|-------|----------|")
    added_npcs = set()
    if regente:
        lines.append(f"| **{regente}** | Governante | {extract_field(section, 'Regente Detalhes') or 'Detalhes no ARCANO_COMPLETO.md'} |")
        added_npcs.add(regente.lower())
    if faccoes:
        # Extract NPC names from faction section
        npc_matches = re.findall(r'\*\*([^*]+)\*\*\s*[:\-]?\s*([^\n]+)', faccoes)
        for npc_name, npc_role in npc_matches[:8]:
            npc_name_clean = npc_name.strip()
            if len(npc_name_clean) > 2 and npc_name_clean.lower() not in added_npcs:
                role_clean = npc_role.strip()[:80]
                lines.append(f"| **{npc_name_clean}** | {role_clean} | Detalhes no ARCANO_COMPLETO.md |")
                added_npcs.add(npc_name_clean.lower())
    if len(lines) == 6:  # Only header rows
        lines.append("| **Líder Local** | Governante | Detalhes no ARCANO_COMPLETO.md |")
        lines.append("| **Figura Notável** | Papel-chave | Detalhes no ARCANO_COMPLETO.md |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Pontos de Interesse
    lines.append("## 🗺️ Pontos de Interesse")
    lines.append("| Local | Descrição |")
    lines.append("|-------|-----------|")
    if topografia:
        landmark_matches = re.findall(r'\*\*([^*]+)\*\*\s*[:\-]\s*([^\n]+)', topografia)
        for lm_name, lm_desc in landmark_matches[:8]:
            lines.append(f"| **{lm_name.strip()}** | {lm_desc.strip()} |")
    if len(lines) == 3:  # Only header rows
        lines.append("| **Centro Principal** | Coração político/cultural/econômico |")
        lines.append("| **Marco Geográfico** | Característica única da região |")
        lines.append("| **Local Sagrado/Histórico** | Importância cultural/religiosa |")
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
    if faccoes:
        hooks.insert(2, "3. **Intriga de Facção** — Facções locais disputam influência; PCs podem mediar ou explorar")
    for hook in hooks:
        lines.append(hook)
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # História Recente
    lines.append("## 📜 História Recente")
    if historia:
        lines.append(clean_markdown(historia[:3000]))
    else:
        lines.append(f"- **Fundação/Origem**: {fundacao or 'Antiga ou expansão imperial'}")
        lines.append(f"- **Eventos-chave**: Guerras, tratados, cataclismos, mudanças de poder")
        lines.append(f"- **Atual**: Situação política/militar atual; tensões ativas")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Vantagem Regional (repeated at end as in template)
    lines.append("## 🌟 Vantagem Regional")
    lines.append(f"> **Personagens nascidos em [{nome.lower()}]({wiki_file})**: *Vantagem Regional* (detalhes a extrair do ARCANO_COMPLETO.md).")
    lines.append(f"> *Nascer aqui molda corpo e mente conforme a terra.*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Links Relacionados
    lines.append("## 🔗 Links Relacionados")
    lines.append(f"- [Índice dos Reinos](index.md) — Volta ao índice mestre")
    lines.append(f"- [Império de Aba](../imperio-aba.md) — Contexto imperial (se aplica)")
    if regiao:
        lines.append(f"- [Região: {regiao}](../geografia/regioes/index.md) — Contexto geográfico maior")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"> *Página populada a partir do ARCANO_COMPLETO.md — revise e complete*")
    
    return '\n'.join(lines)

def main():
    print("Loading ARCANO_COMPLETO.md...")
    kingdom_content = load_arcano()
    print(f"Found content for {len(kingdom_content)} kingdoms")
    
    for wiki_file, section in kingdom_content.items():
        print(f"Generating {wiki_file}...")
        page_content = build_wiki_page(wiki_file, section)
        file_path = WIKI_REINOS_DIR / wiki_file
        file_path.write_text(page_content, encoding='utf-8')
        print(f"  Written: {file_path}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()