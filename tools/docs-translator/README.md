# Markdown Translator

AI-powered documentation translator with Markdown structure preservation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Markdown Translator is a CLI tool designed for translating technical documentation while preserving:

- **Markdown structure**: Headings, tables, lists, blockquotes
- **Code blocks**: Fenced code blocks and inline code remain untouched
- **Technical terms**: Configurable list of terms to preserve (e.g., API names, service names)
- **Requirement IDs**: Patterns like `FR-01`, `NFR-P01`, `US-001` are never translated

## Features

- **Multi-provider support**: OpenAI GPT, Google Gemini, Anthropic Claude
- **Translation Memory**: Cache translations to avoid redundant API calls (up to 99% cost savings)
- **Smart Markdown parsing**: Uses AST-based parsing (markdown-it-py) for accurate structure preservation
- **Rate limit handling**: Automatic retry with exponential backoff
- **Batch processing**: Translate entire directories recursively
- **Interactive setup**: Wizard-based configuration for easy onboarding

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or conda

### Using pip

```bash
git clone https://github.com/ttcagris/ttcagris-markdown-translator.git
cd ttcagris-markdown-translator
pip install -e .
```

### Using conda

```bash
conda create -n docs-translator python=3.11 -y
conda activate docs-translator
pip install -e .
```

## Quick Start

### 1. Configure the tool

```bash
docs-translator configure
```

This will guide you through:
- Selecting an AI provider (Gemini, OpenAI, Claude)
- Entering your API key
- Choosing a model

### 2. Translate a file

```bash
# Basic translation (auto-detect source language)
docs-translator translate --file doc.md --target en

# Specify source and target languages
docs-translator translate --file doc.md --source vi --target en

# Specify output path
docs-translator translate --file doc.md --target vi --output doc_vi.md
```

### Supported Languages

The tool supports **any language pair** supported by the AI provider. Common language codes:

| Code | Language | Code | Language |
|------|----------|------|----------|
| `en` | English | `zh` | Chinese (Simplified) |
| `vi` | Vietnamese | `zh-TW` | Chinese (Traditional) |
| `ja` | Japanese | `ko` | Korean |
| `fr` | French | `de` | German |
| `es` | Spanish | `pt` | Portuguese |
| `ru` | Russian | `ar` | Arabic |
| `th` | Thai | `id` | Indonesian |
| `ms` | Malay | `hi` | Hindi |

**Examples:**

```bash
# Vietnamese -> English
docs-translator translate --file doc.md --source vi --target en

# English -> Japanese
docs-translator translate --file doc.md --source en --target ja

# Chinese -> Vietnamese
docs-translator translate --file doc.md --source zh --target vi

# Auto-detect source, translate to Korean
docs-translator translate --file doc.md --target ko

# French -> German
docs-translator translate --file doc.md --source fr --target de
```

### 3. Translate a directory

```bash
# Translate all .md files in a directory
docs-translator translate --dir docs/confluence --target en --recursive
```

## Configuration

### Configuration file

Configuration is stored in `docs-translator.yaml` in your working directory:

```yaml
providers:
  active: "gemini"
  gemini:
    model: "gemini-2.0-flash"
  openai:
    model: "gpt-4o-mini"
  claude:
    model: "claude-3-haiku-20240307"

translation:
  style: "literal"  # or "natural"
  temperature: 0.3

languages:
  default_source: "auto"
  default_target: "en"

preserve_terms:
  - "User Service"
  - "API Gateway"
  - "AgriOS"
```

### API Keys

API keys are stored securely in `.env` file (never commit this!):

```bash
# .env
GOOGLE_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Translation Styles

| Style | Description | Use Case |
|-------|-------------|----------|
| `literal` | Word-for-word accuracy | Technical specifications, SRS documents |
| `natural` | Idiomatic, reader-friendly | User guides, README files |

## CLI Reference

### Main Commands

```bash
# Interactive setup wizard
docs-translator configure

# Show current configuration
docs-translator config show

# Quick translate a text snippet
docs-translator quick "Hello world" --target vi
```

### Translate Command

```bash
docs-translator translate [OPTIONS]

Options:
  -f, --file PATH      Markdown file to translate
  -d, --dir PATH       Directory of Markdown files
  -o, --output PATH    Output file or directory
  -s, --source TEXT    Source language code (default: auto)
  -t, --target TEXT    Target language code (required)
  -r, --recursive      Process subdirectories
  --dry-run            Preview without translating
  --no-cache           Disable translation cache
  --clear-cache        Clear cache before translating
  -v, --verbose        Enable verbose logging
  --provider           Override provider (gemini/openai/claude)
  --model TEXT         Override model
```

### Config Commands

```bash
# Switch AI provider
docs-translator config use gemini

# Set model
docs-translator config model gemini-2.0-flash

# Set translation style
docs-translator config style literal

# Add term to preserve list
docs-translator config add-term "My Service"

# Remove term from preserve list
docs-translator config remove-term "My Service"

# Set API key interactively
docs-translator config set-key

# View cache statistics
docs-translator config cache --show

# Clear translation cache
docs-translator config cache --clear
```

## Translation Memory (Cache)

The tool uses a file-based cache to store translations:

- **Location**: `.translation_cache/` in working directory
- **Format**: JSON files with source text, translation, metadata
- **Benefits**:
  - Avoid redundant API calls for identical text
  - Resume interrupted translations
  - Incremental updates (only translate changed content)

```bash
# View cache stats
docs-translator config cache --show

# Clear cache (force re-translation)
docs-translator config cache --clear

# Or use --clear-cache flag
docs-translator translate --file doc.md --target en --clear-cache
```

## Project Structure

```
docs-translator/
├── docs_translator/
│   ├── cli/              # CLI commands and wizard
│   │   ├── main.py       # Entry point
│   │   └── wizard.py     # Interactive setup
│   ├── config/           # Configuration management
│   │   ├── manager.py    # Config loading/saving
│   │   └── models.py     # Model definitions
│   ├── parser/           # Markdown parsing
│   │   └── markdown_parser.py
│   ├── translator/       # Translation logic
│   │   ├── core.py       # Main translator
│   │   ├── providers.py  # AI provider adapters
│   │   └── prompts.py    # Translation prompts
│   └── logging.py        # Logging configuration
├── pyproject.toml        # Package configuration
├── docs-translator.yaml  # User configuration
├── .env                  # API keys (gitignored)
└── README.md
```

## Error Handling

### Rate Limiting

The tool automatically handles rate limits with exponential backoff:

- 3 retry attempts
- Wait time: 4s -> 8s -> 16s (max 60s)
- Logs warnings when retrying

### Common Errors

| Error | Solution |
|-------|----------|
| `No API key configured` | Run `docs-translator configure` or `docs-translator config set-key` |
| `Rate limit exceeded` | Wait a moment, the tool will auto-retry |
| `Model not found` | Check model name with `docs-translator config show` |

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add my feature"`
4. Push to branch: `git push origin feature/my-feature`
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [markdown-it-py](https://github.com/executablebooks/markdown-it-py) for Markdown parsing
- [Click](https://click.palletsprojects.com/) for CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- [tenacity](https://tenacity.readthedocs.io/) for retry logic
