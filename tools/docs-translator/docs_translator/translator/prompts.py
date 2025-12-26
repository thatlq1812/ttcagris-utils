"""System prompts for translation."""

from typing import List


class PromptBuilder:
    """Build system prompts for translation."""

    LANGUAGE_NAMES = {
        "vi": "Vietnamese",
        "en": "English",
        "ja": "Japanese",
        "th": "Thai",
        "id": "Indonesian",
        "ko": "Korean",
        "zh": "Chinese",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
    }

    LITERAL_TEMPLATE = """You are a professional technical documentation translator.
Translation style: LITERAL (word-for-word technical accuracy)

RULES:
1. Translate from {source_lang} to {target_lang}
2. Preserve EXACT technical meaning - no paraphrasing
3. NEVER translate these terms (keep them exactly as-is): {preserve_terms}
4. NEVER translate:
   - Requirement IDs (FR-01, NFR-P01, BR-001, US-001, etc.)
   - Technical terms in backticks (`variable`, `function_name`)
   - Code snippets and commands
   - URLs and file paths
   - Image paths and links
   - Service names, entity names in tables (Account, User, Farmer, etc.)
5. ALWAYS translate these common words:
   - "Description" -> appropriate translation in target language
   - "Active" -> appropriate translation (e.g., "Hoạt động" in Vietnamese)
   - "Status" -> appropriate translation
   - Table headers like "Item", "Value", "Document", "Audience"
6. Use formal, technical tone
7. Maintain sentence structure as close to original as possible
8. Keep all Markdown formatting intact (**, *, #, etc.)
9. Context: This is a {context} in technical documentation

CRITICAL: Only output the translated text. Do not add explanations or notes."""

    NATURAL_TEMPLATE = """You are a professional technical documentation translator.
Translation style: NATURAL (idiomatic, reader-friendly)

RULES:
1. Translate from {source_lang} to {target_lang}
2. Make translation sound natural to native {target_lang} speakers
3. NEVER translate these terms (keep them exactly as-is): {preserve_terms}
4. NEVER translate:
   - Requirement IDs (FR-01, NFR-P01, BR-001, US-001, etc.)
   - Technical terms in backticks (`variable`, `function_name`)
   - Code snippets and commands
   - URLs and file paths
   - Image paths and links
   - Service names, entity names in tables (Account, User, Farmer, etc.)
5. ALWAYS translate these common words:
   - "Description" -> appropriate translation in target language
   - "Active" -> appropriate translation (e.g., "Hoạt động" in Vietnamese)
   - "Status" -> appropriate translation
   - Table headers like "Item", "Value", "Document", "Audience"
6. Use conversational but professional tone
7. Prioritize readability and flow over literal accuracy
8. Keep all Markdown formatting intact (**, *, #, etc.)
9. Context: This is a {context} in user-facing documentation

CRITICAL: Only output the translated text. Do not add explanations or notes."""

    @classmethod
    def build_system_prompt(
        cls,
        source_lang: str,
        target_lang: str,
        preserve_terms: List[str],
        style: str = "literal",
        context: str = "paragraph",
    ) -> str:
        """Build system prompt for translation.

        Args:
            source_lang: Source language code (e.g., 'vi')
            target_lang: Target language code (e.g., 'en')
            preserve_terms: List of terms to never translate
            style: Translation style ('literal' or 'natural')
            context: Context type ('heading', 'paragraph', 'table_cell', etc.)

        Returns:
            Formatted system prompt
        """
        template = cls.LITERAL_TEMPLATE if style == "literal" else cls.NATURAL_TEMPLATE

        source_name = cls.LANGUAGE_NAMES.get(source_lang, source_lang)
        target_name = cls.LANGUAGE_NAMES.get(target_lang, target_lang)

        # Format preserve terms
        if preserve_terms:
            terms_str = ", ".join(f'"{term}"' for term in preserve_terms[:20])
            if len(preserve_terms) > 20:
                terms_str += f", ... ({len(preserve_terms) - 20} more)"
        else:
            terms_str = "(none specified)"

        return template.format(
            source_lang=source_name,
            target_lang=target_name,
            preserve_terms=terms_str,
            context=context,
        )

    @classmethod
    def build_user_prompt(cls, text: str) -> str:
        """Build user prompt (the text to translate).

        Args:
            text: Text to translate

        Returns:
            User prompt
        """
        return text

    @classmethod
    def build_batch_prompt(cls, texts: List[str], separator: str = "\n---SEPARATOR---\n") -> str:
        """Build prompt for batch translation.

        Args:
            texts: List of texts to translate
            separator: Separator between texts

        Returns:
            Combined prompt with instructions
        """
        combined = separator.join(texts)
        instruction = f"""Translate each section below. Sections are separated by "{separator.strip()}".
Keep the separators in your response exactly as they appear.

{combined}"""
        return instruction
