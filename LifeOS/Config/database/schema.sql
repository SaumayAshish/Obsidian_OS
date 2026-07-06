-- LifeOS PostgreSQL schema
-- Requires PostgreSQL 15+.
-- Phase 3 intentionally does not require pgvector.
-- Raw Markdown note bodies are intentionally not stored.

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE SCHEMA IF NOT EXISTS lifeos;

SET search_path TO lifeos, public;

CREATE TABLE IF NOT EXISTS notes (
    id BIGSERIAL PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    note_type TEXT NOT NULL DEFAULT 'note',
    status TEXT NOT NULL DEFAULT 'active',
    tags TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    file_mtime TIMESTAMPTZ NOT NULL,
    content_hash TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_notes_type ON notes (note_type);
CREATE INDEX IF NOT EXISTS idx_notes_status ON notes (status);
CREATE INDEX IF NOT EXISTS idx_notes_tags ON notes USING gin (tags);
CREATE INDEX IF NOT EXISTS idx_notes_metadata ON notes USING gin (metadata);

CREATE TABLE IF NOT EXISTS tasks (
    id BIGSERIAL PRIMARY KEY,
    note_id BIGINT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    source_path TEXT NOT NULL,
    source_line INTEGER NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    priority TEXT,
    due_date DATE,
    scheduled_date DATE,
    completed_at TIMESTAMPTZ,
    project TEXT,
    goal TEXT,
    tags TEXT[] NOT NULL DEFAULT '{}',
    external_id TEXT NOT NULL UNIQUE,
    synced_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_tasks_status_due ON tasks (status, due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks (project);
CREATE INDEX IF NOT EXISTS idx_tasks_goal ON tasks (goal);
CREATE INDEX IF NOT EXISTS idx_tasks_tags ON tasks USING gin (tags);

CREATE TABLE IF NOT EXISTS goals (
    id BIGSERIAL PRIMARY KEY,
    note_id BIGINT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    level TEXT NOT NULL CHECK (level IN ('vision', 'annual', 'quarterly', 'weekly')),
    parent_goal_id BIGINT REFERENCES goals(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'active',
    start_date DATE,
    target_date DATE,
    progress NUMERIC(5,2) NOT NULL DEFAULT 0,
    metric_name TEXT,
    metric_target NUMERIC,
    metric_current NUMERIC,
    synced_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_goals_level_status ON goals (level, status);
CREATE INDEX IF NOT EXISTS idx_goals_parent ON goals (parent_goal_id);

CREATE TABLE IF NOT EXISTS habit_definitions (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT,
    target_frequency TEXT NOT NULL DEFAULT 'daily',
    active BOOLEAN NOT NULL DEFAULT true,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS habit_logs (
    id BIGSERIAL PRIMARY KEY,
    habit_id BIGINT NOT NULL REFERENCES habit_definitions(id) ON DELETE CASCADE,
    note_id BIGINT REFERENCES notes(id) ON DELETE SET NULL,
    log_date DATE NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT false,
    value NUMERIC,
    unit TEXT,
    source_line INTEGER,
    synced_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (habit_id, log_date)
);

CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs (log_date);
CREATE INDEX IF NOT EXISTS idx_habit_logs_habit_date ON habit_logs (habit_id, log_date);

CREATE TABLE IF NOT EXISTS finance_transactions (
    id BIGSERIAL PRIMARY KEY,
    note_id BIGINT REFERENCES notes(id) ON DELETE SET NULL,
    tx_date DATE NOT NULL,
    account TEXT,
    category TEXT NOT NULL,
    merchant TEXT,
    description TEXT,
    amount NUMERIC(12,2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'INR',
    tx_type TEXT NOT NULL CHECK (tx_type IN ('expense', 'income', 'transfer', 'investment', 'saving')),
    tags TEXT[] NOT NULL DEFAULT '{}',
    source_line INTEGER,
    external_id TEXT NOT NULL UNIQUE,
    synced_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_finance_date_type ON finance_transactions (tx_date, tx_type);
CREATE INDEX IF NOT EXISTS idx_finance_category ON finance_transactions (category);
CREATE INDEX IF NOT EXISTS idx_finance_tags ON finance_transactions USING gin (tags);

CREATE TABLE IF NOT EXISTS subscriptions (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT,
    amount NUMERIC(12,2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'INR',
    billing_cycle TEXT NOT NULL,
    next_due_date DATE,
    active BOOLEAN NOT NULL DEFAULT true,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS note_chunks (
    id BIGSERIAL PRIMARY KEY,
    note_id BIGINT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    heading_path TEXT,
    chunk_hash TEXT NOT NULL,
    token_estimate INTEGER NOT NULL,
    summary TEXT,
    keywords TEXT[] NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (note_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_note_chunks_keywords ON note_chunks USING gin (keywords);
CREATE INDEX IF NOT EXISTS idx_note_chunks_metadata ON note_chunks USING gin (metadata);

CREATE TABLE IF NOT EXISTS embeddings (
    id BIGSERIAL PRIMARY KEY,
    chunk_id BIGINT NOT NULL UNIQUE REFERENCES note_chunks(id) ON DELETE CASCADE,
    embedding_model TEXT NOT NULL,
    embedding_text TEXT NOT NULL,
    dimensions INTEGER,
    provider TEXT NOT NULL DEFAULT 'text',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings (embedding_model);

CREATE TABLE IF NOT EXISTS ai_memory_items (
    id BIGSERIAL PRIMARY KEY,
    note_id BIGINT REFERENCES notes(id) ON DELETE SET NULL,
    memory_type TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    importance INTEGER NOT NULL DEFAULT 3 CHECK (importance BETWEEN 1 AND 5),
    valid_from DATE,
    valid_until DATE,
    tags TEXT[] NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ai_memory_type ON ai_memory_items (memory_type);
CREATE INDEX IF NOT EXISTS idx_ai_memory_tags ON ai_memory_items USING gin (tags);

CREATE TABLE IF NOT EXISTS daily_metrics (
    metric_date DATE PRIMARY KEY,
    mood INTEGER CHECK (mood BETWEEN 1 AND 5),
    productivity INTEGER CHECK (productivity BETWEEN 1 AND 10),
    sleep_hours NUMERIC(4,2),
    tasks_opened INTEGER NOT NULL DEFAULT 0,
    tasks_completed INTEGER NOT NULL DEFAULT 0,
    habits_completed INTEGER NOT NULL DEFAULT 0,
    habits_total INTEGER NOT NULL DEFAULT 0,
    expense_total NUMERIC(12,2) NOT NULL DEFAULT 0,
    learning_minutes INTEGER NOT NULL DEFAULT 0,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    synced_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sync_runs (
    id BIGSERIAL PRIMARY KEY,
    run_type TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    files_scanned INTEGER NOT NULL DEFAULT 0,
    rows_changed INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE OR REPLACE VIEW task_summary AS
SELECT
    status,
    count(*) AS task_count,
    count(*) FILTER (WHERE due_date < current_date AND status <> 'done') AS overdue_count,
    count(*) FILTER (WHERE due_date = current_date AND status <> 'done') AS due_today_count
FROM tasks
GROUP BY status;

CREATE OR REPLACE VIEW monthly_finance_summary AS
SELECT
    date_trunc('month', tx_date)::date AS month,
    tx_type,
    category,
    currency,
    sum(amount) AS total_amount
FROM finance_transactions
GROUP BY 1, 2, 3, 4;

CREATE OR REPLACE VIEW habit_completion_daily AS
SELECT
    log_date,
    count(*) AS habit_count,
    count(*) FILTER (WHERE completed) AS completed_count,
    CASE
        WHEN count(*) = 0 THEN 0
        ELSE round((count(*) FILTER (WHERE completed))::numeric * 100 / count(*), 2)
    END AS completion_rate
FROM habit_logs
GROUP BY log_date;

CREATE OR REPLACE VIEW dashboard_backend_summary AS
SELECT
    (SELECT count(*) FROM tasks WHERE status <> 'done') AS open_tasks,
    (SELECT count(*) FROM tasks WHERE status <> 'done' AND due_date = current_date) AS tasks_due_today,
    (SELECT count(*) FROM tasks WHERE status <> 'done' AND due_date < current_date) AS overdue_tasks,
    (SELECT count(*) FROM goals WHERE status = 'active') AS active_goals,
    (SELECT coalesce(sum(amount), 0) FROM finance_transactions WHERE tx_type = 'expense' AND tx_date >= date_trunc('month', current_date)) AS month_expenses,
    (SELECT coalesce(round(avg(completion_rate), 2), 0) FROM habit_completion_daily WHERE log_date >= current_date - interval '7 days') AS habit_completion_7d;

CREATE OR REPLACE VIEW embedding_storage_status AS
SELECT
    embedding_model,
    provider,
    count(*) AS embedding_count,
    max(created_at) AS last_created_at
FROM embeddings
GROUP BY embedding_model, provider;
