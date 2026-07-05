Setup & Demo Guide for Obsidian_OS (LifeOS)

## Local Development Setup (15 minutes)

### Prerequisites
- Python 3.10+ (check: python --version)
- Docker & Docker Compose (check: docker-compose --version)
- Git (check: git --version)
- Obsidian (download from obsidian.md if you want to open the vault)

### Step 1: Clone the repository

git clone https://github.com/SaumayAshish/Obsidian_OS.git
cd Obsidian_OS

### Step 2: Set up environment variables

cp LifeOS/Scripts/.env.example LifeOS/Scripts/.env

# Edit .env and set these (or leave defaults for local dev):
# DATABASE_URL=postgresql://lifeos:your_password@localhost:5432/lifeos
# POSTGRES_PASSWORD=your_password

### Step 3: Start PostgreSQL

docker-compose up -d

# Wait ~10 seconds for the database to be ready
docker-compose logs postgres | grep "database system is ready"

### Step 4: Install Python dependencies

pip install -r LifeOS/Scripts/requirements.txt
pip install -r requirements-dev.txt

### Step 5: Apply database schema

export DATABASE_URL="postgresql://lifeos:lifeos@localhost:5432/lifeos"
psql "$DATABASE_URL" -f LifeOS/Config/database/schema.sql

# Verify (should show 20+ tables)
psql "$DATABASE_URL" -c "\dt lifeos.*"

### Step 6: Bootstrap sample data

python LifeOS/Scripts/bootstrap_db.py

# Verify (should show a few rows)
psql "$DATABASE_URL" -c "SELECT count(*) as task_count FROM lifeos.tasks;"

### Step 7: Enable pre-commit hooks (optional but recommended)

pre-commit install

# Test your setup:
pre-commit run --all-files

You're ready!

---

## Demo Walkthrough (20 minutes)

Perfect for interviews or showing friends. This demonstrates the full pipeline: Markdown → DB → RAG → LLM.

### Demo Setup (prep once)

1. Make sure local dev is running (Postgres, Python deps installed).
2. Have two terminal windows open:
   - Terminal A: For running Python commands
   - Terminal B: For querying PostgreSQL

### Demo Script

#### Part 1: Show the vault (Obsidian UI)

**Terminal A:**

open LifeOS  # on macOS: just "LifeOS" in your file explorer, then open with Obsidian

# Or manually open Obsidian and choose LifeOS/ as vault

# Inside Obsidian:
# - Show Dashboard/Home.md (displays tasks, goals, habits, finance summary)
# - Show a daily note (e.g., LifeOS/Daily Notes/2026-07-05.md)
#   - Point out frontmatter: type, status, tags, created, updated
#   - Show task list items (- [ ] or - [x])
#   - Show finance items (table with merchant, amount, etc.)
# - Show a goal note (e.g., LifeOS/Goals/Goal - Learn RAG.md)

**Talking point:**
"This is the Obsidian vault—the source of truth. All my knowledge, tasks, and goals live here as Markdown. Now let's see how the system syncs this into a structured database for analytics and retrieval."

---

#### Part 2: Sync Markdown into PostgreSQL

**Terminal A:**

python LifeOS/Scripts/sync_vault.py

# Output should show:
# Sync completed: {'files': X, 'notes': Y, 'tasks': Z, ...}

**Terminal B (simultaneously or after):**

export DATABASE_URL="postgresql://lifeos:lifeos@localhost:5432/lifeos"

# Show tasks synced from Markdown:
psql "$DATABASE_URL" -c "SELECT description, status, due_date FROM lifeos.tasks LIMIT 5;"

# Show finance transactions:
psql "$DATABASE_URL" -c "SELECT tx_date, category, amount, currency FROM lifeos.finance_transactions LIMIT 3;"

# Show goals:
psql "$DATABASE_URL" -c "SELECT title, level, status, progress FROM lifeos.goals;"

**Talking point:**
"Notice that only metadata appears in the database. Raw note bodies are never stored—only structured records. This keeps the DB lean and follows the principle that Markdown is truth."

---

#### Part 3: Build semantic index

**Terminal A:**

python LifeOS/Scripts/index_embeddings.py

# Output should show:
# Indexed X chunks with embeddings

**Terminal B:**

# Show chunks in the database:
psql "$DATABASE_URL" -c "SELECT note_id, chunk_index, summary, token_estimate FROM lifeos.note_chunks LIMIT 5;"

# Show embeddings storage:
psql "$DATABASE_URL" -c "SELECT chunk_id, embedding_model, provider, dimensions FROM lifeos.embeddings LIMIT 3;"

**Talking point:**
"I've now built a semantic index by chunking notes and creating embeddings. Each chunk stores its summary, token estimate, and metadata—again, never the raw text. This keeps token usage low."

---

#### Part 4: Semantic search + RAG

**Terminal A:**

python LifeOS/Scripts/semantic_search.py "active goals and next actions" --context

# Output should show:
# Top retrieved chunks, summaries, and compressed context

**Talking point:**
"Now I query semantically: 'active goals and next actions.' The system retrieves relevant chunks, compresses their context, and prepares it for an LLM. Notice the compressed context is concise—perfect for token-efficient prompting."

(Optional: If Ollama is running locally, the script can call it directly for a real LLM response.)

---

#### Part 5: Show CI/CD maturity

**Browser (GitHub):**

Visit: https://github.com/SaumayAshish/Obsidian_OS/actions

- Show the CI workflow status
- Click into a passing run and explain:
  - Pre-commit hooks (lint on changed files)
  - flake8 linting
  - Schema validation
  - Sample data bootstrap
  - pytest tests

**Talking point:**
"This is a real DevOps setup: every push triggers automated checks. Pre-commit hooks catch issues early, flake8 ensures code quality, schema migrations are validated, and tests run against sample data. I also have scheduled maintenance jobs that auto-fix formatting issues and open PRs—something professional teams do."

---

#### Part 6: System architecture discussion

**Browser (GitHub):**

Open ARCHITECTURE.md and README.md

- Walk through the ASCII diagram
- Explain layers: Obsidian UI → Python sync → PostgreSQL → embeddings → LLM
- Mention design principles:
  - Markdown is truth
  - DB stores metadata only
  - Token efficiency (chunking, compression, filtering)
  - Local-first (Ollama preferred; cloud providers as fallback)

**Talking point:**
"The system is designed to be scalable and extensible. To add multi-user features, I'd introduce an API layer with auth and tenancy. To scale embeddings, I'd upgrade to pgvector. The phased approach ensures we don't break what's working while adding new capability."

---

## Troubleshooting

### Postgres won't start

docker-compose logs postgres

# If it fails due to port 5432 already in use:
# Kill existing postgres: docker ps | grep postgres && docker kill <container_id>
# Or change port in docker-compose.yml

### Python import errors

pip install -r LifeOS/Scripts/requirements.txt --upgrade

### Sync script fails

export DATABASE_URL="postgresql://lifeos:lifeos@localhost:5432/lifeos"
python LifeOS/Scripts/sync_vault.py --validate-only

# Check .env is set correctly:
cat LifeOS/Scripts/.env

### Pre-commit hook errors

pre-commit clean
pre-commit install

### Tests fail

pytest LifeOS/Scripts/tests -v

# Check sample data was bootstrapped:
python LifeOS/Scripts/bootstrap_db.py

---

## Next Steps

- **Customize the system:** Add your own notes, tasks, and goals to LifeOS/, then re-run sync to see them in the DB.
- **Enable pgvector:** Install pgvector on your Postgres server, then run phase4_pgvector.sql migration.
- **Connect a local LLM:** Install Ollama, set LIFEOS_OLLAMA_URL in .env, and use semantic_search.py for RAG.
- **Deploy:** Use docker-compose for dev/test; for production, consider managed Postgres (AWS RDS, Heroku, etc.) and containerized Python services (ECS, Kubernetes).

---

## Interview tips

**If asked: "Walk me through how this system scales."**

Answer: "The current setup is single-user and local. To scale:
1. Add a REST API layer (FastAPI or Django) with OAuth for multi-user auth and tenancy.
2. Migrate Postgres to managed cloud (RDS, Cloud SQL) or a cluster.
3. Move Python scripts to async workers (Celery, RQ) for background jobs.
4. Add caching (Redis) for frequently accessed queries.
5. Use pgvector for vector similarity at scale—it's more efficient than text-backed storage.
6. Consider a vector DB like Pinecone or Weaviate if embeddings exceed Postgres capacity."

**If asked: "How do you ensure data consistency?"**

Answer: "Several strategies:
1. Markdown is the source of truth—all deltas come from there.
2. Sync script is idempotent (upsert with ON CONFLICT DO UPDATE).
3. Tests with sample data ensure migrations don't break.
4. Backups via backup_lifeos.py (vault + DB dumps).
5. Pre-commit checks catch lint/syntax errors before they reach main."

**If asked: "What's your biggest learning from this project?"**

Answer: "The importance of data ownership and minimal persistence. Storing only metadata (not raw content) in the DB forces you to think about what's queryable vs. what's human-readable. It also reduces storage and token usage. This constraint actually drove better design."
