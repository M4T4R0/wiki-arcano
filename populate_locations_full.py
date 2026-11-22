#!/usr/bin/env python3
"""
Extract ALL kingdom content from ARCANO_COMPLETO.md and populate docs/locations/*.md
"""

import re
from pathlib import Path

ARCANO_PATH = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/ARCANO_COMPLETO.md")
LOCATIONS_DIR = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/locations")

# All 30 kingdoms with their search terms in ARCANO_COMPLETO.md
KINGDOMS = {
    "ypy.md": ["Ypy", "Capital do Império"],
    "kise.md": ["Kisé", "Norvaen", "Irundyna"],
    "moacuba.md": ["Moacuba"],
    "aratama.md": ["Aratama"],
    "aiso.md": ["Aisó"],
    "camua.md": ["Camuá"],
    "jurubatiba.md": ["Jurubatiba", "Dragnovith Uller"],
    "kaluana.md": ["Kaluana"],
    "nambiquara.md": ["Nambiquara"],
    "ypiturui.md": ["Ypiturui"],
    "sam-mael.md": ["Sam-Mael", "Sam Mael"],
    "elfin.md": ["Elfin"],
    "andira.md": ["Andirá"],
    "fortuna.md": ["Fortuna"],
    "naurush.md": ["Naur'Ush", "Naurush"],
    "terra-selvagem.md": ["Terra Selvagem"],
    "terras-auca.md": ["Terras dos Auçás", "Terras dos Auçá"],
    "tiba.md": ["Tiba"],
    "ybi.md": ["Ybi"],
    "yby.md": ["Yby"],
    "ybytu.md": ["Ybytu"],
    "yu.md": ["Yu"],
    "acag.md": ["Acag", "Arquipélago Acag", "Yawara"],
    "lande.md": ["Landé"],
    "mbae.md": ["Mbaê"],
    "arani.md": ["Arani"],
    "avista.md": ["Avista"],
    "araxa.md": ["Araxá"],
    "irundyna.md": ["Irundyna"],
}

def load_arcano():
    return ARCANO_PATH.read_text(encoding='utf-8')

def extract_kingdom_section(content, kingdom_name, search_terms):
    """Extract the full section for a kingdom from ARCANO_COMPLETO.md"""
    # Find the main heading for this kingdom
    # Look for # **Name** or similar
    pattern = rf'^# \*\*({re.escape(kingdom_name)}[^*]*)\*\*'
    matches = list(re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE))
    
    if not matches:
        # Try alternative patterns
        for term in search_terms:
            pattern = rf'^# \*\*({re.escape(term)}[^*]*)\*\*'
            matches = list(re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE))
            if matches:
                break
    
    if not matches:
        return None
    
    # Get the section content (from this heading to next # **)
    start = matches[0].start()
    
    # Find next major heading
    next_headings = list(re.finditer(r'^# \*\*', content[start+1:], re.MULTILINE))
    if next_headings:
        end = start + 1 + next_headings[0].start()
    else:
        end = len(content)
    
    section = content[start:end]
    return section.strip()

def extract_all_mentions(content, search_terms):
    """Extract all paragraphs mentioning the kingdom (for timeline/history)"""
    paragraphs = re.split(r'\n\n+', content)
    mentions = []
    for para in paragraphs:
        para_lower = para.lower()
        for term in search_terms:
            if term.lower() in para_lower and len(para.strip()) > 100:
                mentions.append(para.strip())
                break
    return mentions[:20]  # Limit

def build_kingdom_page(kingdom_file, kingdom_name, search_terms, arcano_content):
    """Build a complete kingdom page from ARCANO content"""
    
    # Extract main section
    main_section = extract_kingdom_section(arcano_content, kingdom_name, search_terms)
    
    # Extract mentions for history/timeline
    mentions = extract_all_mentions(arcano_content, search_terms)
    
    # Build page
    lines = []
    lines.append(f"# {kingdom_name}")
    lines.append("")
    
    # Basic info header
    lines.append(f"> **Região**: [A DEFINIR] | **Fundação**: [A DEFINIR] | **Clima**: [A DEFINIR]")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    if main_section:
        # Clean up the section
        lines.append("## 📜 Conteúdo Original do ARCANO_COMPLETO.md")
        lines.append("")
        lines.append(main_section)
        lines.append("")
    else:
        lines.append("## 📜 Lore e História")
        lines.append("")
        lines.append("*Conteúdo a extrair do ARCANO_COMPLETO.md*")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Add mentions as history/timeline
    if mentions:
        lines.append("## 📜 História e Menções no Livro")
        lines.append("")
        for mention in mentions[:10]:
            # Truncate long mentions
            clean = re.sub(r'\s+', ' ', mention).strip()
            if len(clean) > 500:
                clean = clean[:500] + "..."
            lines.append(f"> {clean}")
            lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Standard sections
    lines.append("## 📍 Localização")
    lines.append("- **Região**: [A DEFINIR]")
    lines.append("- **Coordenadas**: [A DEFINIR]")
    lines.append("- **Clima**: [A DEFINIR]")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🏛️ Governo e Política")
    lines.append("- **Tipo**: [A DEFINIR]")
    lines.append("- **Regente**: [A DEFINIR]")
    lines.append("- **Gentílico**: [A DEFINIR]")
    lines.append("- **População**: [A DEFINIR]")
    lines.append("- **Espécies**: [A DEFINIR]")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🏙️ Cidade/Assentamento")
    lines.append("- **Características**: [A DEFINIR]")
    lines.append("- **Layout**: [A DEFINIR]")
    lines.append("- **Atmosfera**: [A DEFINIR]")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 💰 Economia e Recursos")
    lines.append("- **Base**: [A DEFINIR]")
    lines.append("- **Especializações**: [A DEFINIR]")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🌟 Vantagem Regional")
    lines.append(f"> **Personagens nascidos em [{kingdom_name.lower()}]**({kingdom_file}): *Vantagem Regional* (detalhes a extrair do ARCANO_COMPLETO.md).")
    lines.append(f"> *Nascer aqui molda corpo e mente conforme a terra.*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 👥 NPCs Notáveis")
    lines.append("| Nome | Papel | Detalhes |")
    lines.append("|------|-------|----------|")
    lines.append("| **Líder Local** | Governante | Detalhes no ARCANO_COMPLETO.md |")
    lines.append("| **Figura Notável** | Papel-chave | Detalhes no ARCANO_COMPLETO.md |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🗺️ Pontos de Interesse")
    lines.append("| Local | Descrição |")
    lines.append("|-------|-----------|")
    lines.append("| **Centro Principal** | Coração político/cultural/econômico |")
    lines.append("| **Marco Geográfico** | Característica única da região |")
    lines.append("| **Local Sagrado/Histórico** | Importância cultural/religiosa |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
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
    
    lines.append("## 📜 História Recente")
    lines.append("- **Fundação/Origem**: [A DEFINIR]")
    lines.append("- **Eventos-chave**: Guerras, tratados, cataclismos, mudanças de poder")
    lines.append("- **Atual**: Situação política/militar atual; tensões ativas")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🌟 Vantagem Regional")
    lines.append(f"> **Personagens nascidos em [{kingdom_name.lower()}]**({kingdom_file}): *Vantagem Regional* (detalhes a extrair do ARCANO_COMPLETO.md).")
    lines.append(f"> *Nascer aqui molda corpo e mente conforme a terra.*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🔗 Links Relacionados")
    lines.append(f"- [Índice dos Reinos](../factions/reinos/index.md) — Volta ao índice mestre")
    lines.append(f"- [Império de Aba](../factions/imperio-aba.md) — Contexto imperial (se aplica)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"> *Página populada a partir do ARCANO_COMPLETO.md — revise e complete*")
    
    return '\n'.join(lines)

def main():
    print("Loading ARCANO_COMPLETO.md...")
    arcano_content = load_arcano()
    print(f"Loaded {len(arcano_content)} characters")
    
    for kingdom_file, search_terms in KINGDOMS.items():
        kingdom_name = search_terms[0]  # First term is the display name
        print(f"Generating {kingdom_file} ({kingdom_name})...")
        
        page_content = build_kingdom_page(kingdom_file, kingdom_name, search_terms, arcano_content)
        file_path = LOCATIONS_DIR / kingdom_file
        file_path.write_text(page_content, encoding='utf-8')
        print(f"  Written: {file_path} ({len(page_content)} chars)")
    
    print("\nDone!")

if __name__ == "__main__":
    main()