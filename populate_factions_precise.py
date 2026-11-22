#!/usr/bin/env python3
"""
Extract ALL Faction content from ARCANO_COMPLETO.md - PRECISE EXTRACTION
Only extracts the exact section for each faction
"""

import re
from pathlib import Path

ARCANO_PATH = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/ARCANO_COMPLETO.md")
FACTIONS_DIR = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/factions")

# Only the main factions that have clear section headings in the document
FACTIONS = {
    # Main factions from the document
    "ordem-arcanos-imperiais.md": "A Ordem dos Arcanos Imperiais",
    "cargos-da-ordem.md": "Cargos da Organização",
    "titulos-honorarios.md": "Títulos Honorários",
    "sam-mael-quartel-general.md": "Sam-Mael - O Quartel General dos Arcanos Imperiais",
    "locais-notaveis-ordem.md": "Locais Notáveis",
    "personalidades-notaveis.md": "Personalidades Notáveis",
    "os-cavaleiros.md": "Os Cavaleiros",
    "origens-e-proposito.md": "Origens e Propósito",
    "regimento-vigilia-escarlate.md": "Regimento da Vigília Escarlate",
    "regimento-ossaria-silenciosa.md": "Regimento da Ossaria Silenciosa",
    "regimento-folego-infernal.md": "Regimento do Fôlego Infernal",
    "regimento-limiar-abissal.md": "Regimento do Limiar Abissal",
    "regimento-aurora-fendida.md": "Regimento da Aurora Fendida",
    "regimento-intendentes-ossavermelha.md": "Regimento dos Intendentes de Ossavermelha",
    "treinamento-dos-cavaleiros.md": "Treinamento dos Cavaleiros",
    "imperio-qual-imperio.md": "IMPÉRIO, QUAL IMPÉRIO?",
    "floresta-kaaqwy.md": "FLORESTA KA'AQWY",
    "reino-dos-abare.md": "Reino dos Abaré",
    "elfin.md": "Elfin",
    "reino-dos-abaquar.md": "Reino dos Abaquar",
    "reino-dos-piquira.md": "Reino dos Piquira",
    "mundo-interior.md": "MUNDO INTERIOR",
    "andira.md": "Andirá",
    "as-cidades-livres.md": "AS CIDADES LIVRES",
    "vul.md": "Vul",
    "os-magos-das-trevas-de-vul.md": "Os Magos das Trevas de Vul",
    "fortuna.md": "Fortuna",
    "montes-brancos.md": "Montes Brancos",
    "ybytu.md": "Ybytu",
    "arani.md": "Arani",
    "tamaya.md": "Tamaya",
    "deserto-acuc.md": "DESERTO AÇU",
    "mbae.md": "Mbaê",
    "ybi.md": "Ybi",
    "acuba.md": "Acuba",
    "terra-dos-kaapora.md": "Terra dos Kaapora",
    "anama.md": "Anama",
    "terra-selvagem.md": "TERRA SELVAGEM",
    "as-terras-dos-aucas.md": "As Terras dos Auçás",
    "as-ilhas.md": "AS ILHAS",
    "o-reino-submerso.md": "O Reino Submerso",
    "laure.md": "Lauré",
    "tupa-sununga.md": "Tupãsununga",
    "yu.md": "Yu",
    "tiba.md": "Tibá",
    "soba.md": "Sobá",
    "os-planos-de-existencia.md": "OS PLANOS DE EXISTÊNCIA",
    "aslareth.md": "Aslareth",
    "linha-do-tempo-de-aslareth.md": "LINHA DO TEMPO DE ASLARETH",
    "cidades-perdidas.md": "CIDADES PERDIDAS",
    "as-ruinas-de-ratanaba.md": "AS RUÍNAS DE RATANABA",
    "ameacas-de-arcano.md": "AMEAÇAS DE ARCANO",
    "misty-as-la.md": "MISTY AS-LA",
    "eligos-primeiro-duque.md": "ELIGOS O PRIMEIRO DUQUE DO INFERNO",
    "vlad-dracul.md": "VLAD DRACUL O MAGO DAS TREVAS VAMPIRO",
    "perigos-regionais.md": "PERIGOS REGIONAIS",
    "a-legiao-goblinoide.md": "A LEGIÃO GOBLINÓIDE",
    "a-horda-de-orcs.md": "A HORDA DE ORCS",
    "o-levantamento-taurico.md": "O LEVANTAMENTO TÁURICO",
    "a-alcateia-gnol.md": "A ALCATÉIA GNÓL",
    "artefatos-de-arcano.md": "ARTEFATOS DE ARCANO",
    "aliados-conjurados.md": "Aliados Conjurados",
    "as-armaduras-lendarias.md": "As Armaduras Lendárias",
    "veiculos.md": "Veículos",
    "lista-de-magias.md": "LISTA DE MAGIAS",
    "magias.md": "Magias",
}

def load_arcano():
    return ARCANO_PATH.read_text(encoding='utf-8')

def extract_section(content, exact_heading):
    """Extract the precise section for an exact heading"""
    # Find the exact heading
    pattern = rf'^# \*\*{re.escape(exact_heading)}\*\*'
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        return ""
    
    start = match.start()
    
    # Find next major heading
    next_heading = content.find("\n# **", match.end())
    if next_heading == -1:
        return content[start:]
    
    return content[start:next_heading].strip()

def build_faction_page(faction_file, display_name, arcano_content):
    section = extract_section(arcano_content, display_name)
    
    lines = []
    lines.append(f"# {display_name}")
    lines.append("")
    lines.append(f"> **Facção/Local de Arcano** — {display_name}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    if section:
        lines.append("## 📜 Conteúdo Original do ARCANO_COMPLETO.md")
        lines.append("")
        lines.append(section)
        lines.append("")
    else:
        lines.append("## 📜 Lore e História")
        lines.append("")
        lines.append("*Conteúdo a extrair do ARCANO_COMPLETO.md*")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    lines.append("## 🏛️ Estrutura e Organização")
    lines.append("")
    lines.append("*[A DEFINIR a partir do ARCANO_COMPLETO.md]*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🎯 Agenda e Objetivos")
    lines.append("")
    lines.append("*[A DEFINIR a partir do ARCANO_COMPLETO.md]*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 👥 Membros Notáveis")
    lines.append("| Nome | Cargo | Detalhes |")
    lines.append("|------|-------|----------|")
    lines.append("| **Líder** | [A DEFINIR] | Detalhes no ARCANO_COMPLETO.md |")
    lines.append("| **Membro Notável** | [A DEFINIR] | Detalhes no ARCANO_COMPLETO.md |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🗺️ Território e Bases")
    lines.append("")
    lines.append("*[A DEFINIR a partir do ARCANO_COMPLETO.md]*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🎯 Ganchos de Aventura")
    hooks = [
        f"1. **Contato** — PCs são abordados por {display_name}",
        f"2. **Missão** — Facção contrata PCs para tarefa perigosa",
        f"3. **Conflito** — Facção é antagonista/aliada central",
        f"4. **Infiltração** — PCs devem se infiltrar na organização",
        f"5. **Segredo** — Facção guarda informação vital",
    ]
    for hook in hooks:
        lines.append(hook)
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🔗 Links Relacionados")
    lines.append(f"- [Índice de Facções](index.md) — Volta ao índice")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"> *Página populada a partir do ARCANO_COMPLETO.md — revise e complete*")
    
    return '\n'.join(lines)

def extract_section(content, exact_heading):
    """Extract the precise section for an exact heading"""
    pattern = rf'^# \*\*{re.escape(exact_heading)}\*\*'
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        return ""
    
    start = match.start()
    next_heading = content.find("\n# **", match.end())
    if next_heading == -1:
        return content[start:]
    
    return content[start:next_heading].strip()

def main():
    print("Loading ARCANO_COMPLETO.md...")
    arcano_content = load_arcano()
    print(f"Loaded {len(arcano_content)} characters")
    
    for faction_file, display_name in FACTIONS.items():
        print(f"Generating {faction_file} ({display_name})...")
        
        page_content = build_faction_page(faction_file, display_name, arcano_content)
        file_path = FACTIONS_DIR / faction_file
        file_path.write_text(page_content, encoding='utf-8')
        print(f"  Written: {file_path} ({len(page_content)} chars)")
    
    print("\nDone!")

def load_arcano():
    return ARCANO_PATH.read_text(encoding='utf-8')

def build_faction_page(faction_file, display_name, arcano_content):
    section = extract_section(arcano_content, display_name)
    
    lines = []
    lines.append(f"# {display_name}")
    lines.append("")
    lines.append(f"> **Facção/Local de Arcano** — {display_name}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    if section:
        lines.append("## 📜 Conteúdo Original do ARCANO_COMPLETO.md")
        lines.append("")
        lines.append(section)
        lines.append("")
    else:
        lines.append("## 📜 Lore e História")
        lines.append("")
        lines.append("*Conteúdo a extrair do ARCANO_COMPLETO.md*")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    lines.append("## 🏛️ Estrutura e Organização")
    lines.append("")
    lines.append("*[A DEFINIR a partir do ARCANO_COMPLETO.md]*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🎯 Agenda e Objetivos")
    lines.append("")
    lines.append("*[A DEFINIR a partir do ARCANO_COMPLETO.md]*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 👥 Membros Notáveis")
    lines.append("| Nome | Cargo | Detalhes |")
    lines.append("|------|-------|----------|")
    lines.append("| **Líder** | [A DEFINIR] | Detalhes no ARCANO_COMPLETO.md |")
    lines.append("| **Membro Notável** | [A DEFINIR] | Detalhes no ARCANO_COMPLETO.md |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🗺️ Território e Bases")
    lines.append("")
    lines.append("*[A DEFINIR a partir do ARCANO_COMPLETO.md]*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🎯 Ganchos de Aventura")
    hooks = [
        f"1. **Contato** — PCs são abordados por {display_name}",
        f"2. **Missão** — Facção contrata PCs para tarefa perigosa",
        f"3. **Conflito** — Facção é antagonista/aliada central",
        f"4. **Infiltração** — PCs devem se infiltrar na organização",
        f"5. **Segredo** — Facção guarda informação vital",
    ]
    for hook in hooks:
        lines.append(hook)
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 🔗 Links Relacionados")
    lines.append(f"- [Índice de Facções](index.md) — Volta ao índice")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"> *Página populada a partir do ARCANO_COMPLETO.md — revise e complete*")
    
    return '\n'.join(lines)

def extract_section(content, exact_heading):
    """Extract the precise section for an exact heading"""
    pattern = rf'^# \*\*{re.escape(exact_heading)}\*\*'
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        return ""
    
    start = match.start()
    next_heading = content.find("\n# **", match.end())
    if next_heading == -1:
        return content[start:]
    
    return content[start:next_heading].strip()

def main():
    print("Loading ARCANO_COMPLETO.md...")
    arcano_content = ARCANO_PATH.read_text(encoding='utf-8')
    print(f"Loaded {len(arcano_content)} characters")
    
    for faction_file, display_name in FACTIONS.items():
        print(f"Generating {faction_file} ({display_name})...")
        
        page_content = build_faction_page(faction_file, display_name, arcano_content)
        file_path = FACTIONS_DIR / faction_file
        file_path.write_text(page_content, encoding='utf-8')
        print(f"  Written: {file_path} ({len(page_content)} chars)")
    
    print("\nDone!")

if __name__ == "__main__":
    import re
    from pathlib import Path
    
    ARCANO_PATH = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/ARCANO_COMPLETO.md")
    FACTIONS_DIR = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/factions")
    
    main()