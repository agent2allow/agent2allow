from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    tool: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(128))
    repo: Mapped[str] = mapped_column(String(256))
    risk_level: Mapped[str] = mapped_column(String(16))
    request_payload: Mapped[str] = mapped_column(Text)
    result_payload: Mapped[str] = mapped_column(Text, default="{}")
    reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    agent_id: Mapped[str] = mapped_column(String(128), index=True)
    tool: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(128))
    repo: Mapped[str] = mapped_column(String(256))
    risk_level: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(64), index=True)
    request_payload: Mapped[str] = mapped_column(Text)
    response_payload: Mapped[str] = mapped_column(Text, default="{}")
    approval_id: Mapped[int | None] = mapped_column(ForeignKey("approvals.id"), nullable=True)
    message: Mapped[str] = mapped_column(Text, default="")
