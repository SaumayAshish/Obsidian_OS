CONTRIBUTING.md

# Contributing to Obsidian_OS

Thank you for your interest in contributing to this portfolio project! This guide will help you understand how to set up the environment, make changes, and submit pull requests.

---

## Getting Started

### Prerequisites

- Python 3.10+
- Git
- Docker & Docker Compose
- Obsidian (for vault testing)

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SaumayAshish/Obsidian_OS.git
   cd Obsidian_OS
   ```

2. **Set up the Python environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r LifeOS/Scripts/requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Start the local Postgres service:**
   ```bash
   docker-compose up -d
   ```

4. **Initialize the database:**
   ```bash
   python LifeOS/Scripts/bootstrap_db.py
   ```

5. **Run tests:**
   ```bash
   pytest LifeOS/Scripts/tests/ -v
   ```

---

## Code Style & Quality

This project enforces strict code quality standards using pre-commit hooks and linting.

### Before You Commit

1. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

2. **Run pre-commit on your changes:**
   ```bash
   pre-commit run --all-files
   ```

3. **Fix linting issues:**
   - Pre-commit will auto-fix many issues (formatting, trailing whitespace)
   - For flake8 violations, review `.flake8` and fix manually or ask in your PR

### Linting Standards

- **Max line length:** 180 characters (see `.flake8`)
- **Python version:** 3.10+
- **Formatter:** Auto-formatted by pre-commit
- **Docstring style:** Google style (though not strictly enforced for brevity)
- **Ignored rules:** D100-D107 (module/file docstrings), W391 (blank lines)

---

## Making Changes

### Branch Naming

- Feature: `feature/description`
- Bugfix: `fix/description`
- Docs: `docs/description`
- Chore: `chore/description`

Example: `feature/semantic-search-filtering` or `docs/architecture-updates`

### Commit Messages

Use the conventional commit format:

```
type(scope): description

Optional detailed explanation.

Co-authored-by: Your Name <your.email@example.com>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `chore` - Infrastructure, config
- `ci` - CI/CD workflows
- `refactor` - Code restructuring (no behavior change)
- `test` - Tests
- `perf` - Performance improvement

**Scope Examples:**
- `sync` - Changes to sync logic
- `db` - Schema or database changes
- `api` - REST API changes
- `rag` - RAG/semantic search changes
- `ci` - GitHub Actions workflows
- `infra` - Docker, dependencies, config

**Examples:**
```
feat(sync): add error recovery for failed markdown parses
fix(db): handle unicode characters in note titles
docs(architecture): update Phase 3 backend sync details
ci: improve GitHub Actions matrix test coverage
```

### Testing

- Write tests for new features in `LifeOS/Scripts/tests/`
- Use `pytest` as the test runner
- Aim for >80% code coverage on new logic
- Run tests locally before pushing:
  ```bash
  pytest LifeOS/Scripts/tests/ -v --cov
  ```

### Database Changes

- Schema changes go in `LifeOS/Config/database/schema.sql`
- Migrations go in separate files (e.g., `LifeOS/Config/database/migrations/`)
- Document migration steps in comments
- Test migrations against a fresh Docker Postgres instance

---

## Submitting a Pull Request

1. **Push your branch:**
   ```bash
   git push origin feature/your-description
   ```

2. **Open a pull request on GitHub:**
   - Title: Follow conventional commit format
   - Description: Explain *why* this change, not just *what*
   - Reference related issues if any
   - Add screenshots or demo GIFs if UI/behavior changed

3. **PR checklist:**
   - ✅ Pre-commit hooks pass (`pre-commit run --all-files`)
   - ✅ Tests pass (`pytest LifeOS/Scripts/tests/ -v`)
   - ✅ No new linting violations (flake8 quiet)
   - ✅ Commit messages follow conventional format
   - ✅ Documentation updated (if needed)
   - ✅ No secrets or credentials committed

4. **Review process:**
   - CI must pass (GitHub Actions)
   - Maintainer will review and request changes if needed
   - Address feedback and push updates to the same branch
   - PR will be squashed and merged when approved

---

## Architecture & Design Patterns

### Key Principles

1. **Markdown is the source of truth.** All content originates in Markdown; DB stores metadata only.
2. **Idempotency first.** Sync operations use `ON CONFLICT DO UPDATE` to handle re-runs safely.
3. **Local-first, cloud-optional.** Default to local (Ollama, sentence-transformers); cloud services optional.
4. **Token efficiency.** Minimize tokens sent to LLMs; compress context before generation.
5. **Separation of concerns.** Sync, chunking, embedding, and retrieval are separate modules.

### File Organization

```
LifeOS/Scripts/
├── requirements.txt                 # Project dependencies
├── .env.example                     # Template for .env (secrets)
├── bootstrap_db.py                  # Sample data for CI/tests
├── sync_vault.py                    # Main entry point for Markdown sync
├── index_embeddings.py              # Build semantic index
├── semantic_search.py               # Query & retrieve
├── backup_lifeos.py                 # Backup automation
├── run_daily_automation.py          # Daily tasks coordinator
├── lifeos_sync/
│   ├── __init__.py
│   ├── config.py                    # Config & env loading
│   ├── models.py                    # SQLAlchemy ORM
│   ├── markdown.py                  # Markdown parser (Frontmatter, code blocks)
│   ├── sync.py                      # Upsert logic
│   ├── chunker.py                   # Semantic chunking
│   ├── embedding_service.py         # Local or stub embeddings
│   ├── retrieval.py                 # Search & compression
│   ├── analytics.py                 # Aggregations
│   ├── validation.py                # Schema validation
│   └── vector_index.py              # pgvector operations
└── tests/
    ├── test_markdown_parser.py
    ├── test_chunker.py
    └── test_*.py
```

### When Adding New Features

1. Add schema changes to `LifeOS/Config/database/schema.sql`
2. Create a new Python module in `lifeos_sync/` (e.g., `lifeos_sync/feature_name.py`)
3. Add unit tests to `LifeOS/Scripts/tests/test_feature_name.py`
4. Update the appropriate entry point (sync_vault.py, index_embeddings.py, etc.)
5. Document the feature in `LifeOS/Config/` docs
6. Update ARCHITECTURE.md if it affects system design

---

## Reporting Issues

If you find a bug or have a suggestion:

1. Check existing issues to avoid duplicates
2. Open an issue with:
   - Clear title
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Environment (OS, Python version, etc.)
   - Any error messages or logs

---

## Questions?

Open a discussion or issue on GitHub. We're happy to help!

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License (see LICENSE file).

---

Thank you for contributing to Obsidian_OS! 🚀
