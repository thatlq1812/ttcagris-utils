# [TDD] AI Documentation Translator Tool

| Version | Date | Author | Status |
| --- | --- | --- | --- |
| 1.1.0 | 26 Dec 2024 | @Documentation Team | Ready for Implementation |

**Status**: Ready for Implementation

---

## 1. Overview

### 1.1 Purpose

Build an AI-powered documentation translation tool that automatically converts technical documentation between Vietnamese and English while preserving code blocks, technical terms, Markdown structure, and requirement IDs. This tool enables "Docs as Code" workflows for multilingual enterprise documentation management.

### 1.2 Scope

**In Scope**:
- Markdown file parsing and structure preservation
- AI-powered context-aware translation via LLM APIs
- Batch translation of entire documentation directories
- Preservation of code blocks, inline code, requirement IDs, image links
- Configuration for preserving custom technical terms
- Support for OpenAI, Gemini, and Claude APIs

**Out of Scope**:
- Translation of non-Markdown formats (Word, PDF)
- Real-time collaborative editing
- Translation memory database
- Human translator workflow integration
- Browser extension or GUI application

### 1.3 Related Documents

- [confluence_rules.md](confluence_rules.md) - Documentation standards
- [documentation_rules.md](documentation_rules.md) - Repository documentation rules
- **Templates**: See [templates/](templates/) directory

---

## 2. Background

### 2.1 Current System

Documentation is manually translated by team members, leading to:
- Inconsistent terminology across documents
- High maintenance overhead (2-4 hours per document)
- Delayed translations causing version drift
- Broken Markdown structure after manual edits
- Accidentally translated code blocks and technical terms

### 2.2 Problem Statement

**Technical Challenges**:
1. **Structure Preservation**: Traditional translation tools (Google Translate) break Markdown tables, code blocks, and links
2. **Context Awareness**: Need to preserve technical terms like "User Service", "API Gateway", "gRPC"
3. **Selective Translation**: Must distinguish between translatable content and code/configuration
4. **Batch Processing**: Need to translate entire `docs/` directories efficiently

**Business Impact**:
- Delayed documentation releases block international stakeholder reviews
- Inconsistent translations reduce document quality and trust
- Manual translation costs scale linearly with document count

### 2.3 Goals

- **Primary**: Automate 90% of documentation translation with structure preservation
- **Efficiency**: Reduce translation time from 2-4 hours to 5-10 minutes per document
- **Quality**: Maintain 95%+ translation accuracy with preserved technical terms
- **Scalability**: Support batch translation of 50+ documents in single run

---

## 3. Functional Requirements Summary

### 3.1 Must Have (P0)

- Parse Markdown files into Abstract Syntax Tree (AST)
- Preserve code blocks, inline code, requirement IDs during translation
- Integrate with OpenAI/Gemini/Claude APIs
- Support Vietnamese ↔ English bidirectional translation
- Batch process entire directories

### 3.2 Should Have (P1)

- Configuration file for custom term preservation
- Progress bar and logging during batch translation
- Dry-run mode to preview changes
- Rollback capability

### 3.3 Nice to Have (P2)

- Translation quality metrics
- Support for additional languages (Thai, Indonesian)
- GitHub Actions integration for CI/CD

---

## 4. System Architecture

### 4.1 High-Level Architecture

```
┌─────────────┐
│   CLI Tool  │
│   (Python)  │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────┐
│         Core Pipeline                │
│                                      │
│  Parser → Traverser → Translator    │
│            ↓              ↓          │
│         AST Nodes     AI API        │
│            ↓                         │
│         Renderer                     │
└──────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│  Output MD  │
│   Files     │
└─────────────┘
```

### 4.2 Component Diagram

```
┌────────────────────────────────────────────────┐
│              CLI Interface                     │
│   (argparse: --source, --target, --dry-run)   │
└────────────────┬───────────────────────────────┘
                 │
    ┌────────────▼────────────┐
    │   Configuration Manager  │
    │  (Load preserve_terms)   │
    └────────────┬─────────────┘
                 │
    ┌────────────▼─────────────┐
    │   Markdown Parser        │
    │  (markdown-it-py/mistune)│
    └────────────┬──────────────┘
                 │
                 ▼
         ┌──────────────┐
         │   AST Tree   │
         └──────┬───────┘
                │
    ┌───────────▼──────────────┐
    │   AST Traverser          │
    │  (Classify nodes)        │
    │   - CodeBlock: SKIP      │
    │   - Text: TRANSLATE      │
    │   - RequirementID: KEEP  │
    └───────────┬──────────────┘
                │
    ┌───────────▼──────────────┐
    │   AI Translator          │
    │  (OpenAI/Gemini/Claude)  │
    │  with System Prompt      │
    └───────────┬──────────────┘
                │
    ┌───────────▼──────────────┐
    │   Markdown Renderer      │
    │  (Reconstruct structure) │
    └───────────┬──────────────┘
                │
                ▼
         ┌──────────────┐
         │  Output File │
         └──────────────┘
```

### 4.3 Deployment Architecture

**Local Development**:
```
User Machine
├── Python 3.10+
├── docs-translator/ (tool directory)
└── docs/confluence/ (target documents)
```

**CI/CD Integration** (Future):
```
GitHub Actions
├── Trigger: Pull Request to docs/
├── Run: docs-translator --source vi --target en
└── Create: Automated commit with translations
```

---

## 5. Detailed Design

### 5.1 Component A: Markdown Parser

#### 5.1.1 Responsibility

Convert Markdown text into Abstract Syntax Tree (AST) for precise structure-aware processing.

#### 5.1.2 Interfaces

**Library Choice**: `markdown-it-py` (Python port of markdown-it)

**Why not Regex?**
- Regex fails on nested structures (lists inside tables)
- Cannot handle edge cases (code blocks with markdown inside)
- AST provides guaranteed correctness

**Public API**:
```python
class MarkdownParser:
    def parse(self, md_content: str) -> List[Token]:
        """
        Parse Markdown into token stream.
        
        Returns:
            List of tokens with type, content, markup metadata
        """
        pass
```

**Token Types**:
```python
@dataclass
class Token:
    type: str  # 'fence', 'code_inline', 'text', 'heading_open', etc.
    content: str
    markup: str  # '```', '`', '#', etc.
    info: str  # Language for code blocks ('python', 'go')
    children: List[Token]
```

#### 5.1.3 Internal Structure

```
parser/
├── __init__.py
├── markdown_parser.py     # Main parser class
└── token_types.py         # Token dataclass definitions
```

### 5.2 Component B: AST Traverser

#### 5.2.1 Responsibility

Walk through AST nodes and classify each for translation decision.

#### 5.2.2 Classification Rules

| Node Type | Action | Detection Pattern |
| --- | --- | --- |
| `fence` (Code Block) | SKIP | Triple backticks ``` |
| `code_inline` | SKIP | Single backticks ` |
| `text` with Requirement ID | KEEP PATTERN | Regex: `(FR\|BR\|NFR\|TC\|M)-[A-Z0-9]+` |
| `image` | TRANSLATE ALT, KEEP URL | `![alt](url)` structure |
| `link` | TRANSLATE TEXT, KEEP URL | `[text](url)` structure |
| `heading` | TRANSLATE | Lines starting with `#` |
| `paragraph` | TRANSLATE | Normal text blocks |
| `table` | TRANSLATE CELLS | Preserve `|` delimiters |

#### 5.2.3 Interfaces

```python
class ASTTraverser:
    def __init__(self, preserve_terms: List[str]):
        self.preserve_terms = preserve_terms
        
    def traverse(self, tokens: List[Token]) -> List[TranslationUnit]:
        """
        Walk AST and create translation units.
        
        Returns:
            List of units marked SKIP, TRANSLATE, or PRESERVE
        """
        pass
        
    def is_requirement_id(self, text: str) -> bool:
        """Check if text matches requirement ID pattern."""
        return bool(re.match(r'(FR|BR|NFR|TC|M)-[A-Z0-9]+', text))
```

**TranslationUnit Model**:
```python
@dataclass
class TranslationUnit:
    action: Literal['SKIP', 'TRANSLATE', 'PRESERVE']
    original_text: str
    context: str  # 'heading', 'table_cell', 'paragraph'
    preserve_reason: Optional[str]  # 'code_block', 'requirement_id', etc.
```

### 5.3 Component C: AI Translator

#### 5.3.1 Responsibility

Send translation units to LLM API with context-aware system prompts.

#### 5.3.2 Interfaces

```python
class AITranslator:
    def __init__(self, api_provider: str, api_key: str):
        """
        Args:
            api_provider: 'openai' | 'gemini' | 'claude'
            api_key: API key for provider
        """
        self.client = self._init_client(api_provider, api_key)
        
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        preserve_terms: List[str],
        context: str
    ) -> str:
        """
        Translate text with preservation rules.
        
        Args:
            text: Text to translate
            source_lang: 'vi' | 'en'
            target_lang: 'vi' | 'en'
            preserve_terms: Technical terms to not translate
            context: 'heading' | 'paragraph' | 'table_cell'
            
        Returns:
            Translated text
        """
        pass
```

#### 5.3.3 System Prompt Engineering

**Translation Style Integration**:

System prompts are dynamically generated based on `translation_style` configuration.

**Literal Mode Prompt** (for technical documents):
```python
LITERAL_PROMPT = """You are a professional technical documentation translator.
Translation style: LITERAL (word-for-word technical accuracy)

RULES:
1. Translate from {source_lang} to {target_lang}
2. Preserve EXACT technical meaning - no paraphrasing
3. NEVER translate these terms: {preserve_terms}
4. NEVER translate:
   - Requirement IDs (FR-01, NFR-P01, BR-001)
   - Technical terms in backticks (`variable`)
   - Code snippets
   - URLs
5. Use formal, technical tone
6. Maintain sentence structure as close to original as possible
7. Context: This is a {context} in technical documentation

Examples:
- "Hệ thống phải hỗ trợ User Service" → "System must support User Service"
- "Cài đặt `npm install`" → "Install `npm install`"
- "API trả về status code 200" → "API returns status code 200"
"""
```

**Natural Mode Prompt** (for user-facing documents):
```python
NATURAL_PROMPT = """You are a professional technical documentation translator.
Translation style: NATURAL (idiomatic, reader-friendly)

RULES:
1. Translate from {source_lang} to {target_lang}
2. Make translation sound natural to native {target_lang} speakers
3. NEVER translate these terms: {preserve_terms}
4. NEVER translate:
   - Requirement IDs (FR-01, NFR-P01, BR-001)
   - Technical terms in backticks (`variable`)
   - Code snippets
   - URLs
5. Use conversational but professional tone
6. Prioritize readability and flow over literal accuracy
7. Context: This is a {context} in user-facing documentation

Examples:
- "Để cài đặt, bạn chỉ cần chạy lệnh sau" → "To install, simply run the following command"
- "Quá trình này có thể mất vài phút" → "This process may take a few minutes"
- "Nếu gặp lỗi, hãy kiểm tra logs" → "If you encounter errors, check the logs"
"""
```

**Google Gemini Implementation** (leverages `system_instruction`):
```python
from google import generativeai as genai

class GeminiTranslator:
    def __init__(self, api_key: str, model: str, translation_style: str):
        genai.configure(api_key=api_key)
        
        # Select system instruction based on style
        system_instruction = (
            LITERAL_PROMPT if translation_style == "literal"
            else NATURAL_PROMPT
        )
        
        self.model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_instruction.format(
                source_lang="Vietnamese",
                target_lang="English",
                preserve_terms=", ".join(PRESERVE_TERMS),
                context="paragraph"
            )
        )
    
    def translate(self, text: str) -> str:
        response = self.model.generate_content(text)
        return response.text
```

**OpenAI Implementation** (uses messages array):
```python
import openai

class OpenAITranslator:
    def __init__(self, api_key: str, model: str, translation_style: str):
        openai.api_key = api_key
        self.model = model
        
        self.system_prompt = (
            LITERAL_PROMPT if translation_style == "literal"
            else NATURAL_PROMPT
        )
    
    def translate(self, text: str) -> str:
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
```
```

**API Call Structure**:
```python
# OpenAI Example
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text_to_translate}
    ],
    temperature=0.3,  # Lower temperature for consistency
    max_tokens=2000
)
```

### 5.4 Component D: Markdown Renderer

#### 5.4.1 Responsibility

Reconstruct Markdown file from translated AST nodes, preserving original formatting.

#### 5.4.2 Interfaces

```python
class MarkdownRenderer:
    def render(
        self,
        original_tokens: List[Token],
        translated_units: List[TranslationUnit]
    ) -> str:
        """
        Rebuild Markdown from tokens and translations.
        
        Returns:
            Complete Markdown document as string
        """
        pass
        
    def render_table(self, tokens: List[Token]) -> str:
        """Special handling for table structure."""
        pass
        
    def render_heading(self, level: int, text: str) -> str:
        """Reconstruct heading with correct # count."""
        return f"{'#' * level} {text}\n\n"
```

---

## 6. Data Model

### 6.1 Configuration File

**config.yaml**:
```yaml
translation:
  api_provider: "gemini"  # gemini (recommended) | openai | claude
  api_key_env: "GOOGLE_API_KEY"  # or OPENAI_API_KEY, ANTHROPIC_API_KEY
  model: "gemini-2.0-flash"  # Auto-selected via setup wizard
  temperature: 0.3
  max_tokens: 2000
  translation_style: "literal"  # literal | natural

preserve_terms:
  # Technical terms to never translate
  - "User Service"
  - "API Gateway"
  - "gRPC"
  - "PostgreSQL"
  - "Redis"
  - "Docker"
  - "Kubernetes"
  - "AgriOS"
  - "CAS"  # Centre Auth Service
  - "CQRS"
  - "Clean Architecture"

languages:
  source: "vi"
  target: "en"

directories:
  input: "docs/confluence"
  output: "docs/confluence/translated"
  
logging:
  level: "INFO"
  file: "translation.log"
```

**Translation Style Modes**:

| Mode | Description | Best For | System Instruction |
| --- | --- | --- | --- |
| `literal` | Word-for-word technical accuracy | API specs, code docs, technical constraints | "Translate precisely, preserve all technical terms, maintain formal tone" |
| `natural` | Idiomatic, reader-friendly | User guides, process docs, tutorials | "Translate naturally for native speakers, maintain readability and flow" |

### 6.2 Translation Memory (Gold Standard for Cost Efficiency)

**Purpose**: Incremental translation - only translate changed blocks, not entire files. This is the industry standard for professional CAT (Computer Assisted Translation) tools.

**Problem**: Without this, editing 1 paragraph in a 50-page document requires re-translating all 50 pages ($$$).

**Solution**: Granular Hashing - split document into blocks, hash each block, store translations.

**Architecture**:
```
Document
  ├── Block 1: Heading "Introduction" → Hash: abc123 → Translation cached
  ├── Block 2: Paragraph "System must..." → Hash: def456 → Translation cached
  ├── Block 3: Code Block → Hash: ghi789 → Translation cached
  └── Block 4: Paragraph "Updated text" → Hash: jkl012 → NEW! Call API
```

**On next translation**:
- Blocks 1-3: Hash matches → Use cached translation ($0)
- Block 4: Hash changed → Call API (pay only for this block)

**Result**: 99% cost savings on incremental updates.

**Data Structure**:
```json
{
  "version": "2.0",
  "memory": {
    "abc123def456": {
      "source_text": "System must support User Service",
      "source_lang": "vi",
      "target_lang": "en",
      "target_text": "System must support User Service",
      "context_type": "paragraph",
      "timestamp": "2024-12-26T10:00:00Z",
      "file_path": "docs/srs.md",
      "block_index": 2
    }
  },
  "stats": {
    "total_blocks": 1500,
    "cache_hits": 1485,
    "cache_misses": 15,
    "cost_saved": "$14.85"
  }
}
```

**Implementation**:
```python
import hashlib
import json
from typing import Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TranslationBlock:
    source_text: str
    target_text: str
    source_lang: str
    target_lang: str
    context_type: str  # 'heading', 'paragraph', 'table_cell'
    timestamp: str
    file_path: str
    block_index: int

class TranslationMemoryManager:
    """Intelligent translation memory with granular hashing."""
    
    def __init__(self, db_path: str = ".translation_memory.json"):
        self.db_path = db_path
        self.memory = self._load()
        self.stats = {"hits": 0, "misses": 0, "cost_saved": 0.0}
    
    def _compute_hash(
        self,
        source_text: str,
        context_type: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """Generate hash key for translation lookup.
        
        Include context_type to avoid wrong translations:
        - "Heading" vs "Paragraph" may need different translation style
        - Table cells are more concise than paragraphs
        """
        content = f"{source_text}|{context_type}|{source_lang}|{target_lang}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def get_translation(
        self,
        source_text: str,
        context_type: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """Retrieve cached translation if exists.
        
        Returns:
            Cached translation or None if not found
        """
        key = self._compute_hash(source_text, context_type, source_lang, target_lang)
        
        if key in self.memory:
            self.stats["hits"] += 1
            # Estimate cost saved (GPT-4: ~$0.01 per 1000 tokens)
            tokens_saved = len(source_text) // 4
            self.stats["cost_saved"] += (tokens_saved / 1000) * 0.01
            return self.memory[key]["target_text"]
        
        self.stats["misses"] += 1
        return None
    
    def save_translation(
        self,
        source_text: str,
        target_text: str,
        context_type: str,
        source_lang: str,
        target_lang: str,
        file_path: str,
        block_index: int
    ) -> None:
        """Store translation in memory for future use."""
        key = self._compute_hash(source_text, context_type, source_lang, target_lang)
        
        self.memory[key] = {
            "source_text": source_text,
            "target_text": target_text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "context_type": context_type,
            "timestamp": datetime.utcnow().isoformat(),
            "file_path": file_path,
            "block_index": block_index
        }
    
    def persist(self) -> None:
        """Save memory to disk."""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump({
                "version": "2.0",
                "memory": self.memory,
                "stats": self.stats
            }, f, indent=2, ensure_ascii=False)
    
    def _load(self) -> dict:
        """Load memory from disk."""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("memory", {})
        except FileNotFoundError:
            return {}
    
    def get_cache_stats(self) -> dict:
        """Get cache performance statistics."""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "cache_hits": self.stats["hits"],
            "cache_misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.1f}%",
            "cost_saved": f"${self.stats['cost_saved']:.2f}",
            "total_entries": len(self.memory)
        }
```

**Usage in Translator**:
```python
class Translator:
    def __init__(self, config: Config):
        self.tm = TranslationMemoryManager()
    
    def translate_block(
        self,
        source_text: str,
        context_type: str,
        file_path: str,
        block_index: int
    ) -> str:
        # Check cache first
        cached = self.tm.get_translation(
            source_text,
            context_type,
            self.source_lang,
            self.target_lang
        )
        
        if cached:
            logger.debug(f"Cache HIT for block {block_index}")
            return cached
        
        # Cache miss - call API
        logger.info(f"Cache MISS for block {block_index} - calling API")
        translated = self.api_translate(source_text)
        
        # Save to memory
        self.tm.save_translation(
            source_text,
            translated,
            context_type,
            self.source_lang,
            self.target_lang,
            file_path,
            block_index
        )
        
        return translated
    
    def finish(self):
        """Called at end of translation session."""
        self.tm.persist()
        stats = self.tm.get_cache_stats()
        print(f"Translation Memory Stats: {stats}")
```

**Benefits**:
- **99% Cost Reduction** on incremental updates
- **10x Faster** re-translation of existing documents
- **Context-Aware**: Different translations for headings vs paragraphs
- **Portable**: `.translation_memory.json` can be shared across team
- **Audit Trail**: Track when/where translations were used

---

## 6.3 Recommended Workflow: Standardize → Translate

**Principle**: "Garbage In, Garbage Out" - Clean input ensures clean output.

### 6.3.1 Two-Step Process

**Problem**: If source Markdown is messy (wrong heading levels, misaligned tables, code blocks without language tags), the parser will misinterpret structure, leading to broken translations.

**Solution**: Always standardize before translating.

```
┌─────────────────┐
│  Messy Source   │
│  Markdown       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 1:         │
│ Standardization │  ← Use AI agent or linter
│ (Format Fix)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Clean Source   │
│  Markdown       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 2:         │
│ Translation     │  ← This tool
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Clean Target    │
│ Markdown        │
└─────────────────┘
```

### 6.3.2 Step 1: Standardization Agent

**Input**: Messy Markdown file

**Common Issues**:
- Inconsistent heading levels (`###` followed by `#`)
- Tables with misaligned pipes
- Code blocks missing language identifiers
- Mixed list styles (- and *)
- Inconsistent spacing

**Agent Prompt** (for AI-based standardization):
```markdown
You are a Markdown standardization agent. Fix this document:

RULES:
1. Use ATX headings (# ## ###), never Setext (underlines)
2. Fix heading hierarchy (no skipping levels)
3. Align table pipes properly
4. Add language tags to code blocks (```python, ```go, etc.)
5. Use consistent list markers (- only)
6. Follow documentation_rules.md standards
7. DO NOT change content, only format

Document:
{content}
```

**Or use Linter** (automated, faster):
```bash
# Using markdownlint-cli
markdownlint --fix docs/confluence/*.md

# Using mdformat
mdformat docs/confluence/*.md
```

### 6.3.3 Step 2: Translation

**Input**: Clean, standardized Markdown

```bash
# Now safe to translate
docs-translator translate \
  --file docs/confluence/clean_source.md \
  --source vi \
  --target en
```

**Output**: Clean target language Markdown with preserved structure

### 6.3.4 CLI Integration

**Option 1: Manual two-step**:
```bash
# Step 1: Standardize
mdformat docs/source.md

# Step 2: Translate
docs-translator translate --file docs/source.md ...
```

**Option 2: Built-in flag** (future enhancement):
```bash
# Automatic standardization before translation
docs-translator translate \
  --file docs/source.md \
  --standardize \
  --source vi \
  --target en
```

### 6.3.5 Multi-language Support

**Vietnamese → English**:
```bash
docs-translator translate --source vi --target en --file doc.md
```

**English → Japanese**:
```bash
docs-translator translate --source en --target ja --file doc.md
```

**Vietnamese → Thai** (via English pivot):
```bash
# Step 1: vi → en
docs-translator translate --source vi --target en --file doc.md

# Step 2: en → th
docs-translator translate --source en --target th --file doc_en.md
```

**Supported Languages** (configurable via System Prompt):
- Vietnamese (vi)
- English (en)
- Japanese (ja)
- Thai (th)
- Indonesian (id)
- Korean (ko)
- Chinese (zh)

**Implementation**: Simply change `{target_lang}` variable in System Prompt (Section 5.3.3).

---

## 7. API Design

**Note**: This is a CLI tool, not a web service. API here refers to Python module interfaces.

### 7.1 CLI Interface

#### 7.1.0 Interactive Setup Wizard (First-time Configuration)

**Purpose**: Simplify initial setup with guided configuration instead of manual YAML editing.

**Command**:
```bash
docs-translator configure
```

**Interactive Flow**:
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Documentation Translator Setup Wizard  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Welcome! Let's configure your translation environment.

[?] Select API Provider:
  ❯ Google Gemini (Recommended - Fast & Affordable)
    OpenAI (GPT-4 - High Quality)
    Anthropic Claude (Balanced)

[?] Enter Google API Key: ********************************
    Get your key: https://aistudio.google.com/app/apikey

⏳ Validating API key...
✓ API key valid!

⏳ Fetching available models...

[?] Select Translation Model:
  ❯ gemini-2.0-flash (Recommended)
    └─ Fast, cost-efficient (~$0.075/1M tokens)
    └─ Best for: Large batches, drafts
    
    gemini-1.5-pro
    └─ High quality (~$1.25/1M tokens)
    └─ Best for: Production releases
    
    gemini-1.0-pro
    └─ Legacy model

[?] Translation Style:
  ❯ Literal (Technical accuracy - for API docs, code)
    Natural (Idiomatic - for user guides, tutorials)

[?] Primary language pair:
    Source: [vi] Vietnamese
    Target: [en] English

✓ Configuration saved to config.yaml

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Setup Complete!                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

You're ready to translate! Try:
  docs-translator translate --file sample.md --target en

For help: docs-translator --help
```

**Implementation Details**:

```python
import inquirer
from google import generativeai as genai
from typing import List, Dict

class SetupWizard:
    """Interactive configuration wizard."""
    
    # Static enrichment layer for model metadata
    MODEL_METADATA = {
        "gemini-2.0-flash": {
            "description": "Fast, cost-efficient",
            "cost": "~$0.075/1M input tokens",
            "best_for": "Large batches, drafts",
            "recommended": True
        },
        "gemini-1.5-pro": {
            "description": "High quality",
            "cost": "~$1.25/1M input tokens",
            "best_for": "Production releases",
            "recommended": False
        },
        "gpt-4": {
            "description": "Highest quality",
            "cost": "~$10/1M input tokens",
            "best_for": "Critical documents",
            "recommended": False
        },
        "gpt-3.5-turbo": {
            "description": "Balanced",
            "cost": "~$0.50/1M input tokens",
            "best_for": "General purpose",
            "recommended": False
        }
    }
    
    def run(self) -> Dict:
        """Run interactive setup wizard."""
        console.print("\n[bold cyan]Documentation Translator Setup Wizard[/bold cyan]\n")
        
        # Step 1: Select provider
        provider = self._select_provider()
        
        # Step 2: Get API key
        api_key = self._get_api_key(provider)
        
        # Step 3: Validate and fetch models
        models = self._fetch_models(provider, api_key)
        
        # Step 4: Select model
        model = self._select_model(models)
        
        # Step 5: Select translation style
        style = self._select_translation_style()
        
        # Step 6: Language pair
        source_lang, target_lang = self._select_languages()
        
        # Save configuration
        config = {
            "translation": {
                "api_provider": provider,
                "api_key_env": self._get_key_env_var(provider),
                "model": model,
                "translation_style": style
            },
            "languages": {
                "source": source_lang,
                "target": target_lang
            }
        }
        
        self._save_config(config)
        console.print("\n✓ [green]Configuration saved to config.yaml[/green]\n")
        
        return config
    
    def _fetch_models(self, provider: str, api_key: str) -> List[Dict]:
        """Fetch and enrich model list from provider API."""
        console.print("⏳ Fetching available models...")
        
        if provider == "gemini":
            genai.configure(api_key=api_key)
            raw_models = genai.list_models()
            
            # Filter: Only models that support generateContent
            filtered = [
                m for m in raw_models
                if 'generateContent' in m.supported_generation_methods
            ]
            
            # Enrich with metadata
            enriched = []
            for model in filtered:
                model_id = model.name.split('/')[-1]  # Extract ID
                metadata = self.MODEL_METADATA.get(model_id, {})
                
                enriched.append({
                    "id": model_id,
                    "display_name": model.display_name,
                    "description": metadata.get("description", "No description"),
                    "cost": metadata.get("cost", "Unknown cost"),
                    "best_for": metadata.get("best_for", ""),
                    "recommended": metadata.get("recommended", False)
                })
            
            return enriched
        
        elif provider == "openai":
            # Similar implementation for OpenAI
            pass
    
    def _select_model(self, models: List[Dict]) -> str:
        """Display enriched model list with recommendation."""
        choices = []
        for model in models:
            prefix = "❯ " if model["recommended"] else "  "
            label = f"{prefix}{model['id']}"
            if model["recommended"]:
                label += " (Recommended)"
            label += f"\n    └─ {model['description']} ({model['cost']})"
            label += f"\n    └─ Best for: {model['best_for']}"
            choices.append((label, model["id"]))
        
        questions = [
            inquirer.List('model',
                message="Select Translation Model",
                choices=choices
            )
        ]
        
        answers = inquirer.prompt(questions)
        return answers['model']
    
    def _select_translation_style(self) -> str:
        """Select translation style mode."""
        questions = [
            inquirer.List('style',
                message="Translation Style",
                choices=[
                    ('Literal (Technical accuracy - for API docs, code)', 'literal'),
                    ('Natural (Idiomatic - for user guides, tutorials)', 'natural')
                ]
            )
        ]
        answers = inquirer.prompt(questions)
        return answers['style']
```

**Skip Wizard** (for automation/CI):
```bash
# Manual config via environment variables
export GOOGLE_API_KEY="your-key"
docs-translator translate \
    --provider gemini \
    --model gemini-2.0-flash \
    --file doc.md
```

#### 7.1.0.1 Persistent Configuration Management

**Problem**: Users should not re-enter API keys or re-select models every time they run the tool.

**Solution**: Configuration hierarchy with automatic persistence.

**Configuration File Locations** (Priority Order):
```
1. ./docs-translator.yaml     (Project-specific, highest priority)
2. ~/.docs-translator/config.yaml  (User global config)
3. Environment variables       (CI/CD override)
4. Built-in defaults           (Fallback)
```

**Configuration File Structure** (`docs-translator.yaml`):
```yaml
# docs-translator.yaml - Project Configuration
# Generated by: docs-translator configure
# Last updated: 2024-12-26 14:30:00

version: "1.0"

# API Provider Settings
providers:
  active: "gemini"  # Currently active provider
  
  gemini:
    api_key_source: "env"  # env | file | keyring
    api_key_env: "GOOGLE_API_KEY"
    model: "gemini-2.0-flash"
    validated_at: "2024-12-26T14:30:00Z"
  
  openai:
    api_key_source: "env"
    api_key_env: "OPENAI_API_KEY"
    model: "gpt-4"
    validated_at: null  # Not yet configured
  
  claude:
    api_key_source: "env"
    api_key_env: "ANTHROPIC_API_KEY"
    model: "claude-3-opus-20240229"
    validated_at: null

# Translation Settings
translation:
  style: "literal"  # literal | natural
  temperature: 0.3
  max_tokens: 4096
  
# Language Settings
languages:
  default_source: "vi"
  default_target: "en"
  supported:
    - code: "vi"
      name: "Vietnamese"
    - code: "en"
      name: "English"
    - code: "ja"
      name: "Japanese"
    - code: "th"
      name: "Thai"

# Preserve Terms (never translate these)
preserve_terms:
  - "User Service"
  - "API Gateway"
  - "gRPC"
  - "PostgreSQL"
  - "Redis"
  - "Docker"
  - "Kubernetes"
  - "AgriOS"
  - "CAS"
  - "CQRS"

# Directory Settings
directories:
  input: "docs/confluence"
  output: "docs/confluence/translated"
  cache: ".translation_cache"

# Advanced Settings
advanced:
  rate_limit_tokens_per_minute: 90000
  max_retries: 3
  timeout_seconds: 60
  parallel_files: 4
```

**API Key Storage Options**:

| Method | Security | Ease of Use | Best For |
| --- | --- | --- | --- |
| Environment Variable | Medium | Easy | CI/CD, Containers |
| System Keyring | High | Medium | Developer machines |
| Encrypted File | High | Hard | Enterprise, Air-gapped |

**Implementation - Configuration Manager**:
```python
import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from datetime import datetime
import keyring  # System credential storage

@dataclass
class ProviderConfig:
    """Configuration for a single API provider."""
    api_key_source: str = "env"  # env | file | keyring
    api_key_env: str = ""
    model: str = ""
    validated_at: Optional[str] = None
    
    def get_api_key(self, provider_name: str) -> Optional[str]:
        """Retrieve API key based on configured source."""
        if self.api_key_source == "env":
            return os.getenv(self.api_key_env)
        elif self.api_key_source == "keyring":
            return keyring.get_password("docs-translator", provider_name)
        elif self.api_key_source == "file":
            key_file = Path.home() / ".docs-translator" / f"{provider_name}.key"
            if key_file.exists():
                return key_file.read_text().strip()
        return None
    
    def save_api_key(self, provider_name: str, api_key: str, source: str = "keyring"):
        """Securely save API key."""
        self.api_key_source = source
        
        if source == "keyring":
            keyring.set_password("docs-translator", provider_name, api_key)
        elif source == "env":
            self.api_key_env = f"{provider_name.upper()}_API_KEY"
            # Remind user to set env var
            print(f"Set environment variable: export {self.api_key_env}='{api_key}'")
        elif source == "file":
            key_dir = Path.home() / ".docs-translator"
            key_dir.mkdir(exist_ok=True)
            key_file = key_dir / f"{provider_name}.key"
            key_file.write_text(api_key)
            key_file.chmod(0o600)  # Read/write only for owner

@dataclass
class TranslatorConfig:
    """Main configuration class."""
    version: str = "1.0"
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)
    active_provider: str = "gemini"
    translation_style: str = "literal"
    default_source_lang: str = "vi"
    default_target_lang: str = "en"
    preserve_terms: List[str] = field(default_factory=list)
    
    CONFIG_LOCATIONS = [
        Path("./docs-translator.yaml"),
        Path.home() / ".docs-translator" / "config.yaml"
    ]
    
    @classmethod
    def load(cls) -> "TranslatorConfig":
        """Load configuration from file hierarchy."""
        for config_path in cls.CONFIG_LOCATIONS:
            if config_path.exists():
                with open(config_path) as f:
                    data = yaml.safe_load(f)
                return cls._from_dict(data, config_path)
        
        # No config found - return defaults
        return cls()
    
    def save(self, path: Optional[Path] = None):
        """Save configuration to file."""
        if path is None:
            # Default: save to project directory
            path = Path("./docs-translator.yaml")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            yaml.dump(self._to_dict(), f, default_flow_style=False, 
                      allow_unicode=True, sort_keys=False)
        
        print(f"✓ Configuration saved to {path}")
    
    def get_active_provider(self) -> ProviderConfig:
        """Get currently active provider configuration."""
        return self.providers.get(self.active_provider, ProviderConfig())
    
    def switch_provider(self, provider_name: str):
        """Switch to a different API provider."""
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not configured")
        
        self.active_provider = provider_name
        self.save()
        print(f"✓ Switched to {provider_name}")
```

**Quick Commands for Configuration**:
```bash
# First-time setup (interactive wizard)
docs-translator configure

# View current configuration
docs-translator config show

# Switch provider quickly
docs-translator config set provider openai

# Switch model
docs-translator config set model gpt-4

# Add preserve term
docs-translator config add-term "My Custom Term"

# Update API key for a provider
docs-translator config set-key gemini
# → Prompts for new API key securely

# Export config for team sharing (without secrets)
docs-translator config export --no-secrets > team-config.yaml

# Import team config
docs-translator config import team-config.yaml
```

#### 7.1.0.2 Enhanced Model Selection

**Dynamic Model Discovery**:

The tool automatically fetches available models from each provider's API, ensuring users always see current options.

```python
from typing import List, Dict, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class ModelInfo:
    """Unified model information across providers."""
    id: str
    display_name: str
    provider: str
    description: str
    input_cost_per_1m: float  # USD per 1M input tokens
    output_cost_per_1m: float  # USD per 1M output tokens
    context_window: int  # Max tokens
    best_for: str
    recommended: bool = False
    supports_system_instruction: bool = True

class ModelRegistry:
    """Registry of known models with metadata."""
    
    # Static metadata for enrichment (API doesn't provide costs)
    KNOWN_MODELS = {
        # Google Gemini
        "gemini-2.0-flash": ModelInfo(
            id="gemini-2.0-flash",
            display_name="Gemini 1.5 Flash",
            provider="gemini",
            description="Fast, cost-efficient, large context",
            input_cost_per_1m=0.075,
            output_cost_per_1m=0.30,
            context_window=1000000,
            best_for="Large batches, drafts, cost-sensitive",
            recommended=True
        ),
        "gemini-1.5-pro": ModelInfo(
            id="gemini-1.5-pro",
            display_name="Gemini 1.5 Pro",
            provider="gemini",
            description="High quality, balanced",
            input_cost_per_1m=1.25,
            output_cost_per_1m=5.00,
            context_window=1000000,
            best_for="Production releases, complex documents"
        ),
        "gemini-2.0-flash": ModelInfo(
            id="gemini-2.0-flash",
            display_name="Gemini 2.0 Flash",
            provider="gemini",
            description="Latest generation, improved reasoning",
            input_cost_per_1m=0.10,
            output_cost_per_1m=0.40,
            context_window=1000000,
            best_for="Complex technical translations"
        ),
        
        # OpenAI
        "gpt-4o": ModelInfo(
            id="gpt-4o",
            display_name="GPT-4o",
            provider="openai",
            description="Flagship model, multimodal",
            input_cost_per_1m=2.50,
            output_cost_per_1m=10.00,
            context_window=128000,
            best_for="High-stakes documents",
            recommended=True
        ),
        "gpt-4o-mini": ModelInfo(
            id="gpt-4o-mini",
            display_name="GPT-4o Mini",
            provider="openai",
            description="Affordable, fast",
            input_cost_per_1m=0.15,
            output_cost_per_1m=0.60,
            context_window=128000,
            best_for="Cost-efficient batches"
        ),
        "gpt-4-turbo": ModelInfo(
            id="gpt-4-turbo",
            display_name="GPT-4 Turbo",
            provider="openai",
            description="Enhanced GPT-4",
            input_cost_per_1m=10.00,
            output_cost_per_1m=30.00,
            context_window=128000,
            best_for="Critical documents"
        ),
        
        # Anthropic Claude
        "claude-3-5-sonnet-20241022": ModelInfo(
            id="claude-3-5-sonnet-20241022",
            display_name="Claude 3.5 Sonnet",
            provider="claude",
            description="Best balance of speed and intelligence",
            input_cost_per_1m=3.00,
            output_cost_per_1m=15.00,
            context_window=200000,
            best_for="Nuanced translations",
            recommended=True
        ),
        "claude-3-opus-20240229": ModelInfo(
            id="claude-3-opus-20240229",
            display_name="Claude 3 Opus",
            provider="claude",
            description="Most capable, highest quality",
            input_cost_per_1m=15.00,
            output_cost_per_1m=75.00,
            context_window=200000,
            best_for="Mission-critical documents"
        ),
        "claude-3-haiku-20240307": ModelInfo(
            id="claude-3-haiku-20240307",
            display_name="Claude 3 Haiku",
            provider="claude",
            description="Fastest, most compact",
            input_cost_per_1m=0.25,
            output_cost_per_1m=1.25,
            context_window=200000,
            best_for="High-volume, simple translations"
        ),
    }
    
    @classmethod
    def get_model_info(cls, model_id: str) -> Optional[ModelInfo]:
        """Get enriched model information."""
        return cls.KNOWN_MODELS.get(model_id)
    
    @classmethod
    def get_provider_models(cls, provider: str) -> List[ModelInfo]:
        """Get all models for a provider."""
        return [m for m in cls.KNOWN_MODELS.values() if m.provider == provider]
    
    @classmethod
    def get_recommended_model(cls, provider: str) -> Optional[ModelInfo]:
        """Get recommended model for provider."""
        models = cls.get_provider_models(provider)
        for model in models:
            if model.recommended:
                return model
        return models[0] if models else None

class ModelFetcher(ABC):
    """Abstract base for fetching models from provider APIs."""
    
    @abstractmethod
    def fetch_available_models(self, api_key: str) -> List[str]:
        """Fetch list of available model IDs from API."""
        pass
    
    def get_enriched_models(self, api_key: str) -> List[ModelInfo]:
        """Fetch and enrich with metadata."""
        available_ids = self.fetch_available_models(api_key)
        enriched = []
        
        for model_id in available_ids:
            info = ModelRegistry.get_model_info(model_id)
            if info:
                enriched.append(info)
            else:
                # Unknown model - create basic info
                enriched.append(ModelInfo(
                    id=model_id,
                    display_name=model_id,
                    provider=self.provider_name,
                    description="No description available",
                    input_cost_per_1m=0,
                    output_cost_per_1m=0,
                    context_window=0,
                    best_for="Unknown"
                ))
        
        return enriched

class GeminiModelFetcher(ModelFetcher):
    provider_name = "gemini"
    
    def fetch_available_models(self, api_key: str) -> List[str]:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        models = genai.list_models()
        return [
            m.name.split('/')[-1] 
            for m in models 
            if 'generateContent' in m.supported_generation_methods
        ]

class OpenAIModelFetcher(ModelFetcher):
    provider_name = "openai"
    
    def fetch_available_models(self, api_key: str) -> List[str]:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        models = client.models.list()
        # Filter for chat models only
        return [
            m.id for m in models.data 
            if m.id.startswith(('gpt-4', 'gpt-3.5'))
        ]

class ClaudeModelFetcher(ModelFetcher):
    provider_name = "claude"
    
    def fetch_available_models(self, api_key: str) -> List[str]:
        # Claude API doesn't have list endpoint - return known models
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307"
        ]
```

**Model Selection UI**:
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                         Select Translation Model                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Provider: Google Gemini

  ┌─────────────────────────────────────────────────────────────────────────┐
  │ ❯ gemini-2.0-flash ★ RECOMMENDED                                       │
  │   ├─ Fast, cost-efficient, large context                               │
  │   ├─ Cost: $0.075 input / $0.30 output per 1M tokens                   │
  │   ├─ Context: 1,000,000 tokens                                         │
  │   └─ Best for: Large batches, drafts, cost-sensitive                   │
  ├─────────────────────────────────────────────────────────────────────────┤
  │   gemini-1.5-pro                                                       │
  │   ├─ High quality, balanced                                            │
  │   ├─ Cost: $1.25 input / $5.00 output per 1M tokens                    │
  │   ├─ Context: 1,000,000 tokens                                         │
  │   └─ Best for: Production releases, complex documents                  │
  ├─────────────────────────────────────────────────────────────────────────┤
  │   gemini-2.0-flash                                                     │
  │   ├─ Latest generation, improved reasoning                             │
  │   ├─ Cost: $0.10 input / $0.40 output per 1M tokens                    │
  │   ├─ Context: 1,000,000 tokens                                         │
  │   └─ Best for: Complex technical translations                          │
  └─────────────────────────────────────────────────────────────────────────┘

  [↑↓] Navigate  [Enter] Select  [q] Quit
```

**Cost Estimation Before Selection**:
```python
def estimate_translation_cost(
    file_path: str,
    model: ModelInfo
) -> Dict[str, float]:
    """Estimate translation cost for a file."""
    content = Path(file_path).read_text()
    
    # Estimate tokens (rough: 1 token ≈ 4 chars for English, 2 chars for Vietnamese)
    char_count = len(content)
    estimated_input_tokens = char_count / 2  # Vietnamese
    estimated_output_tokens = estimated_input_tokens * 1.2  # Translation slightly longer
    
    input_cost = (estimated_input_tokens / 1_000_000) * model.input_cost_per_1m
    output_cost = (estimated_output_tokens / 1_000_000) * model.output_cost_per_1m
    
    return {
        "input_tokens": int(estimated_input_tokens),
        "output_tokens": int(estimated_output_tokens),
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost,
        "model": model.id
    }

# Usage in CLI
def show_cost_comparison(file_path: str):
    """Show cost comparison across models."""
    console.print("\n[bold]Cost Estimation for Translation:[/bold]\n")
    
    table = Table()
    table.add_column("Model", style="cyan")
    table.add_column("Input Cost", justify="right")
    table.add_column("Output Cost", justify="right")
    table.add_column("Total", justify="right", style="green")
    
    for model in ModelRegistry.KNOWN_MODELS.values():
        est = estimate_translation_cost(file_path, model)
        table.add_row(
            f"{model.display_name} {'★' if model.recommended else ''}",
            f"${est['input_cost']:.4f}",
            f"${est['output_cost']:.4f}",
            f"${est['total_cost']:.4f}"
        )
    
    console.print(table)
```

#### 7.1.0.3 API Key Input and Validation

**Secure API Key Input Flow**:
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                         Configure API Provider                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

[?] Select API Provider:
  ❯ Google Gemini    ★ Recommended (Best value: fast, cheap, 1M context)
    OpenAI           (GPT-4 quality, higher cost)
    Anthropic Claude (Nuanced translations)

You selected: Google Gemini

┌─────────────────────────────────────────────────────────────────────────┐
│ How to get your Gemini API Key:                                         │
│                                                                         │
│ 1. Go to: https://aistudio.google.com/app/apikey                        │
│ 2. Click "Create API Key"                                               │
│ 3. Copy the key (starts with "AIza...")                                 │
│                                                                         │
│ Note: Free tier includes 15 requests/minute, 1M tokens/day              │
└─────────────────────────────────────────────────────────────────────────┘

[?] Enter your Gemini API Key: ●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●
    (Input is hidden for security)

⏳ Validating API key...

[?] How would you like to store this API key?
  ❯ System Keyring (Recommended - secure, persistent)
    Environment Variable (Good for CI/CD)
    Config File (Least secure - not recommended)

✓ API key validated successfully!
✓ API key stored in system keyring

Available models fetched: 3 models found
```

**Implementation - Secure Key Input**:
```python
import getpass
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

class APIKeyManager:
    """Secure API key input and validation."""
    
    PROVIDER_INFO = {
        "gemini": {
            "name": "Google Gemini",
            "key_url": "https://aistudio.google.com/app/apikey",
            "key_prefix": "AIza",
            "env_var": "GOOGLE_API_KEY",
            "free_tier": "15 req/min, 1M tokens/day",
            "recommendation": "Best value: fast, cheap, 1M context"
        },
        "openai": {
            "name": "OpenAI",
            "key_url": "https://platform.openai.com/api-keys",
            "key_prefix": "sk-",
            "env_var": "OPENAI_API_KEY",
            "free_tier": "None (pay-as-you-go)",
            "recommendation": "GPT-4 quality, higher cost"
        },
        "claude": {
            "name": "Anthropic Claude",
            "key_url": "https://console.anthropic.com/settings/keys",
            "key_prefix": "sk-ant-",
            "env_var": "ANTHROPIC_API_KEY",
            "free_tier": "None (pay-as-you-go)",
            "recommendation": "Nuanced translations"
        }
    }
    
    def prompt_for_key(self, provider: str) -> str:
        """Securely prompt user for API key."""
        info = self.PROVIDER_INFO[provider]
        
        # Show instructions
        instructions = f"""
[bold]How to get your {info['name']} API Key:[/bold]

1. Go to: [link]{info['key_url']}[/link]
2. Click "Create API Key"
3. Copy the key (starts with "{info['key_prefix']}...")

[dim]Free tier: {info['free_tier']}[/dim]
        """
        console.print(Panel(instructions, title="API Key Instructions"))
        
        # Secure input (hidden)
        api_key = getpass.getpass(f"Enter your {info['name']} API Key: ")
        
        # Basic format validation
        if not api_key.startswith(info['key_prefix']):
            console.print(f"[yellow]Warning: Key doesn't start with '{info['key_prefix']}'. "
                          f"This may not be a valid {info['name']} key.[/yellow]")
            if not Confirm.ask("Continue anyway?"):
                return self.prompt_for_key(provider)
        
        return api_key
    
    def validate_key(self, provider: str, api_key: str) -> bool:
        """Validate API key by making a test request."""
        console.print("⏳ Validating API key...", style="dim")
        
        try:
            if provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                # Try to list models as validation
                list(genai.list_models())
                
            elif provider == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                client.models.list()
                
            elif provider == "claude":
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                # Claude doesn't have a list models endpoint
                # Try a minimal request
                client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1,
                    messages=[{"role": "user", "content": "Hi"}]
                )
            
            console.print("✓ API key validated successfully!", style="bold green")
            return True
            
        except Exception as e:
            console.print(f"✘ API key validation failed: {e}", style="bold red")
            return False
    
    def prompt_storage_method(self) -> str:
        """Ask user how to store the API key."""
        console.print("\n[bold]How would you like to store this API key?[/bold]\n")
        
        options = [
            ("keyring", "System Keyring", "Recommended - secure, persistent across sessions"),
            ("env", "Environment Variable", "Good for CI/CD - set in .bashrc/.zshrc"),
            ("file", "Encrypted File", "Stored in ~/.docs-translator/ (less secure)")
        ]
        
        for i, (key, name, desc) in enumerate(options, 1):
            rec = " ★ Recommended" if key == "keyring" else ""
            console.print(f"  {i}. [cyan]{name}[/cyan]{rec}")
            console.print(f"     [dim]{desc}[/dim]")
        
        choice = Prompt.ask("\nSelect option", choices=["1", "2", "3"], default="1")
        return options[int(choice) - 1][0]
    
    def store_key(self, provider: str, api_key: str, method: str):
        """Store API key using selected method."""
        info = self.PROVIDER_INFO[provider]
        
        if method == "keyring":
            import keyring
            keyring.set_password("docs-translator", provider, api_key)
            console.print(f"✓ API key stored in system keyring", style="green")
            
        elif method == "env":
            console.print(f"\n[yellow]Add this line to your shell config (.bashrc, .zshrc):[/yellow]")
            console.print(f"[bold]export {info['env_var']}='{api_key}'[/bold]")
            console.print("\nThen run: source ~/.bashrc (or restart terminal)")
            
        elif method == "file":
            from pathlib import Path
            key_dir = Path.home() / ".docs-translator"
            key_dir.mkdir(exist_ok=True)
            key_file = key_dir / f"{provider}.key"
            key_file.write_text(api_key)
            key_file.chmod(0o600)
            console.print(f"✓ API key stored in {key_file}", style="green")
```

#### 7.1.0.4 Quick Reconfiguration Commands

**Change Settings Without Full Wizard**:
```bash
# Switch provider (if already configured)
docs-translator config use gemini
docs-translator config use openai

# Switch model for current provider
docs-translator config model gemini-1.5-pro
docs-translator config model gpt-4o

# Change translation style
docs-translator config style natural
docs-translator config style literal

# Update API key
docs-translator config update-key gemini
# → Securely prompts for new key

# Show current configuration
docs-translator config show

# Reset to defaults
docs-translator config reset
```

**Output of `docs-translator config show`**:
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                     Current Configuration                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Config file: ./docs-translator.yaml

┌─────────────────────────────────────────────────────────────────────────┐
│ Active Provider                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ Provider:    Google Gemini                                              │
│ Model:       gemini-2.0-flash ★                                         │
│ API Key:     ●●●●●●●●...za4Q (stored in keyring)                        │
│ Validated:   2024-12-26 14:30:00                                        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ Translation Settings                                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ Style:       literal (technical accuracy)                               │
│ Languages:   vi → en                                                    │
│ Temperature: 0.3                                                        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ Preserve Terms (12 terms)                                               │
├─────────────────────────────────────────────────────────────────────────┤
│ User Service, API Gateway, gRPC, PostgreSQL, Redis, Docker,            │
│ Kubernetes, AgriOS, CAS, CQRS, Clean Architecture, ...                  │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ Other Providers (configured)                                            │
├─────────────────────────────────────────────────────────────────────────┤
│ ○ OpenAI      - gpt-4o          (not active)                            │
│ ○ Claude      - not configured                                          │
└─────────────────────────────────────────────────────────────────────────┘

Commands:
  docs-translator config use openai    # Switch provider
  docs-translator config model gpt-4   # Change model
  docs-translator config update-key    # Update API key
```

#### 7.1.1 Basic Usage

```bash
# Simple translation with smart defaults
docs-translator translate \
    --file docs/srs-user.md \
    --source vi \
    --target en
# Output: docs/srs-user_en.md (auto-generated)

# Custom output path
docs-translator translate \
    --file docs/srs-user.md \
    --source vi \
    --target en \
    --output docs/en/srs-user.md

# Translate entire directory
docs-translator translate \
    --dir docs/confluence \
    --source vi \
    --target en \
    --recursive
# Output: docs/confluence_en/ (auto-generated)
```

#### 7.1.2 Smart Defaults

**Auto-generated Output Paths**:
```bash
# Input: file.md, Target: en
# Output: file_en.md (same directory)

# Input: docs/srs.md, Target: ja
# Output: docs/srs_ja.md

# Input directory: docs/vi, Target: en
# Output directory: docs/vi_en
```

**Default Configuration**:
- API Provider: Google Gemini (recommended) - can override with `--provider openai`
- Model: gemini-2.0-flash (auto-selected via wizard)
- Translation Style: literal (technical accuracy)
- Translation Memory: `.translation_memory.json` (current directory)

#### 7.1.3 Dry-run Mode (Recommended Before Production)

```bash
docs-translator translate \
    --file docs/large-document.md \
    --source vi \
    --target en \
    --dry-run
```

**Output Preview**:
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Translation Preview (Dry-run)           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

File: docs/large-document.md
Source: Vietnamese (vi) → Target: English (en)

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Block Analysis                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Total blocks:          100
✔ Cached (unchanged):  95 blocks (skip API call)
⚠ Modified:            3 blocks (will translate)
➕ New:                 2 blocks (will translate)

Cache hit rate: 95%

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Cost Estimation                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Blocks to translate:   5
Estimated tokens:      ~650 tokens
API cost:              ~$0.007 (GPT-4)

Cost saved by cache:   $0.095 (95 blocks)
Total savings:         93%

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Blocks to Translate                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

[Block 23] Paragraph (modified)
  "Hệ thống phải hỗ trợ User Service và..."

[Block 45] Heading (new)
  "## Tính năng mới"

[Block 67] Table Cell (modified)
  "Tăng hiệu suất 50%"

Run without --dry-run to execute translation.
```

#### 7.1.4 Progress Reporting

**Real-time Progress Bar**:
```bash
docs-translator translate \
    --dir docs/confluence \
    --source vi \
    --target en
```

**Output**:
```
Translating: docs/confluence/

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File Progress                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

[1/10] srs-user-service.md
  │████████████████████████████████████████│ 100%
  ✔ 95 blocks cached, 5 translated | $0.007

[2/10] adr-microservices.md
  │████████████████████────────────────────│  50%
  ⏳ Translating block 12/24...

Total progress: 15% | Cache hit rate: 97% | Cost: $0.012
```

#### 7.1.5 Advanced Options

```bash
# Custom provider and model
docs-translator translate \
    --file doc.md \
    --provider gemini \
    --model gemini-pro \
    --source vi --target en

# Custom preserve terms (override config)
docs-translator translate \
    --file doc.md \
    --preserve "User Service,API Gateway,gRPC" \
    --source vi --target en

# Verbose logging
docs-translator translate \
    --file doc.md \
    --source vi --target en \
    --verbose

# Skip cache (force re-translate)
docs-translator translate \
    --file doc.md \
    --source vi --target en \
    --no-cache
```

### 7.2 Python Module API

For programmatic usage:

```python
from docs_translator import Translator, Config

# Initialize
config = Config.from_yaml("config.yaml")
translator = Translator(config)

# Translate single file
result = translator.translate_file(
    input_path="docs/sample.md",
    output_path="docs/sample_en.md",
    source_lang="vi",
    target_lang="en"
)

# Batch translate
results = translator.translate_directory(
    input_dir="docs/confluence",
    output_dir="docs/confluence_en",
    source_lang="vi",
    target_lang="en",
    recursive=True,
    dry_run=False
)

# Check translation stats
print(f"Translated: {result.translated_blocks}")
print(f"Skipped: {result.skipped_blocks}")
print(f"Errors: {result.errors}")
```

---

## 7.3 User Experience (UX) Considerations

### 7.3.1 Design Principles for v1.0.0

**Goal**: Make CLI tool feel "smart" without adding complexity.

**Principles**:
1. **Smart Defaults**: Minimize required parameters
2. **Visual Feedback**: Never leave user wondering if tool is working
3. **Predictable**: Show what will happen before it happens (dry-run)
4. **Transparent**: Show cache hits, cost savings, progress
5. **Fail-Safe**: Validate input before expensive API calls

### 7.3.2 User Journey: Typical Workflow

**Scenario**: User updates SRS document and needs to re-translate.

**Step 1: Preview Changes** (Recommended)
```bash
docs-translator translate \
    --file docs/srs-user.md \
    --source vi --target en \
    --dry-run
```

**User sees**:
```
✔ 95 blocks unchanged (cached)
⚠  5 blocks modified (will translate)
⚡ Estimated cost: $0.007
⚡ Estimated time: 8 seconds
```

**Step 2: Execute Translation**
```bash
# Remove --dry-run flag
docs-translator translate \
    --file docs/srs-user.md \
    --source vi --target en
```

**User sees**:
```
⏳ Translating docs/srs-user.md...
  │████████████████████████████████████████│ 100%
✔ Translation complete!

Output: docs/srs-user_en.md

Statistics:
  • Blocks translated: 5 / 100
  • Cache hit rate: 95%
  • Cost: $0.007
  • Time: 7.2s
  • Cost saved: $0.095 (93% savings)
```

**Step 3: Verify Output**
```bash
# User opens generated file
code docs/srs-user_en.md

# Or compare with previous version
diff docs/srs-user_en.md.backup docs/srs-user_en.md
```

### 7.3.3 Visual Feedback Design

**Progress Indicators**:
```python
from tqdm import tqdm
import time

def translate_with_progress(blocks: List[str]):
    with tqdm(
        total=len(blocks),
        desc="Translating",
        unit="block",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
    ) as pbar:
        for i, block in enumerate(blocks):
            # Check cache
            cached = tm.get_translation(block, ...)
            if cached:
                pbar.set_postfix({"status": "✔ cached", "cost": "$0.00"})
            else:
                pbar.set_postfix({"status": "⏳ translating", "cost": "$0.001"})
                translate_block(block)
            
            pbar.update(1)
            time.sleep(0.1)  # Smooth animation
```

**Color-Coded Output** (using `rich` library):
```python
from rich.console import Console
from rich.table import Table

console = Console()

# Success message
console.print("✔ Translation complete!", style="bold green")

# Warning message
console.print("⚠ 5 blocks modified", style="bold yellow")

# Error message
console.print("✘ API key not found", style="bold red")

# Statistics table
table = Table(title="Translation Statistics")
table.add_column("Metric", style="cyan")
table.add_column("Value", style="magenta")
table.add_row("Cache Hit Rate", "95%")
table.add_row("Cost", "$0.007")
console.print(table)
```

### 7.3.4 Error Prevention

**Pre-flight Checks** (before calling API):
```python
def validate_before_translation(file_path: str) -> List[str]:
    """Return list of errors, empty if valid."""
    errors = []
    
    # Check 1: File exists
    if not os.path.exists(file_path):
        errors.append(f"File not found: {file_path}")
    
    # Check 2: Is Markdown
    if not file_path.endswith('.md'):
        errors.append(f"Not a Markdown file: {file_path}")
    
    # Check 3: File not empty
    if os.path.getsize(file_path) == 0:
        errors.append(f"File is empty: {file_path}")
    
    # Check 4: Valid Markdown syntax
    try:
        parser.parse(open(file_path).read())
    except Exception as e:
        errors.append(f"Invalid Markdown syntax: {e}")
    
    # Check 5: API key present
    if not os.getenv('OPENAI_API_KEY'):
        errors.append("OPENAI_API_KEY not set")
    
    # Check 6: Output directory writable
    output_dir = os.path.dirname(output_path)
    if not os.access(output_dir, os.W_OK):
        errors.append(f"Output directory not writable: {output_dir}")
    
    return errors

# Usage
errors = validate_before_translation(input_file)
if errors:
    console.print("✘ Pre-flight checks failed:", style="bold red")
    for error in errors:
        console.print(f"  • {error}", style="red")
    sys.exit(1)
```

### 7.3.5 Smart Defaults Implementation

```python
import os
from pathlib import Path

def generate_output_path(
    input_path: str,
    target_lang: str,
    output_path: Optional[str] = None
) -> str:
    """Generate smart output path if not provided."""
    
    if output_path:
        return output_path  # User specified, use as-is
    
    # Auto-generate
    path = Path(input_path)
    stem = path.stem  # filename without extension
    suffix = path.suffix  # .md
    parent = path.parent
    
    # Add language suffix
    output_filename = f"{stem}_{target_lang}{suffix}"
    return str(parent / output_filename)

# Examples:
generate_output_path("docs/srs.md", "en")
# → "docs/srs_en.md"

generate_output_path("docs/srs.md", "ja")
# → "docs/srs_ja.md"

generate_output_path("docs/srs.md", "en", "custom/output.md")
# → "custom/output.md" (respects user input)
```

### 7.3.6 Helpful Error Messages

**Bad** (vague, unhelpful):
```
Error: Translation failed
```

**Good** (specific, actionable):
```
✘ Translation failed

Reason: OpenAI API rate limit exceeded (429)

Suggestions:
  1. Wait 60 seconds and try again
  2. Use --provider gemini to switch API
  3. Enable rate limiter: --rate-limit 90000

For more details, run with --verbose
```

---

## 8. Security Design

### 8.1 API Key Management

**CRITICAL**: Never hardcode API keys in code or config files committed to version control.

**Security Hierarchy** (from most to least secure):

| Method | Security Level | Use Case | Implementation |
| --- | --- | --- | --- |
| System Keyring | Highest | Developer workstations | `keyring` library |
| Environment Variables | High | CI/CD, Containers | `os.getenv()` |
| Encrypted File | Medium | Enterprise, audited | AES-256 encryption |
| Plain Config File | Low | Never for production | Avoid |

**Recommended Approach - System Keyring**:
```python
import keyring

# Store API key securely
keyring.set_password("docs-translator", "gemini", "AIza...")

# Retrieve API key
api_key = keyring.get_password("docs-translator", "gemini")
```

**Benefits of System Keyring**:
- Keys stored in OS-level secure storage (Windows Credential Manager, macOS Keychain, Linux Secret Service)
- Encrypted at rest
- Not visible in process environment
- Persists across sessions
- Cannot be accidentally committed to git

**Environment Variables (for CI/CD)**:
```bash
# Store in environment variables
export GOOGLE_API_KEY="AIza..."
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Or use .env file (MUST be in .gitignore)
echo "GOOGLE_API_KEY=AIza..." > .env
```

**.gitignore Requirements**:
```gitignore
# API Keys and Secrets
.env
.env.local
.env.*.local
*.key
docs-translator.yaml  # Contains key references
.docs-translator/     # User config directory
```

**Code Implementation - Multi-source Key Resolution**:
```python
import os
import keyring
from pathlib import Path
from typing import Optional

class SecureKeyManager:
    """Resolve API key from multiple secure sources."""
    
    PROVIDER_ENV_VARS = {
        "gemini": "GOOGLE_API_KEY",
        "openai": "OPENAI_API_KEY",
        "claude": "ANTHROPIC_API_KEY"
    }
    
    def get_api_key(self, provider: str, config: dict) -> Optional[str]:
        """
        Resolve API key with fallback chain:
        1. Environment variable (highest priority - for CI/CD override)
        2. System keyring (secure storage)
        3. Encrypted file (fallback)
        """
        env_var = self.PROVIDER_ENV_VARS.get(provider)
        
        # Priority 1: Environment variable
        if env_var and os.getenv(env_var):
            return os.getenv(env_var)
        
        # Priority 2: System keyring
        try:
            key = keyring.get_password("docs-translator", provider)
            if key:
                return key
        except keyring.errors.KeyringError:
            pass  # Keyring not available
        
        # Priority 3: Encrypted file
        key_file = Path.home() / ".docs-translator" / f"{provider}.key"
        if key_file.exists():
            return self._decrypt_key_file(key_file)
        
        return None
    
    def _decrypt_key_file(self, path: Path) -> str:
        """Decrypt API key from file (placeholder for AES implementation)."""
        # For MVP: simple file read (file permissions protect it)
        return path.read_text().strip()
```

### 8.2 Input Validation

**Prevent Injection Attacks**:
```python
def validate_markdown_file(file_path: str):
    """Ensure file is valid Markdown before processing."""
    if not file_path.endswith('.md'):
        raise ValueError("Only .md files supported")
    
    # Check file size (prevent memory exhaustion)
    file_size = os.path.getsize(file_path)
    if file_size > 10 * 1024 * 1024:  # 10MB limit
        raise ValueError("File too large (max 10MB)")
```

### 8.3 Data Privacy

**Consideration**: Documents may contain sensitive business information.

**Options**:
1. **Self-hosted LLM**: Use local models (LLaMA, Mistral) instead of cloud APIs
2. **Data Sanitization**: Strip sensitive data before sending to API
3. **Audit Logging**: Log all translations for compliance review

---

## 9. Performance Considerations

### 9.1 Performance Requirements

- Single file translation: < 30 seconds for 1000-line document
- Batch translation: 50 files in < 10 minutes
- Memory usage: < 500MB for processing 100 files
- **Incremental translation**: 99% cache hit rate on unchanged content

### 9.2 Optimization Strategies

#### 9.2.1 Incremental Translation (Primary Cost Saver)

**Impact**: This is the single most important optimization - saves 99% of API costs on document updates.

**Scenario Analysis**:
```
Initial Translation (50 documents, 2000 words each):
- Total words: 100,000
- API cost: $10.40 (see Section 17.3)

Update 1 (1 week later - 5% content changed):
- Changed blocks: 5,000 words
- Unchanged blocks: 95,000 words (cached)
- API cost: $0.52 (95% savings)

Update 2 (1 month later - 2% content changed):
- Changed blocks: 2,000 words
- API cost: $0.21 (98% savings)
```

**Annual Cost Comparison**:
```
Without Translation Memory:
- 12 monthly updates × $10.40 = $124.80/year

With Translation Memory (5% avg change rate):
- Initial: $10.40
- 12 updates × $0.52 = $6.24/year
- Total: $16.64/year
- Savings: $108.16 (87% reduction)
```

**Implementation**: See Section 6.2 for Translation Memory Manager code.

#### 9.2.2 Batch API Calls

**Problem**: Translating paragraph-by-paragraph is slow (1 API call per paragraph).

**Solution**: Batch multiple paragraphs into single API call.

```python
def batch_translate(paragraphs: List[str], batch_size: int = 5) -> List[str]:
    """Translate multiple paragraphs in one API call."""
    batched = []
    for i in range(0, len(paragraphs), batch_size):
        batch = paragraphs[i:i+batch_size]
        # Join with delimiter
        combined = "\n---SEPARATOR---\n".join(batch)
        translated = api_translate(combined)
        # Split back
        batched.extend(translated.split("---SEPARATOR---"))
    return batched
```

#### 9.2.3 Translation Memory (Primary)

- Use Translation Memory Manager (Section 6.2) for block-level caching
- Hash-based lookup for O(1) cache hits
- Persist memory to disk between runs
- Context-aware caching (heading vs paragraph)
- **Target**: 95%+ cache hit rate on incremental updates

#### 9.2.4 Parallel Processing

For batch directory translation:

```python
from concurrent.futures import ThreadPoolExecutor

def translate_directory_parallel(files: List[str], max_workers: int = 4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(translate_file, files)
    return list(results)
```

**Trade-off**: API rate limits may require throttling.

---

## 10. Error Handling

### 10.1 Error Code Convention

| Code | Description | Recovery Action |
| --- | --- | --- |
| ERR-001 | Invalid Markdown syntax | Skip file, log error |
| ERR-002 | API key missing | Exit with instructions |
| ERR-003 | API rate limit exceeded | Wait and retry with exponential backoff |
| ERR-004 | Network timeout | Retry up to 3 times |
| ERR-005 | Invalid configuration | Exit with validation errors |
| ERR-006 | Output directory not writable | Exit with permission error |

### 10.2 Retry Logic

**Recommended Approach: Using tenacity (Industry Standard)**

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from openai import RateLimitError, APITimeoutError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((RateLimitError, APITimeoutError)),
    reraise=True
)
def translate_with_retry(text: str) -> str:
    """Translate with automatic retry on transient errors."""
    return api_translate(text)

# Usage is simple and elegant
result = translate_with_retry("Hệ thống phải hỗ trợ User Service")
```

**Benefits of tenacity**:
- Declarative syntax with `@retry` decorator
- Built-in exponential backoff with jitter
- Flexible retry conditions (exception type, result value)
- Automatic logging of retry attempts
- Production-tested by major Python projects

**Manual Implementation** (for reference, not recommended):

```python
import time
from typing import Callable

def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> any:
    """Manual retry with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            print(f"Rate limited. Retrying in {delay}s...")
            time.sleep(delay)
```

**Recommendation**: Use `tenacity` for all retry logic. Manual implementation shown for educational purposes only.

### 10.4 Token Bucket Rate Limiter

**Problem**: When translating 50+ files in batch, reactive retry logic (exponential backoff) still wastes time by hitting rate limits repeatedly.

**Solution**: Proactive rate limiting using Token Bucket algorithm to throttle requests before API rejects them.

```python
import time
import threading

class TokenBucketRateLimiter:
    """
    Proactive rate limiter to prevent exceeding API rate limits.
    
    Example: OpenAI TPM (Tokens Per Minute) limit = 90,000
    """
    def __init__(self, tokens_per_minute: int, max_burst: int):
        self.capacity = max_burst
        self.tokens = max_burst
        self.fill_rate = tokens_per_minute / 60.0  # tokens per second
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def acquire(self, tokens_needed: int) -> None:
        """Block until enough tokens available."""
        with self.lock:
            while True:
                now = time.time()
                elapsed = now - self.last_update
                
                # Refill bucket based on elapsed time
                self.tokens = min(
                    self.capacity,
                    self.tokens + elapsed * self.fill_rate
                )
                self.last_update = now
                
                if self.tokens >= tokens_needed:
                    self.tokens -= tokens_needed
                    return
                
                # Wait for refill
                sleep_time = (tokens_needed - self.tokens) / self.fill_rate
                time.sleep(sleep_time)

# Usage
rate_limiter = TokenBucketRateLimiter(
    tokens_per_minute=90000,  # OpenAI TPM limit
    max_burst=5000  # Allow bursts up to 5000 tokens
)

def translate_with_rate_limit(text: str) -> str:
    estimated_tokens = len(text) // 4  # Rough estimate
    rate_limiter.acquire(estimated_tokens)
    return api_translate(text)
```

**Benefits**:
- Prevents wasted API calls that will be rejected
- Smoother batch processing without sudden pauses
- Configurable per API provider (OpenAI: 90k TPM, Gemini: different limits)

### 10.3 Rollback Strategy

**Problem**: If translation fails mid-batch, how to recover?

**Solution**: Transaction-like approach:
1. Write translations to temporary directory first
2. Only move to final location after all files succeed
3. If any file fails, discard temporary directory

```python
import shutil
import tempfile

def translate_with_rollback(files: List[str]):
    temp_dir = tempfile.mkdtemp()
    try:
        for file in files:
            translate_file(file, output_dir=temp_dir)
        # Success: move temp to final location
        shutil.copytree(temp_dir, final_output_dir)
    except Exception as e:
        # Failure: discard temp directory
        shutil.rmtree(temp_dir)
        raise
```

---

## 11. Testing Strategy

### 11.1 Unit Testing

**Test Cases**:

| Component | Test Case | Expected Result |
| --- | --- | --- |
| Parser | Parse code block | Token type = 'fence', content preserved |
| Parser | Parse table | Correct row/column structure |
| Traverser | Detect requirement ID | FR-01 marked as PRESERVE |
| Traverser | Detect inline code | Text in backticks marked as SKIP |
| Renderer | Rebuild heading | Correct # count, text preserved |
| Renderer | Rebuild table | Markdown table syntax valid |

**Example Test**:
```python
def test_parser_preserves_code_blocks():
    md_input = """
Some text.

```python
print("hello")
```

More text.
    """
    tokens = MarkdownParser().parse(md_input)
    code_tokens = [t for t in tokens if t.type == 'fence']
    assert len(code_tokens) == 1
    assert code_tokens[0].content == 'print("hello")\n'
    assert code_tokens[0].info == 'python'
```

### 11.2 Integration Testing

**Test Scenarios**:
1. **End-to-End Translation**: Translate sample SRS document, verify structure preserved
2. **Preserve Terms**: Configure "User Service" as preserve term, verify not translated
3. **Batch Translation**: Translate 10 files, verify all succeed
4. **API Failure**: Mock API timeout, verify retry logic works

**Golden Test Approach**:
```
tests/
├── fixtures/
│   ├── input/
│   │   └── sample_vi.md
│   └── expected/
│       └── sample_en.md
└── test_translation.py
```

```python
def test_translation_matches_expected():
    result = translator.translate_file("fixtures/input/sample_vi.md")
    expected = open("fixtures/expected/sample_en.md").read()
    assert result == expected
```

### 11.3 Performance Testing

**Load Test**:
```python
import time

def test_performance_100_files():
    start = time.time()
    translator.translate_directory("test_docs", file_count=100)
    duration = time.time() - start
    
    assert duration < 600  # 10 minutes
    assert memory_usage() < 500 * 1024 * 1024  # 500MB
```

---

## 12. Monitoring and Observability

### 12.1 Metrics

**Application Metrics**:
- Files translated per run
- Average translation time per file
- API call count and cost
- Cache hit rate
- Error rate by error code

**Implementation**:
```python
@dataclass
class TranslationStats:
    files_processed: int = 0
    total_tokens_translated: int = 0
    api_calls_made: int = 0
    cache_hits: int = 0
    errors: int = 0
    total_duration: float = 0.0
    
    def report(self):
        print(f"""
Translation Statistics:
- Files: {self.files_processed}
- API Calls: {self.api_calls_made}
- Cache Hit Rate: {self.cache_hits / self.files_processed:.1%}
- Avg Time/File: {self.total_duration / self.files_processed:.2f}s
- Errors: {self.errors}
        """)
```

### 12.2 Logging

**Log Structure**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('translation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('docs_translator')

# Usage
logger.info(f"Translating file: {file_path}")
logger.debug(f"API response time: {duration}ms")
logger.error(f"Translation failed: {error}", exc_info=True)
```

**What to Log**:
- File processing start/end
- API calls (request size, response time)
- Cache hits/misses
- Errors with full stack trace
- Configuration loaded

### 12.3 Progress Reporting

For batch operations, show real-time progress:

```python
from tqdm import tqdm

def translate_directory(files: List[str]):
    with tqdm(total=len(files), desc="Translating") as pbar:
        for file in files:
            translate_file(file)
            pbar.update(1)
            pbar.set_postfix({"current": file})
```

---

## 13. Deployment Plan

### 13.1 Deployment Strategy

**Phase 1: Local Testing (Week 1)**
- Install on 2-3 developer machines
- Translate 5-10 sample documents
- Gather feedback on accuracy and speed

**Phase 2: Pilot Deployment (Week 2-3)**
- Translate entire `docs/confluence/` directory
- Compare output with manual translations
- Adjust preserve_terms configuration

**Phase 3: Production Use (Week 4+)**
- Document tool in team wiki
- Train team on usage
- Integrate into documentation workflow

### 13.2 Installation Steps

**Prerequisites**:
```bash
# Install Python 3.10+
python --version  # Verify 3.10 or higher

# Install pipx for isolated installs
pip install pipx
```

**Install Tool**:
```bash
# From source (development)
git clone https://dev.azure.com/agris-agriculture/Core/_git/docs-translator
cd docs-translator
pip install -e .

# From package (production)
pip install docs-translator
```

**Run Setup Wizard** (Recommended for first-time users):
```bash
docs-translator configure
```

**Interactive configuration** will guide through:
1. API provider selection (Gemini recommended)
2. API key validation
3. Model selection with cost/quality info
4. Translation style preference
5. Language pair setup

**Manual Configuration** (for CI/CD or advanced users):
```bash
# Set API key
export GOOGLE_API_KEY="your-key-here"

# Create config manually
cat > config.yaml << EOF
translation:
  api_provider: "gemini"
  model: "gemini-2.0-flash"
  translation_style: "literal"
languages:
  source: "vi"
  target: "en"
EOF
```

**Verify Installation**:
```bash
docs-translator --version
docs-translator --help
```

### 13.3 CI/CD Integration (Future)

**GitHub Actions Workflow**:
```yaml
name: Auto-translate Documentation

on:
  push:
    paths:
      - 'docs/confluence/**/*.md'

jobs:
  translate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install docs-translator
        run: pip install docs-translator
      
      - name: Translate Documents
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          docs-translator translate \
            --dir docs/confluence \
            --source vi \
            --target en \
            --output docs/confluence_en
      
      - name: Commit Translations
        run: |
          git config user.name "Translation Bot"
          git config user.email "bot@example.com"
          git add docs/confluence_en
          git commit -m "Auto-translate documentation [skip ci]"
          git push
```

---

## 14. Risks and Mitigation

### 14.1 High-Level Risk Summary

| Risk | Probability | Impact | Mitigation |
| --- | --- | --- | --- |
| AI translates technical terms incorrectly | High | High | Use preserve_terms config, review first 10 translations manually |
| API costs exceed budget | Medium | Medium | Set monthly budget alerts, use caching aggressively |
| Translation quality inconsistent | Medium | High | Use temperature=0.3, provide detailed system prompts, A/B test models |
| Tool breaks Markdown structure | Low | Critical | Extensive unit tests, golden file comparisons, dry-run before production |
| API rate limits block batch jobs | Medium | Medium | Implement Token Bucket Rate Limiter, exponential backoff |
| Round-trip rendering loses formatting | High | High | Use mdformat or custom renderer, extensive testing |
| Context loss in batch translation | Medium | Medium | Send previous paragraph as context, use sliding window |

### 14.2 Critical Technical Risks

#### Risk A: Round-trip Rendering (Highest Difficulty)

**Challenge**: 
Libraries like `markdown-it-py` excel at parsing Markdown → HTML/AST, but **lack robust rendering from AST back to Markdown** while preserving original formatting (whitespace, indentation, alignment).

**Specific Issues**:
1. **Table Alignment**: Original file has manually aligned pipes `|`, but renderer may produce unaligned output
   ```markdown
   # Original (beautiful)
   | Column A          | Column B    |
   | ----------------- | ----------- |
   | Value 1           | Value 2     |
   
   # After round-trip (ugly but valid)
   | Column A | Column B |
   | --- | --- |
   | Value 1 | Value 2 |
   ```

2. **Whitespace Collapsing**: Extra blank lines for readability may be removed
3. **List Indentation**: Nested lists may lose custom indentation levels

**Mitigation Strategies**:

**Option 1: Use mdformat Library**
```bash
pip install mdformat
```
```python
import mdformat

def format_output(markdown_text: str) -> str:
    """Post-process translated Markdown for consistent formatting."""
    return mdformat.text(markdown_text, options={"wrap": 80})
```

**Option 2: Custom Renderer** (More control, more work)
```python
class PreservingMarkdownRenderer:
    """Custom renderer that preserves original formatting metadata."""
    
    def __init__(self, original_tokens: List[Token]):
        # Store original formatting metadata
        self.original_format = self._extract_format_metadata(original_tokens)
    
    def render_table(self, translated_cells: List[str]) -> str:
        """Render table preserving original column widths."""
        # Apply original column width to translated cells
        pass
```

**Recommendation**: Start with `mdformat` for MVP, implement custom renderer if formatting quality is critical.

#### Risk B: Context Window & Context Splitting

**Challenge**:
When translating in batches, paragraph N may reference concepts from paragraph N-1, but if translated separately, context is lost.

**Example**:
```markdown
# Paragraph 1 (context)
The User Service handles authentication and authorization.

# Paragraph 2 (depends on context)
It uses JWT tokens for session management.
```

If Paragraph 2 is translated without Paragraph 1, "It" may be mistranslated because AI doesn't know what "It" refers to.

**Mitigation Strategies**:

**Strategy 1: Sliding Window Context**
```python
def translate_with_context(
    paragraphs: List[str],
    window_size: int = 1
) -> List[str]:
    """Translate with previous N paragraphs as context."""
    results = []
    for i, para in enumerate(paragraphs):
        # Include previous paragraph as context
        context = paragraphs[max(0, i-window_size):i]
        
        prompt = f"""
Context (DO NOT translate this):
{chr(10).join(context)}

Translate this paragraph:
{para}
        """
        result = api_translate(prompt)
        results.append(result)
    return results
```

**Strategy 2: Full Document Translation with Gemini** (Leverages large context window)

**Gemini Advantage**: Gemini 1.5 Flash/Pro have **1M+ token context window**, allowing translation of entire documents without splitting.

```python
def translate_document_gemini(doc: str, max_words: int = 50000) -> str:
    \"\"\"
    Translate entire document in single API call (Gemini only).
    
    Gemini 1.5 Flash: 1M token context (~750k words)
    This eliminates context loss completely.
    \"\"\"
    if word_count(doc) < max_words:
        # Send entire document at once
        return gemini_translate(doc, context=\"full_document\")
    else:
        # Document too large, fall back to sliding window
        return translate_with_context(split_paragraphs(doc))

# Usage
translator = GeminiTranslator(model=\"gemini-2.0-flash\")
result = translator.translate_document_gemini(large_document)
```

**Cost Comparison**:
```
OpenAI GPT-4 (8k context):
- Must split 50-page doc into 20 chunks
- 20 API calls × $0.03 = $0.60

Gemini 1.5 Flash (1M context):
- Send entire doc in 1 call
- 1 API call × $0.001 = $0.001
- 600x cheaper!
```

**Recommendation**: 
- Use Gemini 1.5 Flash for documents < 50k words (single-call translation)
- Use sliding window with `window_size=1` for larger documents or other providers

#### Risk C: Rate Limit Management

**Challenge**:
When batch processing 50 files, you will hit API Tokens Per Minute (TPM) limits very quickly.

**Provider Comparison**:

| Provider | Model | TPM Limit (Tier 1) | RPM Limit | Notes |
| --- | --- | --- | --- | --- |
| Google Gemini | 1.5 Flash | 4,000,000 | 1000 | ⭐ Best for batch jobs |
| Google Gemini | 1.5 Pro | 360,000 | 1000 | High throughput |
| OpenAI | GPT-4 | 90,000 | 500 | Restrictive |
| OpenAI | GPT-3.5 | 250,000 | 3000 | Better throughput |
| Anthropic | Claude | 100,000 | 50 | Very restrictive |

**Calculation Example**:
```
50 files × 2000 words/file = 100,000 words
100,000 words × 1.33 tokens/word = 133,000 tokens

OpenAI GPT-4 (90k TPM):
- Requires ~2 minutes minimum
- Will hit rate limits immediately on burst

Gemini 1.5 Flash (4M TPM):
- Can process in seconds
- 44x higher limit than GPT-4
```

**Why Gemini is Recommended**:
1. **44x higher TPM**: 4M vs 90k (GPT-4)
2. **1000 RPM**: High request throughput
3. **Free tier**: 15 RPM free (good for testing)
4. **Lower cost**: ~$0.075 vs $10 per 1M tokens

**Mitigation Strategy** (Already covered in Section 10.4):
- Implement Token Bucket Rate Limiter (proactive throttling)
- Use exponential backoff for reactive handling
- For Gemini: Rate limiting is rarely needed due to high limits

**Code Integration**:
```python
class Translator:
    def __init__(self, config: Config):
        # Adjust rate limiter based on provider
        tpm_limits = {
            "gemini-2.0-flash": 4_000_000,
            "gemini-1.5-pro": 360_000,
            "gpt-4": 90_000,
            "gpt-3.5-turbo": 250_000
        }
        
        self.rate_limiter = TokenBucketRateLimiter(
            tokens_per_minute=tpm_limits.get(config.model, 90_000),
            max_burst=5000
        )
    
    def translate(self, text: str) -> str:
        # Proactive rate limiting (less critical for Gemini)
        estimated_tokens = estimate_tokens(text)
        self.rate_limiter.acquire(estimated_tokens)
        
        # Reactive retry on failure
        return retry_with_backoff(lambda: api_call(text))
```

---

## 15. Dependencies

### 15.1 Python Libraries

**Core**:
- `markdown-it-py` (v3.0+): Markdown parser
- `openai` (v1.0+): OpenAI API client
- `google-generativeai`: Gemini API client
- `anthropic`: Claude API client
- `python-dotenv`: Environment variable management
- `tenacity` (v8.2+): Industry-standard retry/backoff logic

**CLI**:
- `click` (v8.1+): CLI framework
- `tqdm` (v4.66+): Progress bars
- `rich` (v13.0+): Color-coded terminal output
- `pyyaml` (v6.0+): YAML config parsing

**Development**:
- `pytest` (v7.4+): Testing framework
- `pytest-cov`: Coverage reporting
- `black`: Code formatting
- `mypy`: Type checking

**requirements.txt**:
```txt
markdown-it-py>=3.0.0
openai>=1.0.0
google-generativeai>=0.3.0
anthropic>=0.8.0
python-dotenv>=1.0.0
tenacity>=8.2.0
click>=8.1.0
tqdm>=4.66.0
rich>=13.0.0
pyyaml>=6.0.0

# Development
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
mypy>=1.7.0
```

### 15.2 External Services

- **OpenAI API**: GPT-4 or GPT-3.5-turbo
- **Google Gemini API**: gemini-pro
- **Anthropic Claude API**: claude-3-opus

---

## 16. Open Questions

- [ ] Which LLM provider gives best translation quality for Vietnamese-English technical docs?
- [ ] Should we support translation memory (TM) export for professional translator review?
- [ ] How to handle custom Markdown extensions (mermaid diagrams, custom HTML)?
- [ ] Should cache be shared across team members (Redis) or local file only?
- [ ] What is acceptable API cost per document? (Estimate: $0.05-0.20 per 1000-word doc)

---

## 17. Appendix

### 17.1 Glossary

| Term | Definition |
| --- | --- |
| AST | Abstract Syntax Tree - hierarchical representation of document structure |
| LLM | Large Language Model (GPT-4, Gemini, Claude) |
| Token | Basic unit in AST (heading, paragraph, code block, etc.) |
| Preserve Term | Technical term that should not be translated |
| Requirement ID | Identifier like FR-01, NFR-P01 used in SRS documents |
| Tenacity | Python library for retry logic with exponential backoff |
| TPM | Tokens Per Minute - API rate limit measurement |

### 17.2 Reference Documents

**Standards**:
- [CommonMark Spec](https://spec.commonmark.org/) - Markdown specification
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering) - Prompt engineering

**Similar Tools**:
- [mdbook-i18n](https://github.com/google/mdbook-i18n-helpers) - Translation tool for mdBook
- [i18n-auto](https://github.com/linyuxuanlin/i18n-auto) - GitHub Actions for doc translation

### 17.3 Estimation

**Development Effort**:
- Parser + Traverser: 3 days
- AI Translator integration: 2 days
- Renderer: 2 days
- CLI + Config: 1 day
- Testing: 2 days
- **Total**: 10 days (2 weeks)

**API Cost Estimation**:
Assuming 50 documents, 2000 words each:
- Total words: 100,000
- GPT-4 tokens: ~130,000 tokens
- Cost: ~$2.60 (input) + ~$7.80 (output) = **~$10.40 per full translation run**

---

## 18. Production Readiness Assessment

### 18.1 Overall Evaluation

**Status**: ✅ **Ready for v1.0.0 Internal Release**

**Technical Feasibility**: ⭐⭐⭐⭐⭐ (Excellent)
- Python ecosystem for Markdown parsing is mature
- LLM APIs (OpenAI, Gemini, Claude) have proven translation quality
- All critical technical challenges have identified mitigation strategies
- Translation Memory architecture is battle-tested (CAT tool standard)

**Scalability**: ⭐⭐⭐⭐⭐ (Excellent)
- Easy to add new LLM providers (modular design)
- Easy to add new languages (Thai, Indonesian, etc.)
- Translation Memory ensures cost scales linearly with changes, not document size
- Parallel processing supports large documentation sets

**Cost Efficiency**: ⭐⭐⭐⭐⭐ (Highly Optimized)
- Translation Memory eliminates 99% of duplicate work
- Incremental updates cost 93-98% less than full re-translation
- Annual cost: $16.64 vs $124.80 without caching (87% savings)
- Cost predictable and scales with team growth

**User Experience**: ⭐⭐⭐⭐⭐ (Polished)
- Smart defaults minimize friction
- Dry-run mode provides transparency
- Progress bars and visual feedback
- Helpful error messages with actionable suggestions

**Maintenance Burden**: ⭐⭐⭐⭐☆ (Low)
- Configuration-driven (preserve_terms in YAML)
- Minimal code dependencies
- No database required (JSON file storage)
- Standard Python tooling

### 18.2 Version 1.0.0 Feature Set (Confirmed)

**Core Features** (Must Have):
- ✅ Markdown parsing with structure preservation
- ✅ Translation Memory with granular hashing
- ✅ Incremental translation (99% cost savings)
- ✅ Vietnamese ⇄ English support
- ✅ CLI with smart defaults
- ✅ Dry-run mode with cost preview
- ✅ Progress reporting
- ✅ Error handling with retry logic
- ✅ Preserve terms configuration
- ✅ OpenAI/Gemini/Claude provider support

**Out of Scope for v1.0.0** (Future):
- ❌ GUI application
- ❌ Real-time collaboration
- ❌ User management system
- ❌ Cloud-based Translation Memory
- ❌ Custom renderer (use mdformat for MVP)

### 18.3 Sweet Spot Analysis

**Why This is the Perfect v1.0.0**:

**Focused on Core Value**:
- Solves biggest pain points: time waste + format breakage
- Delivers immediate ROI (87% cost reduction)
- No feature bloat

**High Flexibility**:
- Works for individuals (single file)
- Works for teams (batch directories)
- Works in CI/CD pipelines
- Configurable via CLI or YAML

**Low Friction**:
- Smart defaults: `--file doc.md --target en` → auto-generates output
- Dry-run: See cost before spending
- Visual feedback: Never wonder if tool is working

**Production Quality**:
- Translation Memory ensures consistency
- Error prevention (pre-flight checks)
- Transparent cost tracking
- Professional UX (progress bars, colors, helpful errors)

### 18.4 Go/No-Go Criteria

**Go-Live Checklist** (Updated):
- [x] Technical design complete (TDD finished)
- [x] Architecture validated (CAT tool standard)
- [x] UX considerations documented
- [x] Cost optimization strategy confirmed
- [ ] Prototype implementation (2 weeks)
- [ ] Test with 10 sample documents
- [ ] preserve_terms list populated
- [ ] User documentation written
- [ ] Team demo and training

**Success Metrics** (measured after 1 month):
- ⏱️ Translation time: 2-4 hours → 5-10 minutes (90% reduction)
- 💰 API cost: < $20/month for 50-document corpus with weekly updates
- ✅ Translation accuracy: 95%+ (spot-check reviews)
- 🎯 Cache hit rate: 95%+ on incremental updates
- 🚫 Markdown breakage: Zero tolerance

### 18.5 Implementation Roadmap

**Week 1-2: Core Implementation**
- [ ] Markdown parser + AST traverser
- [ ] Translation Memory Manager
- [ ] AI Translator with retry logic
- [ ] Basic CLI with smart defaults
- [ ] Dry-run mode

**Week 3: UX Polish**
- [ ] Progress bars with tqdm
- [ ] Color-coded output with rich
- [ ] Pre-flight validation
- [ ] Helpful error messages

**Week 4: Testing & Documentation**
- [ ] Unit tests (80% coverage)
- [ ] Integration tests with golden files
- [ ] User documentation
- [ ] Team training session

**Post v1.0.0: Continuous Improvement**
- Monitor cache hit rates
- Collect user feedback
- Tune preserve_terms list
- Optimize API costs

### 18.6 Risk Assessment for v1.0.0

| Risk | Mitigation | Status |
| --- | --- | --- |
| Round-trip rendering | Use mdformat library | ✅ Acceptable |
| Context loss | Sliding window (future) | ⚠️ Known limitation |
| API rate limits | Token bucket + retry | ✅ Handled |
| Cost overruns | Translation Memory + dry-run | ✅ Prevented |
| Poor UX | Progress bars + smart defaults | ✅ Addressed |

### 18.7 Confidence Level

**Recommendation**: ✅ **GREEN LIGHT for v1.0.0 Development**

**Reasoning**:
1. **Architecture is sound**: Based on industry-standard CAT tools
2. **Feature set is complete**: Solves real problems without bloat
3. **Cost is optimized**: 87% savings via Translation Memory
4. **UX is polished**: Smart defaults + visual feedback
5. **Risks are mitigated**: All critical challenges addressed

**Next Step**: Begin implementation following TDD specifications.

**Estimated Development Time**: 2-3 weeks (one developer)

**Expected ROI**: 
- Development cost: ~80 hours
- Annual time saved: ~240 hours (team of 10, 2 hours/month each)
- Annual cost saved: $108 in API fees
- Payback period: < 1 month

**This is not just a tool - it's a force multiplier for documentation workflows.** 🚀

---

## 19. Approval

**Go-Live Checklist**:
- [x] Technical design complete
- [ ] Prototype with 5 sample documents tested
- [ ] Round-trip rendering quality validated
- [ ] Cost per document measured and approved
- [ ] preserve_terms list populated with all project terms
- [ ] Error handling tested (rate limits, timeouts)
- [ ] Documentation for tool usage written
- [ ] Team trained on tool and workflow

**Success Metrics** (measured after 1 month):
- Translation time reduced by 80% (from 2-4 hours to 10-15 minutes)
- 95%+ translation accuracy (measured by spot-check reviews)
- Zero Markdown structure breakage
- API cost < $50/month for team of 10

### 18.3 Recommendations

**For MVP (Week 1-2)**:
1. Implement core pipeline with `mdformat` for rendering
2. Test with 10 existing documents
3. Manually review all translations
4. Focus on Vietnamese ↔ English only

**For V1.0 (Week 3-4)**:
1. Implement Token Bucket Rate Limiter
2. Add sliding window context
3. Build comprehensive preserve_terms list
4. Create user documentation

**For Future Versions**:
1. Custom renderer for perfect formatting preservation
2. Support for additional languages
3. GitHub Actions integration
4. Translation memory database
5. Quality metrics dashboard

---

## 19. Approval

**Reviewed By**:
- [ ] Tech Lead: @Name
- [ ] Documentation Team Lead: @Name
- [ ] Senior Backend Engineer: @Name

**Approved By**: @Tech Lead
**Approval Date**: DD MMM YYYY

---

## Changelog

### Version 1.1.0 (26 Dec 2024)

**Enhanced Configuration Management**:
- Added Section 7.1.0.1: Persistent Configuration Management with YAML config file
- Added Section 7.1.0.2: Enhanced Model Selection with dynamic model discovery
- Added Section 7.1.0.3: Secure API Key Input and Validation workflow
- Added Section 7.1.0.4: Quick Reconfiguration Commands (`docs-translator config`)
- Enhanced Section 8.1: Multi-source API Key Management (keyring, env, file)
- Added ModelRegistry class with cost/context metadata for all major models
- Added ModelFetcher abstract class for provider-specific model discovery
- Added SecureKeyManager class for secure API key resolution
- Added configuration priority hierarchy (project > user > env > defaults)
- Added `docs-translator config show` command design
- Added `docs-translator config use/model/style` quick commands
- Updated security design with .gitignore requirements

### Version 1.0.0 (26 Dec 2024)

**Initial Draft**:
- Complete technical design based on instruction.md requirements
- Architecture with 4-component pipeline (Parser → Traverser → Translator → Renderer)
- Python implementation using markdown-it-py and LLM APIs
- Security considerations for API key management
- Performance optimization strategies (batching, caching, parallelization)
- Comprehensive testing and deployment plan
