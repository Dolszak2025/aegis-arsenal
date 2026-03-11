"""SQLAlchemy models for Aegis Arsenal"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, JSON, Enum as SQLEnum, ForeignKey, Integer, Text, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


# Enums
class AgentType(str, Enum):
    TOOL = "tool"
    MODEL = "model"
    WORKER = "worker"


class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


# Models
class Agent(Base):
    """Agent configuration model"""
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    type = Column(SQLEnum(AgentType), nullable=False)
    config = Column(JSONB, nullable=False, default={})
    status = Column(SQLEnum(AgentStatus), nullable=False, default=AgentStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))

    # Relationships
    executions = relationship("AgentExecution", back_populates="agent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, type={self.type}, status={self.status})>"


class AgentExecution(Base):
    """Agent execution history model"""
    __tablename__ = "agent_executions"
    __table_args__ = (
        Index("idx_agent_executions_agent_id", "agent_id"),
        Index("idx_agent_executions_status", "status"),
        Index("idx_agent_executions_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)
    status = Column(SQLEnum(ExecutionStatus), nullable=False, default=ExecutionStatus.PENDING, index=True)
    input = Column(JSONB)
    output = Column(JSONB)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    agent = relationship("Agent", back_populates="executions")

    def __repr__(self):
        return f"<AgentExecution(id={self.id}, agent_id={self.agent_id}, status={self.status})>"


class Workflow(Base):
    """Workflow definition model"""
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    definition = Column(JSONB, nullable=False)
    status = Column(SQLEnum(WorkflowStatus), nullable=False, default=WorkflowStatus.DRAFT, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))

    # Relationships
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Workflow(id={self.id}, name={self.name}, status={self.status})>"


class WorkflowExecution(Base):
    """Workflow execution history model"""
    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False, index=True)
    status = Column(SQLEnum(ExecutionStatus), nullable=False, default=ExecutionStatus.PENDING, index=True)
    execution_log = Column(JSONB)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    workflow = relationship("Workflow", back_populates="executions")

    def __repr__(self):
        return f"<WorkflowExecution(id={self.id}, workflow_id={self.workflow_id}, status={self.status})>"


class Task(Base):
    """Task/Job model for background work"""
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    task_type = Column(String(100), nullable=False)
    status = Column(SQLEnum(ExecutionStatus), nullable=False, default=ExecutionStatus.PENDING, index=True)
    payload = Column(JSONB)
    result = Column(JSONB)
    error_message = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    def __repr__(self):
        return f"<Task(id={self.id}, name={self.name}, type={self.task_type}, status={self.status})>"


class AuditLog(Base):
    """Audit logging for compliance and debugging"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100))
    user_id = Column(String(100))
    details = Column(JSONB)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, entity_type={self.entity_type})>"


# Export all models
__all__ = [
    "Base",
    "Agent",
    "AgentExecution",
    "Workflow",
    "WorkflowExecution",
    "Task",
    "AuditLog",
    "AgentType",
    "AgentStatus",
    "ExecutionStatus",
    "WorkflowStatus",
]
