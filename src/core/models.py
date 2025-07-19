from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class PromptTemplate(BaseModel):
    id: str
    name: str
    template: str
    variables: List[str]
    description: Optional[str] = None

    @validator('template')
    def validate_template(cls, v):
        if not v.strip():
            raise ValueError('Template cannot be empty')
        return v

class TaskRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    channel_id: str
    input_text: str = Field(..., min_length=1, max_length=4000)
    prompt_template_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TaskResponse(BaseModel):
    id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    tokens_used: Optional[int] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrchestrationResult(BaseModel):
    task_id: str
    subtasks: List[TaskResponse]
    final_result: Dict[str, Any]
    total_processing_time: float
    total_tokens_used: int
