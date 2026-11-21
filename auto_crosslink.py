#!/usr/bin/env python3
"""
Auto-Crosslinker for Arcano Wiki
================================
Automatically adds cross-links to known terms (races, NPCs, locations, 
factions, artifacts, magic terms) within wiki markdown pages.

Usage:
    python auto_crosslink.py --scan          # Build registry from wiki
    python auto_crosslink.py --link          # Add cross-links to pages
    python auto_crosslink.py --check         # Show what would be linked
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict

# Configuration
WIKI_ROOT = Path("/home/ubuntu/r2d2-brain/worldbuilding/arcano")
DOCS_DIR = WIKI_ROOT / "docs"

# Terms to exclude from auto-linking (too common, cause noise)
EXCLUDE_TERMS = {
    'a', 'o', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das',
    'e', 'em', 'no', 'na', 'nos', 'nas', 'por', 'para', 'com', 'sem', 'sob', 'sobre',
    'entre', 'após', 'até', 'desde', 'como', 'mais', 'menos', 'muito', 'pouco',
    'todo', 'toda', 'todos', 'todas', 'outro', 'outra', 'outros', 'outras',
    'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas',
    'aquele', 'aquela', 'aqueles', 'aquelas', 'qual', 'quais', 'quem', 'que',
    'se', 'não', 'sim', 'também', 'já', 'ainda', 'sempre', 'nunca', 'agora',
    'hoje', 'ontem', 'amanhã', 'antes', 'depois', 'durante', 'enquanto',
    'porque', 'pois', 'logo', 'então', 'porém', 'contudo', 'todavia', 'entretanto',
    'ou', 'e', 'nem', 'mas', 'se', 'caso', 'quando', 'onde', 'onde', 'aonde',
    'império', 'imperio', 'reino', 'cidade', 'capital', 'muralha', 'infestação',
    'magia', 'mana', 'trevas', 'éter', 'ether', 'raca', 'raca', 'especie',
    'npc', 'personagem', 'aventureiro', 'heroi', 'vilao', 'mago', 'guerreiro',
    'armadura', 'espada', 'escudo', 'arma', 'magico', 'magica', 'poder',
    'norte', 'sul', 'leste', 'oeste', 'centro', 'regiao', 'area', 'zona',
    'antigo', 'antiga', 'novo', 'nova', 'velho', 'velha', 'grande', 'pequeno',
    'forte', 'forte', 'fraco', 'fraca', 'bom', 'boa', 'ruim', 'mal', 'bem',
    'ano', 'anos', 'dia', 'dias', 'mes', 'meses', 'semana', 'semanas',
    'vez', 'vezes', 'vez', 'horas', 'hora', 'minuto', 'segundo',
}

# Minimum term length to consider for linking
MIN_TERM_LENGTH = 4

# Maximum links per page to avoid over-linking
MAX_LINKS_PER_PAGE = 15

# Context window for checking if term is already linked
LINK_CONTEXT_CHARS = 100


@dataclass
class WikiTerm:
    """Represents a linkable term in the wiki."""
    term: str
    category: str  # race, npc, location, faction, artifact, magic, faction
    target_path: str  # relative path from docs/
    aliases: List[str]  # alternative names/spellings
    priority: int = 1  # higher = more important


class WikiCrosslinker:
    def __init__(self, docs_dir: Path):
        self.docs_dir = Path(docs_dir)
        self.terms: Dict[str, WikiTerm] = {}  # normalized term -> WikiTerm
        self.term_aliases: Dict[str, str] = {}  # alias -> canonical term
        self.pages_content: Dict[str, str] = {}  # path -> content
        
    def build_registry(self) -> None:
        """Scan all wiki files and build the term registry."""
        print("Building term registry...")
        
        # 1. Scan races
        self._scan_races()
        
        # 2. Scan NPCs
        self._scan_npcs()
        
        # 3. Scan locations
        self._scan_locations()
        
        # 4. Scan artifacts
        self._scan_artifacts()
        
        # 5. Scan magic terms
        self._scan_magic()
        
        # 6. Scan factions
        self._scan_factions()
        
        # 7. Load all page contents for cross-linking
        self._load_all_pages()
        
        print(f"Registry built: {len(self.terms)} canonical terms, {len(self.term_aliases)} aliases")
        
    def _scan_races(self):
        """Extract race terms from races/individual/"""
        race_dir = self.docs_dir / "races" / "individual"
        if not race_dir.exists():
            return
            
        for md_file in race_dir.glob("*.md"):
            if md_file.name == "index.md":
                continue
            content = md_file.read_text(encoding='utf-8')
            # Extract race name from first header
            match = re.search(r'^#\s+\*\*(.+?)\*\*', content, re.MULTILINE)
            if match:
                name = match.group(1).strip()
                # Clean name for canonical term
                canonical = self._normalize_term(name)
                rel_path = f"races/individual/{md_file.name}"
                
                term = WikiTerm(
                    term=canonical,
                    category="race",
                    target_path=rel_path,
                    aliases=[name],
                    priority=3
                )
                self._register_term(term)
                
                # Also extract sub-races (Meio-Elfos, Meio-Orc, etc.)
                sub_matches = re.findall(r'^##\s+\*\*(.+?)\*\*', content, re.MULTILINE)
                for sub in sub_matches:
                    sub_canonical = self._normalize_term(sub.strip())
                    if sub_canonical != canonical:
                        sub_term = WikiTerm(
                            term=sub_canonical,
                            category="race",
                            target_path=rel_path,
                            aliases=[sub.strip()],
                            priority=2
                        )
                        self._register_term(sub_term)
    
    def _scan_npcs(self):
        """Extract NPC terms from npcs/individual/"""
        npc_dir = self.docs_dir / "npcs" / "individual"
        if not npc_dir.exists():
            return
            
        for md_file in npc_dir.glob("*.md"):
            if md_file.name == "index.md":
                continue
            content = md_file.read_text(encoding='utf-8')
            match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
            if match:
                name = match.group(1).strip()
                canonical = self._normalize_term(name)
                rel_path = f"npcs/individual/{md_file.name}"
                
                term = WikiTerm(
                    term=canonical,
                    category="npc",
                    target_path=rel_path,
                    aliases=[name],
                    priority=3
                )
                self._register_term(term)
    
    def _scan_locations(self):
        """Extract location terms from locations/ and factions/reinos/"""
        # Cities
        cities_dir = self.docs_dir / "locations" / "cidades"
        if cities_dir.exists():
            for md_file in cities_dir.glob("*.md"):
                if md_file.name == "index.md":
                    continue
                content = md_file.read_text(encoding='utf-8')
                match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
                if match:
                    name = match.group(1).strip()
                    canonical = self._normalize_term(name)
                    rel_path = f"locations/cidades/{md_file.name}"
                    term = WikiTerm(
                        term=canonical,
                        category="location",
                        target_path=rel_path,
                        aliases=[name],
                        priority=2
                    )
                    self._register_term(term)
        
        # Kingdoms/Realms
        reinos_dir = self.docs_dir / "factions" / "reinos"
        if reinos_dir.exists():
            for md_file in reinos_dir.glob("*.md"):
                if md_file.name == "index.md":
                    continue
                content = md_file.read_text(encoding='utf-8')
                match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
                if match:
                    name = match.group(1).strip()
                    # Remove suffixes like " — Tipo"
                    name_clean = re.sub(r'\s*—\s*.+$', '', name).strip()
                    canonical = self._normalize_term(name_clean)
                    rel_path = f"factions/reinos/{md_file.name}"
                    term = WikiTerm(
                        term=canonical,
                        category="location",
                        target_path=rel_path,
                        aliases=[name_clean],
                        priority=2
                    )
                    self._register_term(term)
    
    def _scan_factions(self):
        """Extract faction terms"""
        faction_dirs = [
            self.docs_dir / "factions",
            self.docs_dir / "factions" / "reinos",
        ]
        for fdir in faction_dirs:
            if not fdir.exists():
                continue
            for md_file in fdir.glob("*.md"):
                if md_file.name == "index.md":
                    continue
                content = md_file.read_text(encoding='utf-8')
                match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
                if match:
                    name = match.group(1).strip()
                    name_clean = re.sub(r'\s*—\s*.+$', '', name).strip()
                    canonical = self._normalize_term(name_clean)
                    rel_path = md_file.relative_to(self.docs_dir).as_posix()
                    term = WikiTerm(
                        term=canonical,
                        category="faction",
                        target_path=rel_path,
                        aliases=[name_clean],
                        priority=2
                    )
                    self._register_term(term)
    
    def _scan_artifacts(self):
        """Extract artifact terms"""
        artifacts_dir = self.docs_dir / "artifacts"
        if not artifacts_dir.exists():
            return
        for md_file in artifacts_dir.glob("*.md"):
            if md_file.name == "index.md":
                continue
            content = md_file.read_text(encoding='utf-8')
            # Extract weapon/armor/artifact names from headers
            headers = re.findall(r'^##\s+(.+)', content, re.MULTILINE)
            for h in headers:
                name = h.strip()
                canonical = self._normalize_term(name)
                rel_path = f"artifacts/{md_file.name}"
                term = WikiTerm(
                    term=canonical,
                    category="artifact",
                    target_path=rel_path,
                    aliases=[name],
                    priority=2
                )
                self._register_term(term)
    
    def _scan_magic(self):
        """Extract magic terms"""
        magic_dir = self.docs_dir / "magic"
        if not magic_dir.exists():
            return
        for md_file in magic_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            # Extract magic schools, fonemas, etc.
            headers = re.findall(r'^##\s+(.+)', content, re.MULTILINE)
            for h in headers:
                name = h.strip()
                canonical = self._normalize_term(name)
                rel_path = f"magic/{md_file.name}"
                term = WikiTerm(
                    term=canonical,
                    category="magic",
                    target_path=rel_path,
                    aliases=[name],
                    priority=2
                )
                self._register_term(term)
            
            # Also extract fonemas (ECH, OR, EL, THAR, Anti-Fonemas)
            fonemas = ['ECH', 'OR', 'EL', 'THAR', 'Anti-Fonemas']
            for f in fonemas:
                canonical = self._normalize_term(f)
                term = WikiTerm(
                    term=canonical,
                    category="magic",
                    target_path=f"magic/{md_file.name}",
                    aliases=[f],
                    priority=3
                )
                self._register_term(term)
    
    def _normalize_term(self, term: str) -> str:
        """Normalize term for registry key."""
        # Remove markdown formatting
        term = re.sub(r'\*\*', '', term)
        # Remove parenthetical suffixes like " (1 ponto)"
        term = re.sub(r'\s*\([^)]*\)\s*$', '', term)
        # Remove trailing punctuation
        term = term.strip(' .,;:')
        # Normalize whitespace
        term = re.sub(r'\s+', ' ', term).strip()
        return term.lower()
    
    def _register_term(self, term: WikiTerm):
        """Register a term and its aliases."""
        if term.term in EXCLUDE_TERMS or len(term.term) < MIN_TERM_LENGTH:
            return
        
        # Register canonical term
        if term.term not in self.terms or term.priority > self.terms[term.term].priority:
            self.terms[term.term] = term
        
        # Register aliases
        for alias in term.aliases:
            alias_norm = self._normalize_term(alias)
            if alias_norm not in EXCLUDE_TERMS and len(alias_norm) >= MIN_TERM_LENGTH:
                if alias_norm not in self.term_aliases or term.priority > self.terms.get(self.term_aliases[alias_norm], WikiTerm('', '', '', [], 0)).priority:
                    self.term_aliases[alias_norm] = term.term
    
    def _load_all_pages(self):
        """Load all markdown page contents."""
        for md_file in self.docs_dir.rglob("*.md"):
            try:
                rel_path = md_file.relative_to(self.docs_dir).as_posix()
                content = md_file.read_text(encoding='utf-8')
                self.pages_content[rel_path] = content
            except Exception as e:
                print(f"Warning: Could not load {md_file}: {e}")
    
    def _is_in_header(self, content: str, pos: int) -> bool:
        """Check if position is inside a markdown header (lines starting with #)."""
        line_start = content.rfind('\n', 0, pos) + 1
        line = content[line_start:content.find('\n', pos)]
        return line.lstrip().startswith('#')
    
    def _is_in_code_block(self, content: str, pos: int) -> bool:
        """Check if position is inside a code block (```)."""
        before = content[:pos]
        code_blocks = before.count('```')
        return code_blocks % 2 == 1
    
    def _is_in_link(self, content: str, pos: int) -> bool:
        """Check if position is already inside a markdown link [text](url)."""
        before = content[:pos]
        after = content[pos:]
        
        # Check if we're inside [text](url)
        # Find the last [ before pos
        last_open = before.rfind('[')
        if last_open == -1:
            return False
        
        # Find the ] after the last [
        close_bracket = before.find(']', last_open)
        if close_bracket == -1:
            return False
            
        # Check if followed by (
        after_bracket = before[close_bracket+1:]
        if after_bracket.startswith('('):
            # We're inside [text]( - now check if we're before the closing )
            after_pos = content[pos:]
            close_paren = after_pos.find(')')
            if close_paren != -1:
                return True
        return False
    
    def _compute_relative_path(self, current_path: str, target_path: str) -> str:
        """Compute relative path from current page to target page."""
        current_dir = Path(current_path).parent
        target = Path(target_path)
        
        # If target is absolute from docs root, make it relative to current_dir
        try:
            rel = target.relative_to(current_dir)
            return rel.as_posix()
        except ValueError:
            # Target is not under current_dir, go up and down
            # Compute relative path from current_dir to target
            return os.path.relpath(target_path, current_dir.as_posix())
    
    def find_linkable_terms(self, content: str, current_path: str) -> List[Tuple[str, str, int]]:
        """Find all linkable terms in content that aren't already linked."""
        matches = []
        
        # Get current page title to avoid self-linking
        current_title = ""
        if current_path in self.pages_content:
            current_title = self._extract_title(self.pages_content[current_path])
        current_title_norm = self._normalize_term(current_title)
        
        # Sort terms by length (longest first) to match longest terms first
        sorted_aliases = sorted(self.term_aliases.items(), key=lambda x: -len(x[0]))
        
        for alias, canonical in sorted_aliases:
            if alias in EXCLUDE_TERMS or len(alias) < MIN_TERM_LENGTH:
                continue
            
            # Skip if this is the current page's own title (avoid self-linking)
            if canonical == current_title_norm:
                continue
            
            # Find all occurrences of this alias
            # Use word boundaries for better matching
            pattern = r'(?<![\w\[\]\(\)])' + re.escape(alias) + r'(?![\w\[\]\(\)])'
            for match in re.finditer(pattern, content, re.IGNORECASE):
                start, end = match.span()
                
                # Skip if in header
                if self._is_in_header(content, start):
                    continue
                
                # Skip if in code block
                if self._is_in_code_block(content, start):
                    continue
                
                # Skip if already in a link
                if self._is_in_link(content, start):
                    continue
                
                matches.append((alias, canonical, match.start()))
        
        return matches
    
    def _extract_title(self, content: str) -> str:
        """Extract first H1 title from content."""
        match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        return match.group(1).strip() if match else ""
    
    def add_crosslinks(self, content: str, current_path: str, max_links: int = MAX_LINKS_PER_PAGE) -> Tuple[str, int]:
        """Add cross-links to content."""
        matches = self.find_linkable_terms(content, current_path)
        
        if not matches:
            return content, 0
        
        # Sort by position (reverse for safe replacement)
        matches.sort(key=lambda x: -x[2])
        
        added = 0
        new_content = content
        
        for alias, canonical, pos in matches:
            if added >= max_links:
                break
            
            term = self.terms.get(canonical)
            if not term:
                continue
            
            # Compute correct relative path from current page to target
            rel_path = self._compute_relative_path(current_path, term.target_path)
            
            # Build link - use the original alias casing for display
            link = f"[{alias}]({rel_path})"
            
            # Replace at position
            new_content = new_content[:pos] + link + new_content[pos + len(alias):]
            added += 1
        
        return new_content, added
    
    def check_page(self, path: str) -> List[Tuple[str, str]]:
        """Check what terms in a page could be linked (dry run)."""
        if path not in self.pages_content:
            return []
        content = self.pages_content[path]
        matches = self.find_linkable_terms(content, path)
        return [(alias, self.term_aliases[alias]) for alias, _, _ in matches]
    
    def process_all_pages(self, dry_run: bool = True) -> Dict[str, int]:
        """Process all pages adding cross-links."""
        results = {}
        for path, content in self.pages_content.items():
            if path.endswith("index.md"):
                continue  # Skip index files
            new_content, added = self.add_crosslinks(content, path)
            results[path] = added
            if not dry_run and added > 0:
                full_path = self.docs_dir / path
                full_path.write_text(new_content, encoding='utf-8')
        return results
    
    def save_registry(self, path: Path):
        """Save registry to JSON for inspection."""
        data = {
            term: {
                "term": t.term,
                "category": t.category,
                "target_path": t.target_path,
                "aliases": t.aliases,
                "priority": t.priority
            }
            for term, t in self.terms.items()
        }
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def load_registry(self, path: Path):
        """Load registry from JSON."""
        data = json.loads(path.read_text(encoding='utf-8'))
        self.terms = {}
        self.term_aliases = {}
        for term, t in data.items():
            wt = WikiTerm(**t)
            self.terms[term] = wt
            for alias in wt.aliases:
                self.term_aliases[self._normalize_term(alias)] = term


def main():
    parser = argparse.ArgumentParser(description="Arcano Wiki Auto-Crosslinker")
    parser.add_argument("--scan", action="store_true", help="Build term registry from wiki")
    parser.add_argument("--link", action="store_true", help="Add cross-links to pages")
    parser.add_argument("--check", action="store_true", help="Show what would be linked (dry run)")
    parser.add_argument("--registry", default="wiki_registry.json", help="Registry file path")
    parser.add_argument("--max-links", type=int, default=MAX_LINKS_PER_PAGE, help="Max links per page")
    args = parser.parse_args()
    
    linker = WikiCrosslinker(DOCS_DIR)
    
    if args.scan or args.link or args.check:
        linker.build_registry()
    
    if args.scan:
        linker.save_registry(Path(args.registry))
        print(f"Registry saved to {args.registry}")
    
    if args.check:
        # Dry run on all pages
        results = linker.process_all_pages(dry_run=True)
        total = sum(results.values())
        pages_with_links = sum(1 for v in results.values() if v > 0)
        print(f"\nDry run results:")
        print(f"  Pages with potential links: {pages_with_links}")
        print(f"  Total potential links: {total}")
        print(f"  Average per page: {total/len(results):.1f}")
        
        # Show top pages
        sorted_results = sorted(results.items(), key=lambda x: -x[1])
        print(f"\nTop 10 pages with most link opportunities:")
        for path, count in sorted_results[:10]:
            if count > 0:
                print(f"  {path}: {count} links")
    
    if args.link:
        print("Adding cross-links to pages...")
        results = linker.process_all_pages(dry_run=False)
        total = sum(results.values())
        pages_modified = sum(1 for v in results.values() if v > 0)
        print(f"Modified {pages_modified} pages, added {total} cross-links")


if __name__ == "__main__":
    main()