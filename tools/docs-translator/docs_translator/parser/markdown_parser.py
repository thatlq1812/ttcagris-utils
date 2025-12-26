"""Markdown parser with structure preservation."""

import re
from pathlib import Path
from typing import List, Optional, Tuple

from markdown_it import MarkdownIt
from markdown_it.token import Token

from docs_translator.parser.tokens import (
    DocumentBlock,
    ParsedDocument,
    TranslationAction,
    TranslationUnit,
)


class MarkdownParser:
    """Parse Markdown files into structured translation units."""

    # Requirement ID patterns (never translate)
    REQUIREMENT_PATTERNS = [
        r"\b(FR|BR|NFR|TC|M|REQ|US|EPIC)-[A-Z0-9]+-?[A-Z0-9]*\b",  # FR-01, NFR-P01, US-001
        r"\b[A-Z]{2,4}-\d{1,5}\b",  # JIRA-like: ABC-123
    ]

    # URL pattern
    URL_PATTERN = r"https?://[^\s\)\]\"'>]+"

    # Code inline pattern (already handled by markdown-it, but for text processing)
    INLINE_CODE_PATTERN = r"`[^`]+`"

    def __init__(self, preserve_terms: Optional[List[str]] = None):
        """Initialize parser with optional preserve terms."""
        self.preserve_terms = preserve_terms or []
        self.md = MarkdownIt("commonmark", {"html": True})

    def parse_file(self, file_path: str) -> ParsedDocument:
        """Parse a Markdown file into a structured document."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = path.read_text(encoding="utf-8")
        return self.parse_content(content, source_path=file_path)

    def parse_content(
        self, content: str, source_path: str = "<string>"
    ) -> ParsedDocument:
        """Parse Markdown content into a structured document."""
        # Parse with markdown-it
        tokens = self.md.parse(content)

        # Convert to our block structure
        blocks = self._process_tokens(tokens, content)

        # Create document
        doc = ParsedDocument(source_path=source_path, blocks=blocks)

        # Extract title from first heading
        for block in blocks:
            if block.block_type == "heading" and block.level == 1:
                if block.units:
                    doc.title = block.units[0].content
                break

        doc.update_statistics()
        return doc

    def _process_tokens(
        self, tokens: List[Token], original_content: str
    ) -> List[DocumentBlock]:
        """Process markdown-it tokens into document blocks."""
        blocks = []
        lines = original_content.split("\n")
        i = 0

        while i < len(tokens):
            token = tokens[i]

            # Skip closing tokens
            if token.type.endswith("_close"):
                i += 1
                continue

            block = self._token_to_block(token, tokens, i, lines)
            if block:
                blocks.append(block)

            # Skip nested tokens for block-level elements
            if token.nesting == 1:  # Opening token
                # Find matching close
                depth = 1
                i += 1
                while i < len(tokens) and depth > 0:
                    if tokens[i].nesting == 1:
                        depth += 1
                    elif tokens[i].nesting == -1:
                        depth -= 1
                    i += 1
            else:
                i += 1

        return blocks

    def _token_to_block(
        self,
        token: Token,
        all_tokens: List[Token],
        index: int,
        lines: List[str],
    ) -> Optional[DocumentBlock]:
        """Convert a token to a document block."""
        # Get line range
        line_start = token.map[0] if token.map else 0
        line_end = token.map[1] if token.map else 0

        # Get raw content from original lines
        raw_content = "\n".join(lines[line_start:line_end])

        # Handle different token types
        if token.type == "heading_open":
            return self._process_heading(token, all_tokens, index, raw_content, line_start, line_end)

        elif token.type == "paragraph_open":
            return self._process_paragraph(token, all_tokens, index, raw_content, line_start, line_end)

        elif token.type == "fence":
            return self._process_code_fence(token, raw_content, line_start, line_end)

        elif token.type == "code_block":
            return self._process_code_block(token, raw_content, line_start, line_end)

        elif token.type == "bullet_list_open" or token.type == "ordered_list_open":
            return self._process_list(token, all_tokens, index, raw_content, line_start, line_end, lines)

        elif token.type == "blockquote_open":
            return self._process_blockquote(token, all_tokens, index, raw_content, line_start, line_end)

        elif token.type == "table_open":
            return self._process_table(token, all_tokens, index, raw_content, line_start, line_end)

        elif token.type == "hr":
            return DocumentBlock(
                block_type="hr",
                raw_content=raw_content,
                line_start=line_start,
                line_end=line_end,
                units=[
                    TranslationUnit(
                        content=raw_content,
                        action=TranslationAction.SKIP,
                        context="hr",
                        preserve_reason="horizontal_rule",
                    )
                ],
            )

        elif token.type == "html_block":
            return DocumentBlock(
                block_type="html",
                raw_content=raw_content,
                line_start=line_start,
                line_end=line_end,
                units=[
                    TranslationUnit(
                        content=raw_content,
                        action=TranslationAction.SKIP,
                        context="html",
                        preserve_reason="html_block",
                    )
                ],
            )

        return None

    def _process_heading(
        self,
        token: Token,
        all_tokens: List[Token],
        index: int,
        raw_content: str,
        line_start: int,
        line_end: int,
    ) -> DocumentBlock:
        """Process a heading block."""
        level = int(token.tag[1])  # h1 -> 1, h2 -> 2, etc.

        # Get inline content from next token
        inline_token = all_tokens[index + 1] if index + 1 < len(all_tokens) else None
        text = ""
        if inline_token and inline_token.type == "inline":
            text = inline_token.content

        units = self._extract_translation_units(text, "heading")

        return DocumentBlock(
            block_type="heading",
            raw_content=raw_content,
            units=units,
            level=level,
            line_start=line_start,
            line_end=line_end,
        )

    def _process_paragraph(
        self,
        token: Token,
        all_tokens: List[Token],
        index: int,
        raw_content: str,
        line_start: int,
        line_end: int,
    ) -> DocumentBlock:
        """Process a paragraph block."""
        # Get inline content from next token
        inline_token = all_tokens[index + 1] if index + 1 < len(all_tokens) else None
        text = ""
        if inline_token and inline_token.type == "inline":
            text = inline_token.content

        units = self._extract_translation_units(text, "paragraph")

        return DocumentBlock(
            block_type="paragraph",
            raw_content=raw_content,
            units=units,
            line_start=line_start,
            line_end=line_end,
        )

    def _process_code_fence(
        self,
        token: Token,
        raw_content: str,
        line_start: int,
        line_end: int,
    ) -> DocumentBlock:
        """Process a fenced code block."""
        return DocumentBlock(
            block_type="fence",
            raw_content=raw_content,
            language=token.info or "",
            line_start=line_start,
            line_end=line_end,
            units=[
                TranslationUnit(
                    content=token.content,
                    action=TranslationAction.SKIP,
                    context="code_fence",
                    preserve_reason="code_block",
                    line_start=line_start,
                    line_end=line_end,
                )
            ],
        )

    def _process_code_block(
        self,
        token: Token,
        raw_content: str,
        line_start: int,
        line_end: int,
    ) -> DocumentBlock:
        """Process an indented code block."""
        return DocumentBlock(
            block_type="code_block",
            raw_content=raw_content,
            line_start=line_start,
            line_end=line_end,
            units=[
                TranslationUnit(
                    content=token.content,
                    action=TranslationAction.SKIP,
                    context="code_block",
                    preserve_reason="indented_code",
                    line_start=line_start,
                    line_end=line_end,
                )
            ],
        )

    def _process_list(
        self,
        token: Token,
        all_tokens: List[Token],
        index: int,
        raw_content: str,
        line_start: int,
        line_end: int,
        lines: List[str],
    ) -> DocumentBlock:
        """Process a list block."""
        is_ordered = token.type == "ordered_list_open"
        units = []

        # Extract list item text
        # Simple approach: parse the raw content line by line
        list_marker_pattern = r"^(\s*)([-*+]|\d+\.)\s+(.*)$"

        for line in lines[line_start:line_end]:
            match = re.match(list_marker_pattern, line)
            if match:
                item_text = match.group(3)
                if item_text.strip():
                    units.extend(self._extract_translation_units(item_text, "list_item"))

        return DocumentBlock(
            block_type="list",
            raw_content=raw_content,
            units=units,
            is_ordered=is_ordered,
            line_start=line_start,
            line_end=line_end,
        )

    def _process_blockquote(
        self,
        token: Token,
        all_tokens: List[Token],
        index: int,
        raw_content: str,
        line_start: int,
        line_end: int,
    ) -> DocumentBlock:
        """Process a blockquote."""
        # Extract text from blockquote
        text = re.sub(r"^>\s*", "", raw_content, flags=re.MULTILINE)
        units = self._extract_translation_units(text, "blockquote")

        return DocumentBlock(
            block_type="blockquote",
            raw_content=raw_content,
            units=units,
            line_start=line_start,
            line_end=line_end,
        )

    def _process_table(
        self,
        token: Token,
        all_tokens: List[Token],
        index: int,
        raw_content: str,
        line_start: int,
        line_end: int,
    ) -> DocumentBlock:
        """Process a table."""
        units = []

        # Parse table cells from raw content
        for line in raw_content.split("\n"):
            # Skip separator line
            if re.match(r"^\s*\|?\s*[-:]+", line):
                continue

            # Extract cell content
            cells = re.findall(r"\|([^|]+)", line)
            for cell in cells:
                cell_text = cell.strip()
                if cell_text:
                    units.extend(self._extract_translation_units(cell_text, "table_cell"))

        return DocumentBlock(
            block_type="table",
            raw_content=raw_content,
            units=units,
            line_start=line_start,
            line_end=line_end,
        )

    def _extract_translation_units(
        self, text: str, context: str
    ) -> List[TranslationUnit]:
        """Extract translation units from text, handling inline elements."""
        if not text.strip():
            return []

        units = []

        # Check if entire text should be preserved
        if self._should_skip_entirely(text):
            units.append(
                TranslationUnit(
                    content=text,
                    action=TranslationAction.SKIP,
                    context=context,
                    preserve_reason="all_code_or_preserved",
                )
            )
            return units

        # For most content, create a single translation unit
        # The translator will handle inline code preservation
        units.append(
            TranslationUnit(
                content=text,
                action=TranslationAction.TRANSLATE,
                context=context,
            )
        )

        return units

    def _should_skip_entirely(self, text: str) -> bool:
        """Check if text should be entirely skipped."""
        # All inline code
        stripped = re.sub(self.INLINE_CODE_PATTERN, "", text).strip()
        if not stripped:
            return True

        # All URLs
        stripped = re.sub(self.URL_PATTERN, "", text).strip()
        if not stripped:
            return True

        return False

    def _is_requirement_id(self, text: str) -> bool:
        """Check if text is a requirement ID."""
        for pattern in self.REQUIREMENT_PATTERNS:
            if re.match(f"^{pattern}$", text.strip()):
                return True
        return False

    def _contains_preserve_term(self, text: str) -> Optional[str]:
        """Check if text contains a preserve term. Returns the term if found."""
        for term in self.preserve_terms:
            if term.lower() in text.lower():
                return term
        return None
