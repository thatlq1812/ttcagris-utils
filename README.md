# TTC AgriS Utils

Monorepo chứa các công cụ hỗ trợ phát triển và vận hành cho hệ sinh thái TTC AgriS.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Repository này được tổ chức theo mô hình **Monorepo**, tập trung tất cả các công cụ, tiện ích và scripts hỗ trợ cho việc phát triển các dự án trong hệ sinh thái TTC AgriS.

### Lợi ích của Monorepo

- **Quản lý tập trung**: Clone một lần, có tất cả
- **Chia sẻ code**: Các module dùng chung dễ dàng import
- **CI/CD thống nhất**: Pipeline chung cho tất cả tools
- **Version đồng bộ**: Đảm bảo tính tương thích giữa các tools

## Repository Structure

```
ttcagris-utils/
├── tools/                      # Development & Operations Tools
│   └── docs-translator/        # AI-powered Markdown translator
│
├── libs/                       # Shared libraries (future)
│   └── (coming soon)
│
├── scripts/                    # Automation scripts (future)
│   └── (coming soon)
│
├── .gitignore
├── LICENSE
└── README.md
```

## Tools

### docs-translator

AI-powered documentation translator with Markdown structure preservation.

| Feature | Description |
|---------|-------------|
| Multi-provider | OpenAI, Google Gemini, Anthropic Claude |
| Smart parsing | AST-based Markdown parsing |
| Translation Memory | Cache for 99% cost savings |
| Batch processing | Translate entire directories |

**Quick Start:**

```bash
cd tools/docs-translator
pip install -e .
docs-translator configure
docs-translator translate --file doc.md --target en
```

[Read full documentation](tools/docs-translator/README.md)

## Getting Started

### Prerequisites

- Git
- Python 3.10+ (for Python-based tools)
- Node.js 18+ (for JS-based tools, future)

### Clone Repository

```bash
git clone https://github.com/thatlq1812/ttcagris-utils.git
cd ttcagris-utils
```

### Install a Specific Tool

Each tool has its own installation instructions. Navigate to the tool directory and follow its README:

```bash
cd tools/docs-translator
pip install -e .
```

## Development

### Adding a New Tool

1. Create a new directory under `tools/`:
   ```bash
   mkdir tools/my-new-tool
   ```

2. Add your tool's code and configuration

3. Create a `README.md` with:
   - Description
   - Installation steps
   - Usage examples
   - Configuration options

4. Update this root README to list the new tool

### Project Conventions

| Convention | Description |
|------------|-------------|
| Language | American English for docs |
| Commits | Conventional Commits format |
| Branching | `feature/`, `fix/`, `docs/` prefixes |
| Python | Use `pyproject.toml`, format with `black` |

## Roadmap

### Current Tools

- [x] **docs-translator** - Markdown documentation translator

### Planned Tools

- [ ] **log-analyzer** - Log analysis and visualization
- [ ] **api-tester** - API testing automation
- [ ] **db-migrator** - Database migration helper
- [ ] **env-manager** - Environment configuration manager

### Planned Shared Libraries

- [ ] **agris-logger** - Unified logging library
- [ ] **agris-config** - Configuration management
- [ ] **agris-cli** - CLI framework utilities

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Commit: `git commit -m "feat(tool-name): add new feature"`
5. Push: `git push origin feature/my-feature`
6. Open a Pull Request

### Commit Message Format

```
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore
Scope: tool name or 'root' for repo-level changes
```

Examples:
- `feat(docs-translator): add batch processing`
- `fix(docs-translator): handle rate limit errors`
- `docs(root): update README`

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contact

- **Organization**: TTC AgriS
- **Repository**: [github.com/thatlq1812/ttcagris-utils](https://github.com/thatlq1812/ttcagris-utils)
