#!/usr/bin/env python3
"""
Extract ALL NPC content from ARCANO_COMPLETO.md and populate docs/npcs/individual/*.md
"""

import re
from pathlib import Path

ARCANO_PATH = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/ARCANO_COMPLETO.md")
NPCS_DIR = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/npcs/individual")

# All NPCs with their search terms in ARCANO_COMPLETO.md
NPCS = {
    "ahriman-arcano-da-destruicao.md": ["Ahriman", "Ahrimam", "Arcano da Destruição", "Arqui Mestre dos Arcanos"],
    "antarius-gram-mestre.md": ["Antarius", "Gram Mestre", "Arcano da Esperança"],
    "morbius-lich.md": ["Morbius", "Lich", "Arcano do Deslocamento"],
    "ignatius-arcano-da-coragem.md": ["Ignatius", "Arcano da Coragem", "Primeiro Necromecha"],
    "misty-as-la.md": ["Misty As-La", "M.A.L.", "MAL", "Misty As'La"],
    "vlad-dracul.md": ["Vlad Dracul", "Vlad Dracul o Mago das Trevas Vampiro"],
    "azeron.md": ["Azeron", "Rasyl Azeron Dellarier", "Horripilus Belmonte", "Benedito Salvador"],
    "sani-dellarier.md": ["Sani Dellarier", "Sani"],
    "mordigueiro.md": ["Mordigueiro"],
    "marmana.md": ["Senhora Marmana", "Marmana"],
    "charles.md": ["Charles", "Mago do Abstrato"],
    "meri.md": ["Meri", "Intocável"],
    "murilo.md": ["Murilo"],
    "razar-dafar.md": ["Razar", "Dafar"],
    "sir-habbor.md": ["Sir Habbor"],
    "capelobo.md": ["Capelobo"],
    "durell-azeron.md": ["Durell Azeron", "Durell", "Último Suspiro"],
    "carolaine-azeron.md": ["Carolaine Azeron Dellarier", "Carolaine"],
    "pai-de-azeron.md": ["Pai de Azeron"],
    "avo-de-azeron.md": ["Avô de Azeron", "Durell", "Último Suspiro"],
    "vekann.md": ["Vekann", "Lich", "Arquivista Cego"],
    "irial.md": ["Irial", "Alta-Maga", "Conselheira"],
    "deziel-aureo.md": ["Deziel Áureo", "Imperador", "Deziel Áureo XIV"],
    "vaelyn.md": ["Vaelyn", "Vaelyn As La"],
    "mal-entidade.md": ["Mal", "O Mal", "MAL"],
    "eligos-duque-inferno.md": ["Eligos", "Primeiro Duque do Inferno"],
    "vulcazar.md": ["Vulcazar", "Meio-Dragão Meio-Orc"],
    "fawkes.md": ["Fawkes", "Garem Fawkes"],
    "garem.md": ["Garem", "Garem Fawkes"],
    "sani-dellarier.md": ["Sani Dellarier"],
    "mordigueiro.md": ["Mordigueiro"],
    "sir-habbor.md": ["Sir Habbor"],
    "capelobo.md": ["Capelobo"],
    "durell-azeron.md": ["Durell Azeron"],
    "carolaine-azeron.md": ["Carolaine Azeron"],
    "pai-de-azeron.md": ["Pai de Azeron"],
    "avo-de-azeron.md": ["Avô de Azeron"],
    "vekann.md": ["Vekann"],
    "irial.md": ["Irial"],
    "deziel-aureo.md": ["Deziel Áureo", "Imperador"],
    "vaelyn.md": ["Vaelyn"],
    "mal-entidade.md": ["Mal", "MAL"],
    "eligos.md": ["Eligos"],
    "vulcazar.md": ["Vulcazar"],
    "fawkes.md": ["Fawkes"],
    "garem.md": ["Garem"],
    "sani.md": ["Sani"],
    "mordigueiro.md": ["Mordigueiro"],
    "sir-habbor.md": ["Sir Habbor"],
    "capelobo.md": ["Capelobo"],
    "durell.md": ["Durell"],
    "carolaine.md": ["Carolaine"],
    "pai-azeron.md": ["Pai de Azeron"],
    "avo-azeron.md": ["Avô de Azeron"],
    "imperador-deziel-aureo.md": ["Imperador Deziel Áureo", "Deziel Áureo", "Deziel Áureo XIV"],
    "arthur-aureo.md": ["Arthur Áureo", "Áureo II"],
    "aureo-i.md": ["Áureo I", "Fundador do Império"],
    "luna-lin.md": ["Luna Lin", "Amazona"],
    "huck-hor.md": ["Huck Hor", "Comandante da Cavalaria"],
    "dragnovith-uller.md": ["Dragnovith Uller", "Arquimago Imperial"],
    "stigin-nato.md": ["Stigin Nato", "Taverneiro"],
    "sucelus.md": ["Sucelus"],
    "ror-general.md": ["Ror", "General", "Ror General"],
    "mictian-auca.md": ["Mictian", "Rei Auçá"],
    "sidius-acemira.md": ["Sidius", "Acemira", "Sidius Acemira"],
    "belero-leroy.md": ["Belero", "Leroy", "Oráculo de Moá", "Mago Vampiro"],
    "baley-ell.md": ["Baley Ell", "Curandeiro do Imperador"],
    "purpleskull-arc.md": ["Purpleskull Arc", "Mestre das Sombras"],
    "stigin-nato.md": ["Stigin Nato"],
    "karnos-minor.md": ["Karnos Minor", "Faraó de Ybi"],
    "elros-palantir.md": ["Elros Palantír", "Mago Glacial", "Abaré"],
    "escuridao.md": ["Escuridão", "Entidade da Infestação"],
    "faraos-ybi.md": ["Faraós de Ybi", "Faraós"],
    "guarda-aca.md": ["Guarda Açã", "Guarda Aca"],
    "homem-leao.md": ["Homem Leão", "Líder dos Yawara"],
    "meio-elfos-cacadores.md": ["Meio-Elfos Caçadores", "Caçadores de Magos"],
    "misty-as-la-arquimago.md": ["Misty As-La", "Arquimago Possível Mal"],
    "paladinos-aiso.md": ["Paladinos de Aisó", "Templários"],
    "arthur-aureo-general.md": ["Arthur Áureo", "General Imperador"],
    "aureo-i-fundador.md": ["Áureo I", "Fundador do Império"],
    "luna-lin-amazona.md": ["Luna Lin", "Amazona"],
    "huck-hor-comandante.md": ["Huck Hor", "Comandante da Cavalaria"],
    "dragnovith-uller-arquimago.md": ["Dragnovith Uller", "Arquimago Imperial"],
    "elros-palantir-mago-glacial.md": ["Elros Palantír", "Mago Glacial", "Abaré"],
    "escuridao-entidade.md": ["Escuridão", "Entidade da Infestação"],
    "faraos-ybi.md": ["Faraós de Ybi"],
    "guarda-aca.md": ["Guarda Açã"],
    "homem-leao.md": ["Homem Leão"],
    "meio-elfos-cacadores.md": ["Meio-Elfos Caçadores"],
    "misty-as-la-possivel-mal.md": ["Misty As-La", "Possível Mal"],
    "paladinos-aiso.md": ["Paladinos de Aisó"],
    "sidius-acemira-auca.md": ["Sidius Acemira", "Acemira", "Auçá"],
    "vlad-dracul.md": ["Vlad Dracul"],
    "karnos-minor-arquimago.md": ["Karnos Minor", "Arquimago"],
}

# Deduplicate by filename
NPCS_DEDUP = {}
for fname, terms in NPCS.items():
    if fname not in NPCS_DEDUP:
        NPCS_DEDUP[fname] = terms
    else:
        NPCS_DEDUP[fname].extend(terms)

def load_arcano():
    return ARCANO_PATH.read_text(encoding='utf-8')

def extract_npc_section(content, search_terms):
    """Extract the full section for an NPC from ARCANO_COMPLETO.md"""
    best_section = ""
    best_score = 0
    
    # Split by major headings
    sections = re.split(r'\n(?=# \*\*[^*]+\*\*)', content)
    
    for section in sections:
        score = 0
        section_lower = section.lower()
        for term in search_terms:
            if term.lower() in section_lower:
                score += section_lower.count(term.lower()) * len(term)
        if score > best_score:
            best_score = score
            best_section = section
    
    if best_score < 50:
        # Try searching in paragraphs
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
    
    return best_section if best_score >= 50 else ""

def build_npc_page(npc_file, display_name, search_terms, arcano_content):
    """Build a complete NPC page from ARCANO content"""
    
    section = extract_npc_section(arcano_content, search_terms)
    
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
    lines.append("| **Nome** | " + display_name + " |")
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
    hooks = [
        "1. **Encontro** — PCs cruzam com " + display_name + "; conversa revela segredo",
        "2. **Missão** — " + display_name + " contrata PCs para tarefa perigosa",
        "3. **Conflito** — " + display_name + " é antagonista/aliado central",
        "4. **Segredo** — " + display_name + " guarda informação vital",
        "5. **Legado** — Após morte/desaparecimento, herança cai nas mãos dos PCs",
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
    
    for npc_file, search_terms in NPCS_DEDUP.items():
        # Use first term as display name
        display_name = search_terms[0].replace("-", " ").title()
        if "md" in display_name.lower():
            display_name = search_terms[1].replace("-", " ").title() if len(search_terms) > 1 else display_name
        
        print(f"Generating {npc_file} ({display_name})...")
        
        page_content = build_npc_page(npc_file, display_name, search_terms, arcano_content)
        file_path = NPCS_DIR / npc_file
        file_path.write_text(page_content, encoding='utf-8')
        print(f"  Written: {file_path} ({len(page_content)} chars)")
    
    print("\nDone!")

if __name__ == "__main__":
    main()