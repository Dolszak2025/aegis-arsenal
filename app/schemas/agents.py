"""Pydantic schemas for request/response validation"""

from datetime import datetime
from typing import Optional, Any, Dict
from enum import Enum
from pydantic import BaseModel, Field
import uuid


# Enums (mirrored from models)
class AgentTypeSchema(str, Enum):
    TOOL = "tool"
    MODEL = "model"
    WORKER = "worker"


class AgentStatusSchema(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class ExecutionStatusSchema(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStatusSchema(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


# Agent Schemas
class AgentCreate(BaseModel):
    """Schema for creating an agent"""
    name: str = Field(..., min_length=1, max_length=255)
    type: AgentTypeSchema
    config: Dict[str, Any] = Field(default_factory=dict)
    created_by: Optional[str] = None


class AgentUpdate(BaseModel):
    """Schema for updating an agent"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    config: Optional[Dict[str, Any]] = None
    status: Optional[AgentStatusSchema] = None


class AgentResponse(BaseModel):
    """Schema for agent response"""
    id: uuid.UUID
    name: str
    type: AgentTypeSchema
    config: Dict[str, Any]
    status: AgentStatusSchema
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    """Schema for list of agents"""
    total: int
    items: list[AgentResponse]
    page: int = 1
    page_size: int = 10


# Agent Execution Schemas
class AgentExecutionCreate(BaseModel):
    """Schema for creating an agent execution"""
    agent_id: uuid.UUID
    input: Optional[Dict[str, Any]] = None


class AgentExecutionResponse(BaseModel):
    """Schema for agent execution response"""
    id: uuid.UUID
    agent_id: uuid.UUID
    status: ExecutionStatusSchema
    input: Optional[Dict[str, Any]]
    output: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Workflow Schemas
class WorkflowCreate(BaseModel):
    """Schema for creating a workflow"""
    name: str = Field(..., min_length=1, max_length=255)
    definition: Dict[str, Any]
    created_by: Optional[str] = None


class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow"""
    name: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    status: Optional[WorkflowStatusSchema] = None


class WorkflowResponse(BaseModel):
    """Schema for workflow response"""
    id: uuid.UUID
    name: str
    definition: Dict[str, Any]
    status: WorkflowStatusSchema
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True


# Task Schemas
class TaskCreate(BaseModel):
    """Schema for creating a task"""
    name: str = Field(..., min_length=1)
    task_type: str = Field(..., min_length=1)
    payload: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """Schema for task response"""
    id: uuid.UUID
    name: str
    task_type: str
    status: ExecutionStatusSchema
    payload: Optional[Dict[str, Any]]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Health Check Response
class HealthCheckResponse(BaseModel):
    """Schema for health check response"""
    status: str
    version: str
    database: str
    timestamp: datetime


# Metrics Response
class MetricsResponse(BaseModel):
    """Schema for system metrics"""
    total_agents: int
    total_executions: int
    total_workflows: int
    total_tasks: int
    failed_executions: int
    average_execution_time_ms: float


# Export all schemas
__all__ = [
    "AgentTypeSchema",
    "AgentStatusSchema",
    "ExecutionStatusSchema",
    "WorkflowStatusSchema",
    "AgentCreate",
    "AgentUpdate",
    "AgentResponse",
    "AgentListResponse",
    "AgentExecutionCreate",
    "AgentExecutionResponse",
    "WorkflowCreate",
    "WorkflowUpdate",
    "WorkflowResponse",
    "TaskCreate",
    "TaskResponse",
    "HealthCheckResponse",
    "MetricsResponse",
]
