from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"
    __table_args__ = {"schema": "lifeos"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    path: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    note_type: Mapped[str] = mapped_column(Text, nullable=False, default="note")
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    file_mtime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    content_hash: Mapped[str] = mapped_column(Text, nullable=False)
    note_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = {"schema": "lifeos"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("lifeos.notes.id", ondelete="CASCADE"), nullable=False)
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    source_line: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="open")
    priority: Mapped[str | None] = mapped_column(Text)
    due_date: Mapped[date | None] = mapped_column(Date)
    scheduled_date: Mapped[date | None] = mapped_column(Date)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    project: Mapped[str | None] = mapped_column(Text)
    goal: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    external_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Goal(Base):
    __tablename__ = "goals"
    __table_args__ = {"schema": "lifeos"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("lifeos.notes.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(Text, nullable=False)
    parent_goal_id: Mapped[int | None] = mapped_column(ForeignKey("lifeos.goals.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    start_date: Mapped[date | None] = mapped_column(Date)
    target_date: Mapped[date | None] = mapped_column(Date)
    progress: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    metric_name: Mapped[str | None] = mapped_column(Text)
    metric_target: Mapped[Decimal | None] = mapped_column(Numeric)
    metric_current: Mapped[Decimal | None] = mapped_column(Numeric)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class HabitDefinition(Base):
    __tablename__ = "habit_definitions"
    __table_args__ = {"schema": "lifeos"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    category: Mapped[str | None] = mapped_column(Text)
    target_frequency: Mapped[str] = mapped_column(Text, nullable=False, default="daily")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    habit_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class HabitLog(Base):
    __tablename__ = "habit_logs"
    __table_args__ = (UniqueConstraint("habit_id", "log_date"), {"schema": "lifeos"})

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("lifeos.habit_definitions.id", ondelete="CASCADE"), nullable=False)
    note_id: Mapped[int | None] = mapped_column(ForeignKey("lifeos.notes.id", ondelete="SET NULL"))
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    value: Mapped[Decimal | None] = mapped_column(Numeric)
    unit: Mapped[str | None] = mapped_column(Text)
    source_line: Mapped[int | None] = mapped_column(Integer)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class FinanceTransaction(Base):
    __tablename__ = "finance_transactions"
    __table_args__ = {"schema": "lifeos"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    note_id: Mapped[int | None] = mapped_column(ForeignKey("lifeos.notes.id", ondelete="SET NULL"))
    tx_date: Mapped[date] = mapped_column(Date, nullable=False)
    account: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    merchant: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(Text, nullable=False, default="INR")
    tx_type: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    source_line: Mapped[int | None] = mapped_column(Integer)
    external_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = {"schema": "lifeos"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    category: Mapped[str | None] = mapped_column(Text)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(Text, nullable=False, default="INR")
    billing_cycle: Mapped[str] = mapped_column(Text, nullable=False)
    next_due_date: Mapped[date | None] = mapped_column(Date)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    subscription_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class NoteChunk(Base):
    __tablename__ = "note_chunks"
    __table_args__ = (UniqueConstraint("note_id", "chunk_index"), {"schema": "lifeos"})

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("lifeos.notes.id", ondelete="CASCADE"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    heading_path: Mapped[str | None] = mapped_column(Text)
    chunk_hash: Mapped[str] = mapped_column(Text, nullable=False)
    token_estimate: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    keywords: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    chunk_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class EmbeddingRecord(Base):
    __tablename__ = "embeddings"
    __table_args__ = {"schema": "lifeos"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chunk_id: Mapped[int] = mapped_column(ForeignKey("lifeos.note_chunks.id", ondelete="CASCADE"), nullable=False, unique=True)
    embedding_model: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_text: Mapped[str] = mapped_column(Text, nullable=False)
    dimensions: Mapped[int | None] = mapped_column(Integer)
    provider: Mapped[str] = mapped_column(Text, nullable=False, default="text")
    embedding_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class AiMemoryItem(Base):
    __tablename__ = "ai_memory_items"
    __table_args__ = {"schema": "lifeos"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    note_id: Mapped[int | None] = mapped_column(ForeignKey("lifeos.notes.id", ondelete="SET NULL"))
    memory_type: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    valid_from: Mapped[date | None] = mapped_column(Date)
    valid_until: Mapped[date | None] = mapped_column(Date)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    memory_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class DailyMetric(Base):
    __tablename__ = "daily_metrics"
    __table_args__ = {"schema": "lifeos"}

    metric_date: Mapped[date] = mapped_column(Date, primary_key=True)
    mood: Mapped[int | None] = mapped_column(Integer)
    productivity: Mapped[int | None] = mapped_column(Integer)
    sleep_hours: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    tasks_opened: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tasks_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    habits_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    habits_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    expense_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    learning_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metric_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class SyncRun(Base):
    __tablename__ = "sync_runs"
    __table_args__ = {"schema": "lifeos"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    run_type: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    files_scanned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_changed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error: Mapped[str | None] = mapped_column(Text)
    sync_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
