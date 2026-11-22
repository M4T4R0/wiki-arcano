#!/usr/bin/env python3
"""
Extract ALL NPC content from ARCANO_COMPLETO.md and populate docs/npcs/individual/*.md
Precise extraction: finds the specific NPC subsection within "Personalidades Notáveis"
"""

import re
from pathlib import Path

ARCANO_PATH = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/ARCANO_COMPLETO.md")
NPCS_DIR = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/npcs/individual")

# NPCs with their exact display names and search patterns
NPCS = {
    "ahriman-arcano-da-destruicao.md": {"name": "AHRIMAM Arqui Mestre dos Arcanos Imperiais", "terms": ["AHRIMAM", "Ahrimam", "Arqui Mestre"]},
    "antarius-gram-mestre.md": {"name": "ANTARIUS, Gram Mestre da Ordem dos Arcanos Imperiais", "terms": ["ANTARIUS", "Gram Mestre", "Arcano da Esperança"]},
    "morbius-lich.md": {"name": "MORBIUS, O Lich", "terms": ["MORBIUS", "Lich", "Arcano do Deslocamento"]},
    "ignatius-arcano-da-coragem.md": {"name": "IGNATIUS, o Arcano da Coragem, o Primeiro Necromecha", "terms": ["IGNATIUS", "Arcano da Coragem", "Primeiro Necromecha"]},
    "misty-as-la.md": {"name": "MISTY AS-LA", "terms": ["MISTY AS-LA", "M.A.L.", "MAL", "Misty As'La"]},
    "vlad-dracul.md": {"name": "VLAD DRACUL O MAGO DAS TREVAS VAMPIRO", "terms": ["VLAD DRACUL", "Vlad Dracul"]},
    "azeron.md": {"name": "AZERON (Rasyl Azeron Dellarier)", "terms": ["Azeron", "Rasyl Azeron", "Horripilus Belmonte", "Benedito Salvador"]},
    "sani-dellarier.md": {"name": "Sani Dellarier", "terms": ["Sani Dellarier", "Sani"]},
    "mordigueiro.md": {"name": "Mordigueiro", "terms": ["Mordigueiro"]},
    "marmana.md": {"name": "Senhora Marmana", "terms": ["Senhora Marmana", "Marmana"]},
    "charles.md": {"name": "Charles", "terms": ["Charles", "Mago do Abstrato"]},
    "meri.md": {"name": "Meri", "terms": ["Meri", "Intocável"]},
    "murilo.md": {"name": "Murilo", "terms": ["Murilo"]},
    "razar-dafar.md": {"name": "Razar e Dafar", "terms": ["Razar", "Dafar"]},
    "sir-habbor.md": {"name": "Sir Habbor", "terms": ["Sir Habbor"]},
    "capelobo.md": {"name": "Capelobo", "terms": ["Capelobo"]},
    "durell-azeron.md": {"name": "Durell Azeron", "terms": ["Durell Azeron", "Durell", "Último Suspiro"]},
    "carolaine-azeron.md": {"name": "Carolaine Azeron Dellarier", "terms": ["Carolaine", "Carolaine Azeron"]},
    "pai-de-azeron.md": {"name": "Pai de Azeron", "terms": ["Pai de Azeron"]},
    "avo-de-azeron.md": {"name": "Avô de Azeron", "terms": ["Avô de Azeron"]},
    "vekann.md": {"name": "Vekann", "terms": ["Vekann", "Lich", "Arquivista Cego"]},
    "irial.md": {"name": "Irial", "terms": ["Irial", "Alta-Maga", "Conselheira"]},
    "deziel-aureo.md": {"name": "Deziel Áureo", "terms": ["Deziel Áureo", "Imperador", "Deziel Áureo XIV"]},
    "vaelyn.md": {"name": "Vaelyn", "terms": ["Vaelyn", "Vaelyn As La"]},
    "mal-entidade.md": {"name": "Mal", "terms": ["Mal", "O Mal", "MAL"]},
    "eligos-duque-inferno.md": {"name": "Eligos", "terms": ["Eligos", "Primeiro Duque do Inferno"]},
    "vulcazar.md": {"name": "Vulcazar", "terms": ["Vulcazar", "Meio-Dragão Meio-Orc"]},
    "fawkes.md": {"name": "Fawkes", "terms": ["Fawkes", "Garem Fawkes"]},
    "garem.md": {"name": "Garem", "terms": ["Garem", "Garem Fawkes"]},
    "sani-dellarier.md": {"name": "Sani Dellarier", "terms": ["Sani Dellarier", "Sani"]},
    "mordigueiro.md": {"name": "Mordigueiro", "terms": ["Mordigueiro"]},
    "sir-habbor.md": {"name": "Sir Habbor", "terms": ["Sir Habbor"]},
    "capelobo.md": {"name": "Capelobo", "terms": ["Capelobo"]},
    "durell-azeron.md": {"name": "Durell Azeron", "terms": ["Durell Azeron"]},
    "carolaine-azeron.md": {"name": "Carolaine Azeron", "terms": ["Carolaine", "Carolaine Azeron"]},
    "pai-de-azeron.md": {"name": "Pai de Azeron", "terms": ["Pai de Azeron"]},
    "avo-de-azeron.md": {"name": "Avô de Azeron", "terms": ["Avô de Azeron"]},
    "vekann.md": {"name": "Vekann", "terms": ["Vekann"]},
    "irial.md": {"name": "Irial", "terms": ["Irial", "Alta-Maga"]},
    "deziel-aureo.md": {"name": "Deziel Áureo", "terms": ["Deziel Áureo", "Imperador"]},
    "vaelyn.md": {"name": "Vaelyn", "terms": ["Vaelyn"]},
    "mal-entidade.md": {"name": "Mal", "terms": ["Mal", "MAL"]},
    "eligos.md": {"name": "Eligos", "terms": ["Eligos", "Duque do Inferno"]},
    "vulcazar.md": {"name": "Vulcazar", "terms": ["Vulcazar"]},
    "fawkes.md": {"name": "Fawkes", "terms": ["Fawkes", "Garem Fawkes"]},
    "garem.md": {"name": "Garem", "terms": ["Garem"]},
    "sani.md": {"name": "Sani", "terms": ["Sani"]},
    "durell.md": {"name": "Durell", "terms": ["Durell"]},
    "carolaine.md": {"name": "Carolaine", "terms": ["Carolaine"]},
    "pai-azeron.md": {"name": "Pai de Azeron", "terms": ["Pai de Azeron"]},
    "avo-azeron.md": {"name": "Avô de Azeron", "terms": ["Avô de Azeron"]},
    "imperador-deziel-aureo.md": {"name": "Imperador Deziel Áureo", "terms": ["Imperador Deziel Áureo", "Deziel Áureo", "Deziel Áureo XIV"]},
    "arthur-aureo.md": {"name": "Arthur Áureo", "terms": ["Arthur Áureo", "Áureo II"]},
    "aureo-i.md": {"name": "Áureo I", "terms": ["Áureo I", "Fundador do Império"]},
    "luna-lin.md": {"name": "Luna Lin", "terms": ["Luna Lin", "Amazona"]},
    "huck-hor.md": {"name": "Huck Hor", "terms": ["Huck Hor", "Comandante da Cavalaria"]},
    "dragnovith-uller.md": {"name": "Dragnovith Uller", "terms": ["Dragnovith Uller", "Arquimago Imperial"]},
    "stigin-nato.md": {"name": "Stigin Nato", "terms": ["Stigin Nato", "Taverneiro"]},
    "sucelus.md": {"name": "Sucelus", "terms": ["Sucelus"]},
    "ror-general.md": {"name": "Ror", "terms": ["Ror", "General", "Ror General"]},
    "mictian-auca.md": {"name": "Mictian", "terms": ["Mictian", "Rei Auçá"]},
    "sidius-acemira.md": {"name": "Sidius Acemira", "terms": ["Sidius", "Acemira", "Sidius Acemira"]},
    "belero-leroy.md": {"name": "Belero Leroy", "terms": ["Belero", "Leroy", "Oráculo de Moá", "Mago Vampiro"]},
    "baley-ell.md": {"name": "Baley Ell", "terms": ["Baley Ell", "Curandeiro do Imperador"]},
    "purpleskull-arc.md": {"name": "Purpleskull Arc", "terms": ["Purpleskull Arc", "Mestre das Sombras"]},
    "stigin-nato.md": {"name": "Stigin Nato", "terms": ["Stigin Nato"]},
    "karnos-minor.md": {"name": "Karnos Minor", "terms": ["Karnos Minor", "Faraó de Ybi"]},
    "elros-palantir.md": {"name": "Elros Palantír", "terms": ["Elros Palantír", "Mago Glacial", "Abaré"]},
    "escuridao.md": {"name": "Escuridão", "terms": ["Escuridão", "Entidade da Infestação"]},
    "faraos-ybi.md": {"name": "Faraós de Ybi", "terms": ["Faraós de Ybi", "Faraós"]},
    "guarda-aca.md": {"name": "Guarda Açã", "terms": ["Guarda Açã", "Guarda Aca"]},
    "homem-leao.md": {"name": "Homem Leão", "terms": ["Homem Leão"]},
    "meio-elfos-cacadores.md": {"name": "Meio-Elfos Caçadores", "terms": ["Meio-Elfos Caçadores", "Caçadores de Magos"]},
    "misty-as-la-arquimago.md": {"name": "Misty As-La", "terms": ["Misty As-La", "Arquimago"]},
    "paladinos-aiso.md": {"name": "Paladinos de Aisó", "terms": ["Paladinos de Aisó", "Templários"]},
    "arthur-aureo-general.md": {"name": "Arthur Áureo", "terms": ["Arthur Áureo", "General Imperador"]},
    "aureo-i-fundador.md": {"name": "Áureo I", "terms": ["Áureo I", "Fundador do Império"]},
    "luna-lin-amazona.md": {"name": "Luna Lin", "terms": ["Luna Lin", "Amazona"]},
    "huck-hor-comandante.md": {"name": "Huck Hor", "terms": ["Huck Hor", "Comandante da Cavalaria"]},
    "dragnovith-uller-arquimago.md": {"name": "Dragnovith Uller", "terms": ["Dragnovith Uller", "Arquimago Imperial"]},
    "elros-palantir-mago-glacial.md": {"name": "Elros Palantír", "terms": ["Elros Palantír", "Mago Glacial", "Abaré"]},
    "escuridao.md": {"name": "Escuridão", "terms": ["Escuridão", "Entidade da Infestação"]},
    "faraos-ybi.md": {"name": "Faraós de Ybi", "terms": ["Faraós de Ybi"]},
    "guarda-aca.md": {"name": "Guarda Açã", "terms": ["Guarda Açã"]},
    "homem-leao.md": {"name": "Homem Leão", "terms": ["Homem Leão"]},
    "meio-elfos-cacadores.md": {"name": "Meio-Elfos Caçadores", "terms": ["Meio-Elfos Caçadores"]},
    "misty-as-la-arquimago.md": {"name": "Misty As-La", "terms": ["Misty As-La", "Arquimago"]},
    "paladinos-aiso.md": {"name": "Paladinos de Aisó", "terms": ["Paladinos de Aisó"]},
    "arthur-aureo-general.md": {"name": "Arthur Áureo", "terms": ["Arthur Áureo", "General"]},
    "aureo-i-fundador.md": {"name": "Áureo I", "terms": ["Áureo I", "Fundador"]},
    "luna-lin-amazona.md": {"name": "Luna Lin", "terms": ["Luna Lin"]},
    "huck-hor-comandante.md": {"name": "Huck Hor", "terms": ["Huck Hor"]},
    "dragnovith-uller-arquimago.md": {"name": "Dragnovith Uller", "terms": ["Dragnovith Uller"]},
    "elros-palantir-mago-glacial.md": {"name": "Elros Palantír", "terms": ["Elros Palantír"]},
    "escuridao-entidade.md": {"name": "Escuridão", "terms": ["Escuridão", "Entidade"]},
    "misty-as-la-possivel-mal.md": {"name": "Misty As-La", "terms": ["Misty As-La", "Possível Mal"]},
    "sidius-acemira-auca.md": {"name": "Sidius Acemira", "terms": ["Sidius", "Acemira", "Auçá"]},
    "karnos-minor-arquimago.md": {"name": "Karnos Minor", "terms": ["Karnos Minor", "Arquimago", "Faraó"]},
}

def load_arcano():
    return ARCANO_PATH.read_text(encoding='utf-8')

def extract_npc_section(content, npc_data):
    """Extract the precise NPC subsection from 'Personalidades Notáveis'"""
    display_name = npc_data["name"]
    terms = npc_data["terms"]
    
    # First, find the "Personalidades Notáveis" section
    pessoais_start = content.find("# **Personalidades Notáveis**")
    if pessoais_start == -1:
        return ""
    
    # Find the end of this section (next major heading)
    next_heading = content.find("\n# **", pessoais_start + 1)
    if next_heading == -1:
        pessoais_section = content[pessoais_start:]
    else:
        pessoais_section = content[pessoais_start:next_heading]
    
    # Now find the specific NPC within this section
    # Look for **NAME** pattern (bold uppercase name)
    best_section = ""
    best_score = 0
    
    # Split by bold uppercase names (NPC headers)
    npc_pattern = r'\n\*\*([A-ZÁÉÍÓÚÂÊÔÃÕÇ\s\.\,\-\']+)\*\*'
    matches = list(re.finditer(npc_pattern, pessoais_section))
    
    for i, match in enumerate(matches):
        npc_header = match.group(1).strip()
        start = match.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(pessoais_section)
        section_text = pessoais_section[start:end].strip()
        
        # Score this section against our search terms
        score = 0
        section_lower = section_text.lower()
        for term in npc_data["terms"]:
            if term.lower() in section_lower:
                score += section_lower.count(term.lower()) * len(term)
        
        # Bonus if the header matches the display name closely
        if display_name.upper() in npc_header.upper():
            score += 1000
        
        if score > best_score:
            best_score = score
            best_section = section_text
    
    # If still no good match, try the whole section with term scoring
    if best_score < 50:
        # Fallback: score the whole section
        for term in npc_data["terms"]:
            if term.lower() in pessoais_section.lower():
                return pessoais_section[:15000]  # Limit size
    
    return best_section if best_section else ""

def build_npc_page(npc_file, npc_data, arcano_content):
    """Build a complete NPC page from ARCANO content"""
    
    display_name = npc_data["name"]
    section = extract_npc_section(arcano_content, npc_data)
    
    lines = []
    lines.append(f"# {display_name}")
    lines.append("")
    lines.append(f"> **NPC de Arcano** — {display_name}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    if section:
        lines.append("## 📜 Conteúdo Original do ARCANO_COMPLETO.md")
        lines.append("")
        lines.append(section.strip())
        lines.append("")
    else:
        lines.append("## 📜 Lore e História")
        lines.append("")
        lines.append("*Conteúdo a extrair do ARCANO_COMPLETO.md*")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Standard sections
    lines.append("## 👤 Ficha do Personagem")
    lines.append("")
    lines.append("| Atributo | Valor |")
    lines.append("|----------|-------|")
    lines.append(f"| **Nome** | {display_name} |")
    lines.append("| **Raça** | [A DEFINIR] |")
    lines.append("| **Classe/Kit** | [A DEFINIR] |")
    lines.append("| **Origem** | [A DEFINIR] |")
    lines.append("| **Afiliação** | [A DEFINIR] |")
    lines.append("| **Nível Sugerido** | [A DEFINIR] |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## ⚔️ Mecânicas 3D&T Sugeridas")
    lines.append("")
    lines.append("### Atributos Base")
    lines.append("")
    lines.append("| Atributo | Valor |")
    lines.append("|----------|-------|")
    lines.append("| **Força** | [A DEFINIR] |")
    lines.append("| **Habilidade** | [A DEFINIR] |")
    lines.append("| **Resistência** | [A DEFINIR] |")
    lines.append("| **Armadura** | [A DEFINIR] |")
    lines.append("| **Poder de Fogo** | [A DEFINIR] |")
    lines.append("")
    
    lines.append("### Vantagens Sugeridas")
    lines.append("- [A DEFINIR]")
    lines.append("")
    
    lines.append("### Desvantagens Sugeridas")
    lines.append("- [A DEFINIR]")
    lines.append("")
    
    lines.append("---")
    lines.append("")
    
    lines.append("## 🎒 Equipamento Notável")
    lines.append("- [A DEFINIR]")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🎯 Ganchos de Aventura")
    display = display_name
    hooks = [
        f"1. **Encontro** — PCs cruzam com {display}; conversa revela segredo",
        f"2. **Missão** — {display} contrata PCs para tarefa perigosa",
        f"3. **Conflito** — {display} é antagonista/aliado central",
        f"4. **Segredo** — {display} guarda informação vital",
        f"5. **Legado** — Após morte/desaparecimento, herança cai nas mãos dos PCs",
    ]
    for hook in hooks:
        lines.append(hook)
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🔗 Links Relacionados")
    lines.append(f"- [Índice de NPCs](index.md) — Volta ao índice")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"> *Página populada a partir do ARCANO_COMPLETO.md — revise e complete*")
    
    return '\n'.join(lines)

def main():
    print("Loading ARCANO_COMPLETO.md...")
    arcano_content = load_arcano()
    print(f"Loaded {len(arcano_content)} characters")
    
    # Deduplicate by filename
    seen = {}
    for fname, data in NPCS.items():
        if fname not in seen:
            seen[fname] = data
        else:
            # Merge terms
            seen[fname]["terms"].extend(data["terms"])
    
    for npc_file, npc_data in seen.items():
        display_name = npc_data["name"]
        print(f"Generating {npc_file} ({display_name})...")
        
        page_content = build_npc_page(npc_file, npc_data, arcano_content)
        file_path = NPCS_DIR / npc_file
        file_path.write_text(page_content, encoding='utf-8')
        print(f"  Written: {file_path} ({len(page_content)} chars)")
    
    print("\nDone!")

if __name__ == "__main__":
    main()