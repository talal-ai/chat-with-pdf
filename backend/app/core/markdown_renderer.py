"""Professional markdown renderer with keyword bolding and structured formatting."""
import re
from typing import List, Set, Optional, Dict
from app.schemas.qa_response import QAResponse


# Domain-specific terms to auto-bold
BASE_TERMS = {
    "shariah", "shari'ah", "sharia", "fiqh", "fatwa", "aaoifi",
    "riba", "gharar", "maysir",
    "murabaha", "mudarabah", "musharakah", "ijarah", "tawarruq",
    "wakalah", "sukuk", "guarantee", "pledge", "contract", "resolution",
    "supervisory board", "shariah board", "sharia board", "enforceable", "prohibition",
    "monitoring", "reporting", "governance", "compliance", "islamic",
    "halal", "haram", "makruh", "mandub", "mubah",
    "qard", "salam", "istisna", "kafalah", "hawalah",
    "profit", "loss", "partnership", "transaction", "investment",
    "zakat", "sadaqah", "waqf", "qirad", "muzara'ah",
    "musaqah", "mudharib", "rab al-mal", "mudarib"
}


def bold_keywords(text: str, extra_terms: Optional[Set[str]] = None) -> str:
    """Bold domain-specific keywords in text."""
    terms = set(BASE_TERMS)
    if extra_terms:
        terms |= {t.lower() for t in extra_terms}
    
    # Sort longest first to prevent partial bolding inside multi-word terms
    for term in sorted(terms, key=len, reverse=True):
        # Use word boundaries to avoid partial matches
        pattern = r"\b" + re.escape(term) + r"\b"
        # Check if already bolded to avoid double-bolding
        text = re.sub(
            pattern,
            lambda m: f"**{m.group(0)}**" if not text[max(0, m.start()-2):m.start()] == "**" else m.group(0),
            text,
            flags=re.IGNORECASE
        )
    
    return text


def render_markdown(resp: QAResponse, extra_terms: Optional[Set[str]] = None) -> str:
    """Render response as natural, conversational markdown with optional structure."""
    
    def B(s: str) -> str:
        """Bold keywords in text."""
        return bold_keywords(s, extra_terms=extra_terms)
    
    sections = []
    
    # Start with the main answer (always present)
    if resp.answer:
        sections.append(B(resp.answer))
        sections.append("")
    
    # Add optional sections only if they have content
    
    # Executive Summary (only for complex topics)
    if resp.executive_summary:
        sections.append("### Key Points")
        for bullet in resp.executive_summary:
            sections.append(f"- {B(bullet)}")
        sections.append("")
    
    # Requirements (only when relevant)
    if resp.requirements_by_page:
        sections.append("### Requirements")
        
        # Sort pages numerically if possible
        def sort_key(page: str) -> tuple:
            try:
                return (float(page), page)
            except ValueError:
                return (float('inf'), page)
        
        for page in sorted(resp.requirements_by_page.keys(), key=sort_key):
            for item in resp.requirements_by_page[page]:
                sections.append(f"- {B(item)} *(Page {page})*")
        sections.append("")
    
    # Implementation steps (only for how-to questions)
    if resp.implementation_checklist:
        sections.append("### Implementation Steps")
        for i, step in enumerate(resp.implementation_checklist, 1):
            sections.append(f"{i}. {B(step)}")
        sections.append("")
    
    # Pitfalls (only when warnings are relevant)
    if resp.pitfalls:
        sections.append("### Important Considerations")
        for pitfall in resp.pitfalls:
            sections.append(f"- {B(pitfall)}")
        sections.append("")
    
    # Definitions (only when terms need explanation)
    if resp.definitions:
        sections.append("### Key Terms")
        for term, definition in resp.definitions.items():
            sections.append(f"**{term}**: {B(definition)}")
        sections.append("")
    
    # Sources (show if available)
    if resp.sources:
        unique_pages = list(dict.fromkeys(str(p) for p in resp.sources))
        if unique_pages:
            sections.append("*References: " + ", ".join(f"Page {p}" for p in unique_pages) + "*")
            sections.append("")
    
    # Follow-up questions (only when they add value)
    if resp.follow_up_questions:
        sections.append("---")
        sections.append("**Related questions you might ask:**")
        for question in resp.follow_up_questions:
            sections.append(f"- {question}")
    
    return "\n".join(sections)


def render_simple_markdown(text: str, sources: List[str], extra_terms: Optional[Set[str]] = None) -> str:
    """Render simple markdown for fallback responses with inline citations."""
    
    def B(s: str) -> str:
        return bold_keywords(s, extra_terms=extra_terms)
    
    # Bold the main text
    bolded_text = B(text)
    
    # Extract page numbers from the text and add inline citations
    import re
    
    # Find all existing [Page X] citations in the text
    existing_citations = re.findall(r'\[Page\s+([\d.]+)\]', bolded_text)
    
    # Get unique page numbers from sources
    unique_pages = list(dict.fromkeys(str(p) for p in sources))
    
    # Remove the separate Sources section first
    result = re.sub(r'\n\n\*\*Sources:\*\*.*$', '', bolded_text, flags=re.DOTALL)
    
    # Add inline citations to each numbered point
    lines = result.split('\n')
    processed_lines = []
    page_index = 0
    
    for line in lines:
        # Check if this is a numbered point (starts with number and period)
        if re.match(r'^\d+\.', line.strip()):
            # Extract the page number from the line if it exists
            line_citations = re.findall(r'\[Page\s+([\d.]+)\]', line)
            if line_citations:
                # Line already has citations, keep as is
                processed_lines.append(line)
            else:
                # Add a citation from our sources (distribute evenly)
                if page_index < len(unique_pages):
                    page = unique_pages[page_index]
                    processed_lines.append(f"{line} [Page {page}]")
                    page_index += 1
                else:
                    processed_lines.append(line)
        else:
            processed_lines.append(line)
    
    # Join the lines back together
    result = '\n'.join(processed_lines)
    
    return result

