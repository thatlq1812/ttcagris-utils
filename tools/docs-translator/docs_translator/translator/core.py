"""Core translator implementation."""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable

from tqdm import tqdm

from docs_translator.config.manager import TranslatorConfig
from docs_translator.parser.markdown_parser import MarkdownParser
from docs_translator.parser.tokens import (
    DocumentBlock,
    ParsedDocument,
    TranslationAction,
    TranslationUnit,
)
from docs_translator.translator.providers import BaseProvider, create_provider
from docs_translator.translator.prompts import PromptBuilder


@dataclass
class TranslationResult:
    """Result of a translation operation."""

    source_path: str
    output_path: str
    success: bool
    total_blocks: int = 0
    translated_blocks: int = 0
    cached_blocks: int = 0
    skipped_blocks: int = 0
    error: Optional[str] = None
    duration_seconds: float = 0.0
    estimated_cost: float = 0.0


@dataclass
class TranslationMemoryEntry:
    """Entry in translation memory."""

    source_hash: str
    source_text: str
    target_text: str
    source_lang: str
    target_lang: str
    context: str
    timestamp: str
    model: str


class TranslationMemory:
    """Translation memory for caching translations."""

    def __init__(self, cache_dir: str = ".translation_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "translation_memory.json"
        self.memory: Dict[str, TranslationMemoryEntry] = {}
        self._load()

        # Statistics
        self.hits = 0
        self.misses = 0

    def _load(self):
        """Load memory from disk."""
        if self.cache_file.exists():
            try:
                data = json.loads(self.cache_file.read_text(encoding="utf-8"))
                for key, entry_data in data.get("memory", {}).items():
                    self.memory[key] = TranslationMemoryEntry(**entry_data)
            except (json.JSONDecodeError, TypeError):
                self.memory = {}

    def save(self):
        """Save memory to disk."""
        data = {
            "version": "1.0",
            "memory": {key: entry.__dict__ for key, entry in self.memory.items()},
            "stats": {
                "total_entries": len(self.memory),
                "hits": self.hits,
                "misses": self.misses,
            },
        }
        self.cache_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _compute_hash(
        self, text: str, source_lang: str, target_lang: str, context: str
    ) -> str:
        """Compute hash for cache lookup."""
        content = f"{source_lang}|{target_lang}|{context}|{text}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    def get(
        self, text: str, source_lang: str, target_lang: str, context: str
    ) -> Optional[str]:
        """Get cached translation."""
        key = self._compute_hash(text, source_lang, target_lang, context)
        if key in self.memory:
            self.hits += 1
            return self.memory[key].target_text
        self.misses += 1
        return None

    def set(
        self,
        text: str,
        translation: str,
        source_lang: str,
        target_lang: str,
        context: str,
        model: str,
    ):
        """Store translation in cache."""
        key = self._compute_hash(text, source_lang, target_lang, context)
        self.memory[key] = TranslationMemoryEntry(
            source_hash=key,
            source_text=text,
            target_text=translation,
            source_lang=source_lang,
            target_lang=target_lang,
            context=context,
            timestamp=datetime.now().isoformat(),
            model=model,
        )

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_entries": len(self.memory),
            "hit_rate": hit_rate,
        }


class Translator:
    """Main translator class."""

    def __init__(
        self,
        config: Optional[TranslatorConfig] = None,
        use_cache: bool = True,
    ):
        """Initialize translator.

        Args:
            config: Configuration object. If None, loads from default locations.
            use_cache: Whether to use translation memory cache.
        """
        self.config = config or TranslatorConfig.load()
        self.parser = MarkdownParser(preserve_terms=self.config.preserve_terms)
        self.provider: Optional[BaseProvider] = None
        self.use_cache = use_cache
        self.memory: Optional[TranslationMemory] = None

        if use_cache:
            self.memory = TranslationMemory(self.config.cache_dir)

    def _ensure_provider(self):
        """Ensure provider is initialized."""
        if self.provider is None:
            api_key = self.config.get_api_key()
            if not api_key:
                raise ValueError(
                    f"No API key found for {self.config.active_provider}. "
                    f"Run 'docs-translator configure' to set up."
                )

            self.provider = create_provider(
                provider_name=self.config.active_provider,
                api_key=api_key,
                model=self.config.get_model(),
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

    def translate_text(
        self,
        text: str,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
        context: str = "paragraph",
    ) -> str:
        """Translate a single piece of text.

        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            context: Context type for translation

        Returns:
            Translated text
        """
        self._ensure_provider()

        source = source_lang or self.config.default_source_lang
        target = target_lang or self.config.default_target_lang

        # Check cache
        if self.memory:
            cached = self.memory.get(text, source, target, context)
            if cached:
                return cached

        # Build prompt and translate
        system_prompt = PromptBuilder.build_system_prompt(
            source_lang=source,
            target_lang=target,
            preserve_terms=self.config.preserve_terms,
            style=self.config.translation_style,
            context=context,
        )

        translated = self.provider.translate(text, system_prompt)

        # Cache result
        if self.memory:
            self.memory.set(
                text=text,
                translation=translated,
                source_lang=source,
                target_lang=target,
                context=context,
                model=self.config.get_model(),
            )

        return translated

    def translate_file(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
        dry_run: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> TranslationResult:
        """Translate a Markdown file.

        Args:
            input_path: Path to input file
            output_path: Path for output file. If None, auto-generated.
            source_lang: Source language code
            target_lang: Target language code
            dry_run: If True, don't actually translate, just analyze
            progress_callback: Callback for progress updates (current, total)

        Returns:
            TranslationResult with statistics
        """
        import time

        start_time = time.time()
        source = source_lang or self.config.default_source_lang
        target = target_lang or self.config.default_target_lang

        # Generate output path if not provided
        if output_path is None:
            input_p = Path(input_path)
            output_path = str(input_p.parent / f"{input_p.stem}_{target}{input_p.suffix}")

        result = TranslationResult(
            source_path=input_path,
            output_path=output_path,
            success=False,
        )

        try:
            # Parse document
            doc = self.parser.parse_file(input_path)
            result.total_blocks = doc.total_blocks

            if dry_run:
                # Just count what would be translated
                for block in doc.blocks:
                    if block.needs_translation():
                        for unit in block.units:
                            if unit.action == TranslationAction.TRANSLATE:
                                if self.memory:
                                    cached = self.memory.get(
                                        unit.content, source, target, unit.context
                                    )
                                    if cached:
                                        result.cached_blocks += 1
                                    else:
                                        result.translated_blocks += 1
                                else:
                                    result.translated_blocks += 1
                    else:
                        result.skipped_blocks += 1

                result.success = True
            else:
                # Actually translate
                self._ensure_provider()
                translated_content = self._translate_document(
                    doc, source, target, progress_callback
                )

                # Count statistics
                for block in doc.blocks:
                    if block.needs_translation():
                        result.translated_blocks += 1
                    else:
                        result.skipped_blocks += 1

                # Write output
                output_p = Path(output_path)
                output_p.parent.mkdir(parents=True, exist_ok=True)
                output_p.write_text(translated_content, encoding="utf-8")

                # Save cache
                if self.memory:
                    self.memory.save()
                    stats = self.memory.get_stats()
                    result.cached_blocks = stats["hits"]

                result.success = True

        except Exception as e:
            result.error = str(e)
            result.success = False

        result.duration_seconds = time.time() - start_time
        return result

    def _translate_document(
        self,
        doc: ParsedDocument,
        source_lang: str,
        target_lang: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> str:
        """Translate a parsed document and reconstruct Markdown."""
        translated_blocks = []
        total_units = len(doc.get_translatable_units())
        current_unit = 0

        for block in doc.blocks:
            if not block.needs_translation():
                # Keep as-is
                translated_blocks.append(block.raw_content)
                continue

            # Translate each unit in the block
            translated_units = []
            for unit in block.units:
                if unit.action == TranslationAction.TRANSLATE:
                    translated_text = self.translate_text(
                        text=unit.content,
                        source_lang=source_lang,
                        target_lang=target_lang,
                        context=unit.context,
                    )
                    unit.translated = translated_text
                    translated_units.append(translated_text)

                    current_unit += 1
                    if progress_callback:
                        progress_callback(current_unit, total_units)
                else:
                    # Keep original
                    translated_units.append(unit.content)

            # Reconstruct block with translations
            translated_block = self._reconstruct_block(block, translated_units)
            translated_blocks.append(translated_block)

        # Join blocks - strip trailing newlines first, then join with double newline
        result_parts = []
        for block in translated_blocks:
            stripped = block.rstrip("\n")
            if stripped:  # Skip empty blocks
                result_parts.append(stripped)
        
        return "\n\n".join(result_parts) + "\n"

    def _reconstruct_block(
        self, block: DocumentBlock, translated_texts: List[str]
    ) -> str:
        """Reconstruct a block with translated content."""
        if block.block_type == "heading":
            # Reconstruct heading
            prefix = "#" * block.level
            text = translated_texts[0] if translated_texts else ""
            return f"{prefix} {text}\n"

        elif block.block_type == "paragraph":
            # Simple paragraph
            return "\n".join(translated_texts) + "\n"

        elif block.block_type in ("fence", "code_block"):
            # Keep original (code blocks are not translated)
            return block.raw_content

        elif block.block_type == "list":
            # Reconstruct list - this is a simplified approach
            # For complex lists, we'd need to track the original structure
            lines = block.raw_content.split("\n")
            result_lines = []
            text_idx = 0

            for line in lines:
                if line.strip().startswith(("-", "*", "+")) or (
                    len(line.strip()) > 0 and line.strip()[0].isdigit()
                ):
                    # This is a list item
                    # Find the marker
                    import re

                    match = re.match(r"^(\s*)([-*+]|\d+\.)\s+", line)
                    if match and text_idx < len(translated_texts):
                        prefix = match.group(0)
                        result_lines.append(f"{prefix}{translated_texts[text_idx]}")
                        text_idx += 1
                    else:
                        result_lines.append(line)
                else:
                    result_lines.append(line)

            return "\n".join(result_lines)

        elif block.block_type == "table":
            # Reconstruct table - simplified approach
            # For proper table handling, we'd need to track cell positions
            return self._reconstruct_table(block.raw_content, translated_texts)

        elif block.block_type == "blockquote":
            # Reconstruct blockquote
            text = translated_texts[0] if translated_texts else ""
            lines = text.split("\n")
            return "\n".join(f"> {line}" for line in lines) + "\n"

        elif block.block_type == "hr":
            # Horizontal rule - add blank line after for proper Markdown rendering
            return "---\n\n"

        else:
            # Default: return original
            return block.raw_content

    def _reconstruct_table(self, raw_content: str, translated_texts: List[str]) -> str:
        """Reconstruct a table with translated cell content."""
        import re

        lines = raw_content.split("\n")
        result_lines = []
        text_idx = 0

        for line in lines:
            # Skip separator line
            if re.match(r"^\s*\|?\s*[-:]+", line):
                result_lines.append(line)
                continue

            # Process cells
            cells = re.split(r"\|", line)
            new_cells = []

            for cell in cells:
                cell_stripped = cell.strip()
                if cell_stripped and text_idx < len(translated_texts):
                    # Replace with translated text, preserving spacing
                    leading = len(cell) - len(cell.lstrip())
                    trailing = len(cell) - len(cell.rstrip())
                    new_cell = " " * leading + translated_texts[text_idx] + " " * max(1, trailing)
                    new_cells.append(new_cell)
                    text_idx += 1
                else:
                    new_cells.append(cell)

            result_lines.append("|".join(new_cells))

        return "\n".join(result_lines)

    def translate_directory(
        self,
        input_dir: str,
        output_dir: Optional[str] = None,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
        recursive: bool = True,
        dry_run: bool = False,
        show_progress: bool = True,
    ) -> List[TranslationResult]:
        """Translate all Markdown files in a directory.

        Args:
            input_dir: Input directory path
            output_dir: Output directory path. If None, files are placed alongside originals.
            source_lang: Source language code
            target_lang: Target language code
            recursive: Whether to process subdirectories
            dry_run: If True, don't actually translate
            show_progress: Show progress bar

        Returns:
            List of TranslationResult for each file
        """
        input_path = Path(input_dir)
        target = target_lang or self.config.default_target_lang

        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = None

        # Find all Markdown files
        pattern = "**/*.md" if recursive else "*.md"
        files = list(input_path.glob(pattern))

        results = []

        iterator = tqdm(files, desc="Translating files", disable=not show_progress)
        for file_path in iterator:
            # Compute output path
            if output_path:
                relative = file_path.relative_to(input_path)
                out_file = output_path / relative.parent / f"{file_path.stem}_{target}{file_path.suffix}"
            else:
                out_file = file_path.parent / f"{file_path.stem}_{target}{file_path.suffix}"

            result = self.translate_file(
                input_path=str(file_path),
                output_path=str(out_file),
                source_lang=source_lang,
                target_lang=target_lang,
                dry_run=dry_run,
            )
            results.append(result)

            if show_progress:
                status = "OK" if result.success else "FAIL"
                iterator.set_postfix({"file": file_path.name, "status": status})

        # Save cache at the end
        if self.memory:
            self.memory.save()

        return results
