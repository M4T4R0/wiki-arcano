#!/usr/bin/env python3
"""
Extract ALL Faction content from ARCANO_COMPLETO.md and populate docs/factions/*.md
"""

import re
from pathlib import Path

ARCANO_PATH = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/ARCANO_COMPLETO.md")
FACTIONS_DIR = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano/docs/factions")

# Factions with their exact section names and search terms
FACTIONS = {
    "ordem-arcanos-imperiais.md": {"name": "A Ordem dos Arcanos Imperiais", "terms": ["Ordem dos Arcanos Imperiais", "Arcanos Imperiais"]},
    "cargos-da-ordem.md": {"name": "Cargos da Organização", "terms": ["Cargos da Organização", "Cargos da Ordem"]},
    "titulos-honorarios.md": {"name": "Títulos Honorários", "terms": ["Títulos Honorários"]},
    "sam-mael-quartel-general.md": {"name": "Sam-Mael - O Quartel General dos Arcanos Imperiais", "terms": ["Sam-Mael", "Quartel General dos Arcanos"]},
    "locais-notaveis-ordem.md": {"name": "Locais Notáveis", "terms": ["Locais Notáveis", "Ordem dos Arcanos"]},
    "personalidades-notaveis.md": {"name": "Personalidades Notáveis", "terms": ["Personalidades Notáveis", "Arcanos"]},
    "os-cavaleiros.md": {"name": "Os Cavaleiros", "terms": ["Os Cavaleiros", "Cavaleiros da Ordem"]},
    "origens-e-proposito.md": {"name": "Origens e Propósito", "terms": ["Origens e Propósito", "Origem da Ordem"]},
    "regimento-vigilia-escarlate.md": {"name": "Regimento da Vigília Escarlate", "terms": ["Regimento da Vigília Escarlate", "Vigília Escarlate"]},
    "regimento-ossaria-silenciosa.md": {"name": "Regimento da Ossaria Silenciosa", "terms": ["Regimento da Ossaria Silenciosa", "Ossaria Silenciosa"]},
    "regimento-folego-infernal.md": {"name": "Regimento do Fôlego Infernal", "terms": ["Regimento do Fôlego Infernal", "Fôlego Infernal"]},
    "regimento-limiar-abissal.md": {"name": "Regimento do Limiar Abissal", "terms": ["Regimento do Limiar Abissal", "Limiar Abissal"]},
    "regimento-aurora-fendida.md": {"name": "Regimento da Aurora Fendida", "terms": ["Regimento da Aurora Fendida", "Aurora Fendida"]},
    "regimento-intendentes-ossavermelha.md": {"name": "Regimento dos Intendentes de Ossavermelha", "terms": ["Regimento dos Intendentes", "Ossavermelha"]},
    "treinamento-dos-cavaleiros.md": {"name": "Treinamento dos Cavaleiros", "terms": ["Treinamento dos Cavaleiros", "Treinamento da Ordem"]},
    "imperio-qual-imperio.md": {"name": "IMPÉRIO, QUAL IMPÉRIO?", "terms": ["IMPÉRIO, QUAL IMPÉRIO?"]},
    "floresta-kaaqwy.md": {"name": "FLORESTA KA'AQWY", "terms": ["FLORESTA KA'AQWY", "KA'AQWY"]},
    "reino-dos-abare.md": {"name": "Reino dos Abaré", "terms": ["Reino dos Abaré"]},
    "elfin.md": {"name": "Elfin", "terms": ["Elfin", "Cidade Elfin"]},
    "reino-dos-abaquar.md": {"name": "Reino dos Abaquar", "terms": ["Reino dos Abaquar"]},
    "reino-dos-piquira.md": {"name": "Reino dos Piquira", "terms": ["Reino dos Piquira", "Avista"]},
    "mundo-interior.md": {"name": "MUNDO INTERIOR", "terms": ["MUNDO INTERIOR", "Mundo Interior", "Andirá"]},
    "andira.md": {"name": "Andirá", "terms": ["Andirá", "Última Cidadela Anã"]},
    "as-cidades-livres.md": {"name": "AS CIDADES LIVRES", "terms": ["AS CIDADES LIVRES", "Cidades Livres"]},
    "vul.md": {"name": "Vul", "terms": ["Vul", "Magos das Trevas de Vul"]},
    "os-magos-das-trevas-de-vul.md": {"name": "Os Magos das Trevas de Vul", "terms": ["Os Magos das Trevas de Vul", "Magos das Trevas de Vul"]},
    "fortuna.md": {"name": "Fortuna", "terms": ["Fortuna", "Cidade Pirata"]},
    "montes-brancos.md": {"name": "Montes Brancos", "terms": ["Montes Brancos", "Ybytu", "Arani"]},
    "ybytu.md": {"name": "Ybytu", "terms": ["Ybytu", "Ybytui"]},
    "arani.md": {"name": "Arani", "terms": ["Arani", "Tamaya", "Portões da Névoa"]},
    "tamaya.md": {"name": "Tamaya", "terms": ["Tamaya", "Cidade dos Portões da Névoa"]},
    "deserto-acuc.md": {"name": "DESERTO AÇU", "terms": ["DESERTO AÇU", "Deserto Açu"]},
    "mbae.md": {"name": "Mbaê", "terms": ["Mbaê", "Rainha Morrigan"]},
    "ybi.md": {"name": "Ybi", "terms": ["Ybi", "Faraó Karnos Minor", "Muralha Habitável"]},
    "acuba.md": {"name": "Acuba", "terms": ["Acuba", "Acuba Sidious"]},
    "terra-dos-kaapora.md": {"name": "Terra dos Kaapora", "terms": ["Terra dos Kaapora", "Kaapora", "Anama"]},
    "anama.md": {"name": "Anama", "terms": ["Anama", "Halflings Kaapora"]},
    "terra-selvagem.md": {"name": "TERRA SELVAGEM", "terms": ["TERRA SELVAGEM", "Terra Selvagem"]},
    "as-terras-dos-aucas.md": {"name": "As Terras dos Auçás", "terms": ["As Terras dos Auçás", "Terras dos Auçás", "Terras dos Auçá"]},
    "as-ilhas.md": {"name": "AS ILHAS", "terms": ["AS ILHAS", "Ilhas", "Tibá", "Araxá", "Avista", "Acag"]},
    "o-reino-submerso.md": {"name": "O Reino Submerso", "terms": ["O Reino Submerso"]},
    "laure.md": {"name": "Lauré", "terms": ["Lauré", "Yawara", "Kemonos"]},
    "tupa-sununga.md": {"name": "Tupãsununga", "terms": ["Tupãsununga", "Tupãsunuguano"]},
    "yu.md": {"name": "Yu", "terms": ["Yu", "Continente Oriental", "Meiji", "Sasaki Musashi"]},
    "tiba.md": {"name": "Tibá", "terms": ["Tibá", "Ilha dos Gigantes", "Megalópia"]},
    "soba.md": {"name": "Sobá", "terms": ["Sobá"]},
    "os-planos-de-existencia.md": {"name": "OS PLANOS DE EXISTÊNCIA", "terms": ["OS PLANOS DE EXISTÊNCIA", "Planos de Existência"]},
    "aslareth.md": {"name": "Aslareth", "terms": ["Aslareth", "Antiga Capital"]},
    "linha-do-tempo-de-aslareth.md": {"name": "LINHA DO TEMPO DE ASLARETH", "terms": ["LINHA DO TEMPO DE ASLARETH"]},
    "cidades-perdidas.md": {"name": "CIDADES PERDIDAS", "terms": ["CIDADES PERDIDAS", "Ratanaba"]},
    "as-ruinas-de-ratanaba.md": {"name": "AS RUÍNAS DE RATANABA", "terms": ["AS RUÍNAS DE RATANABA", "Ratanaba"]},
    "ameacas-de-arcano.md": {"name": "AMEAÇAS DE ARCANO", "terms": ["AMEAÇAS DE ARCANO", "Ameaças"]},
    "misty-as-la.md": {"name": "MISTY AS-LA", "terms": ["MISTY AS-LA", "MAL", "M.A.L."]},
    "eligos-primeiro-duque.md": {"name": "ELIGOS O PRIMEIRO DUQUE DO INFERNO", "terms": ["ELIGOS", "Primeiro Duque do Inferno"]},
    "vlad-dracul.md": {"name": "VLAD DRACUL O MAGO DAS TREVAS VAMPIRO", "terms": ["VLAD DRACUL", "Vlad Dracul"]},
    "perigos-regionais.md": {"name": "PERIGOS REGIONAIS", "terms": ["PERIGOS REGIONAIS"]},
    "a-legiao-goblinoide.md": {"name": "A LEGIÃO GOBLINÓIDE", "terms": ["A LEGIÃO GOBLINÓIDE", "Goblinoides"]},
    "a-horda-de-orcs.md": {"name": "A HORDA DE ORCS", "terms": ["A HORDA DE ORCS", "Horda de Orcs"]},
    "o-levantamento-taurico.md": {"name": "O LEVANTAMENTO TÁURICO", "terms": ["O LEVANTAMENTO TÁURICO", "Levante Taurico", "Minotauros"]},
    "a-alcateia-gnol.md": {"name": "A ALCATÉIA GNÓL", "terms": ["A ALCATÉIA GNÓL", "Alcatéia Gnól", "Gnól"]},
    "artefatos-de-arcano.md": {"name": "ARTEFATOS DE ARCANO", "terms": ["ARTEFATOS DE ARCANO", "Artefatos"]},
    "aliados-conjurados.md": {"name": "Aliados Conjurados", "terms": ["Aliados Conjurados", "Conjurados"]},
    "as-armaduras-lendarias.md": {"name": "As Armaduras Lendárias", "terms": ["As Armaduras Lendárias", "Armaduras Lendárias"]},
    "veiculos.md": {"name": "Veículos", "terms": ["Veículos", "Aparatos", "Aiship"]},
    "lista-de-magias.md": {"name": "LISTA DE MAGIAS", "terms": ["LISTA DE MAGIAS", "Magias", "Escola"]},
    "magias.md": {"name": "Magias", "terms": ["Magias", "Escola Física", "Escola Alquímica", "Escola Natural", "Escola Abstrata"]},
}

def load_arcano():
    return ARCANO_PATH.read_text(encoding='utf-8')

def extract_faction_section(content, faction_data):
    """Extract the precise faction subsection"""
    display_name = faction_data["name"]
    terms = faction_data["terms"]
    
    # Try to find the exact section heading
    best_section = ""
    best_score = 0
    
    # Split by major headings
    sections = re.split(r'\n(?=# \*\*[^*]+\*\*)', content)
    
    for section in sections:
        score = 0
        section_lower = section.lower()
        for term in faction_data["terms"]:
            if term.lower() in section_lower:
                score += section_lower.count(term.lower()) * len(term)
        
        # Bonus if section starts with the exact name
        if faction_data["name"].upper() in section.upper()[:200]:
            score += 1000
        
        if score > best_score:
            best_score = score
            best_section = section
    
    if best_score < 30:
        # Fallback: try paragraphs
        paragraphs = re.split(r'\n\n+', content)
        for para in paragraphs:
            score = 0
            para_lower = para.lower()
            for term in faction_data["terms"]:
                if term.lower() in para_lower:
                    score += para_lower.count(term.lower()) * len(term)
            if score > best_score:
                best_score = score
                best_section = para
    
    return best_section if best_score >= 20 else ""

def build_faction_page(faction_file, faction_data, arcano_content):
    display_name = faction_data["name"]
    section = extract_faction_section(arcano_content, faction_data)
    
    lines = []
    lines.append(f"# {display_name}")
    lines.append("")
    lines.append(f"> **Facção de Arcano** — {display_name}")
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
    lines.append(f"- [Índice de Facções](../factions/index.md) — Volta ao índice")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"> *Página populada a partir do ARCANO_COMPLETO.md — revise e complete*")
    
    return '\n'.join(lines)

def main():
    print("Loading ARCANO_COMPLETO.md...")
    arcano_content = load_arcano()
    print(f"Loaded {len(arcano_content)} characters")
    
    for faction_file, faction_data in FACTIONS.items():
        display_name = faction_data["name"]
        print(f"Generating {faction_file} ({display_name})...")
        
        page_content = build_faction_page(faction_file, faction_data, arcano_content)
        file_path = FACTIONS_DIR / faction_file
        file_path.write_text(page_content, encoding='utf-8')
        print(f"  Written: {file_path} ({len(page_content)} chars)")
    
    print("\nDone!")

if __name__ == "__main__":
    main()