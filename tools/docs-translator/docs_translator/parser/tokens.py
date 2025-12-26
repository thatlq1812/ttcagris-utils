"""Token types and translation units for the parser."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class TranslationAction(Enum):
    """Action to take for a translation unit."""

    TRANSLATE = "translate"  # Send to AI for translation
    SKIP = "skip"  # Keep as-is (code blocks, inline code)
    PRESERVE = "preserve"  # Keep specific pattern (requirement IDs, URLs)


@dataclass
class TranslationUnit:
    """A unit of content to be processed for translation."""

    # The original text content
    content: str

    # Action to take
    action: TranslationAction

    # Context type for better translation
    context: str  # 'heading', 'paragraph', 'table_cell', 'list_item', 'blockquote'

    # Original position in the document
    line_start: int = 0
    line_end: int = 0

    # Reason for skipping/preserving (for debugging)
    preserve_reason: Optional[str] = None

    # Additional metadata
    metadata: dict = field(default_factory=dict)

    # Translated content (filled after translation)
    translated: Optional[str] = None

    def __repr__(self) -> str:
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"TranslationUnit({self.action.value}, {self.context}, '{preview}')"


@dataclass
class DocumentBlock:
    """A block in the document (preserves structure)."""

    # Block type from markdown-it
    block_type: str  # 'heading', 'paragraph', 'fence', 'code_block', 'table', 'list', etc.

    # Raw content of the block
    raw_content: str

    # Parsed translation units within this block
    units: List[TranslationUnit] = field(default_factory=list)

    # Block-level metadata
    level: int = 0  # For headings
    language: str = ""  # For code blocks
    is_ordered: bool = False  # For lists

    # Original line numbers
    line_start: int = 0
    line_end: int = 0

    # Translated raw content (filled after translation)
    translated_content: Optional[str] = None

    def needs_translation(self) -> bool:
        """Check if this block contains translatable content."""
        return any(unit.action == TranslationAction.TRANSLATE for unit in self.units)


@dataclass
class ParsedDocument:
    """A fully parsed document ready for translation."""

    # Original file path
    source_path: str

    # All blocks in order
    blocks: List[DocumentBlock] = field(default_factory=list)

    # Document metadata
    title: Optional[str] = None
    frontmatter: Optional[dict] = None

    # Statistics
    total_blocks: int = 0
    translatable_blocks: int = 0
    skipped_blocks: int = 0

    def get_translatable_units(self) -> List[TranslationUnit]:
        """Get all units that need translation."""
        units = []
        for block in self.blocks:
            for unit in block.units:
                if unit.action == TranslationAction.TRANSLATE:
                    units.append(unit)
        return units

    def get_all_units(self) -> List[TranslationUnit]:
        """Get all translation units."""
        units = []
        for block in self.blocks:
            units.extend(block.units)
        return units

    def update_statistics(self):
        """Update document statistics."""
        self.total_blocks = len(self.blocks)
        self.translatable_blocks = sum(1 for b in self.blocks if b.needs_translation())
        self.skipped_blocks = self.total_blocks - self.translatable_blocks
