# Markdown Translator

AI-powered documentation translator with Markdown structure preservation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Getting Started (30 seconds)

**Fastest way - No Python installation needed:**

```bash
# 1. Download docs-translator.exe (Windows only)
# 2. Configure API key (first time)
docs-translator configure

# 3. Start translating!
docs-translator translate --file README.md --source vi --target en
```

Done! Output saved to `README_en.md`

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

### Option 1: Using Standalone Executable (Recommended)

**Windows (Pre-built):**

1. Download `docs-translator.exe` from the [releases page](https://github.com/agrios/docs-translator/releases)
2. Place it in a directory in your `PATH` or run it directly:
   ```bash
   docs-translator --help
   ```

**No Python installation required!**

### Option 2: Using pip

```bash
git clone https://github.com/ttcagris/ttcagris-markdown-translator.git
cd ttcagris-markdown-translator
pip install -e .
```

### Option 3: Using conda

```bash
conda create -n docs-translator python=3.11 -y
conda activate docs-translator
pip install -e .
```

## Quick Start

### Quick Start with Executable

If you have `docs-translator.exe`:

```bash
# First time: Configure API key
docs-translator configure

# Translate a file
docs-translator translate --file doc.md --source vi --target en

# View results
cat doc_en.md
```

### Quick Start with Python Installation

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

### Default Models (Optional)

You can override default models via environment variables:

```bash
# .env (optional - defaults shown)
DOCS_TRANSLATOR_GEMINI_MODEL=gemini-2.0-flash
DOCS_TRANSLATOR_OPENAI_MODEL=gpt-4o-mini
DOCS_TRANSLATOR_CLAUDE_MODEL=claude-3-5-sonnet-20241022
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

## Building Executable from Source

If you want to build your own `docs-translator.exe`:

### Prerequisites for Building

```bash
# Setup conda environment (Windows Git Bash)
source ~/.bashrc
conda activate docs-translator
pip install pyinstaller
```

### Build on Windows

**Using PowerShell:**
```powershell
cd path\to\docs-translator
.\build.ps1
```

**Using Git Bash:**
```bash
cd path/to/docs-translator
bash build.sh
```

**Manual Build:**
```bash
cd path/to/docs-translator
pyinstaller --onefile --name docs-translator --distpath ./dist -w docs_translator/cli/main.py
```

### Output

After successful build:
- **Executable location**: `./dist/docs-translator.exe`
- **Size**: ~40-50 MB (includes all dependencies)
- **No Python required to run!**

### Distribution

To share with your team:
1. Copy `./dist/docs-translator.exe` to a shared location
2. Each user can run it directly or add it to their `PATH`
3. First run will prompt for API key configuration (stored securely)

### Troubleshooting Build Issues

| Issue | Solution |
|-------|----------|
| `pyinstaller: command not found` | Run `pip install pyinstaller==6.5.0` |
| `module not found` | Ensure you're in the conda environment with all deps installed |
| Antivirus blocking exe | Some antivirus software may flag PyInstaller-generated executables. Add to whitelist if needed |
| Very large exe size | Normal - includes Python runtime + all dependencies (Google AI, OpenAI, Claude APIs) |

### Verification & Testing

**Executable Build Status:** ✅ Verified and tested

The `docs-translator.exe` has been built and tested on Windows with the following results:

#### Test Results

| Test | Result | Details |
|------|--------|---------|
| Config Display | ✅ Pass | `docs-translator config show` displays API configuration correctly |
| Quick Translate | ✅ Pass | `docs-translator quick "Xin chào" --target en` → Output: "Hello" |
| File Translation | ✅ Pass | 7/9 blocks translated in 8.77s, cache working correctly |

#### Performance Metrics

- **Startup Time**: ~5 seconds (first run, exe unpacking)
- **Subsequent Runs**: ~2-3 seconds
- **File Size**: 41 MB (includes Python runtime + all AI provider SDKs)
- **Memory Usage**: ~200-300 MB during execution
- **No External Dependencies**: Runs standalone without Python installation

#### Sample Output

```bash
$ docs-translator quick "Xin chào thế giới" --target en
Original (vi): Xin chào thế giới
Translated (en): Hello world
```

```bash
$ docs-translator translate --file test.md --source vi --target en

Translation complete!
Output: test_en.md

     Statistics
 Metric        Value
 Total blocks      9
 Translated        7
 From cache        0
 Skipped           2
 Duration      8.77s
```

#### Known Issues

- **Google Generativeai FutureWarning**: Harmless warning from deprecated package, functionality works correctly
- **First Run Delay**: Executable unpacks all dependencies on first execution (~5s)
- **Antivirus**: Some antivirus may flag PyInstaller-generated executables as suspicious; safe to whitelist

## Project Structure

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
