"""
Enterprise-grade API layer for AI Orchestrator
FastAPI with async support, authentication, rate limiting, and comprehensive endpoints
"""
import asyncio
import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import asyncpg
import redis
from dotenv import load_dotenv
from fastapi import (BackgroundTasks, Depends, FastAPI, HTTPException,
                     Security)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Global connections
DB_POOL = None
REDIS_CLIENT = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Function that handles startup and shutdown events.
    To be used with the lifespan argument of the FastAPI constructor.
    """
    # Startup
    DB_POOL = await asyncpg.create_pool(DATABASE_URL)
    REDIS_CLIENT = redis.from_url(REDIS_URL)
    logger.info("Database and Redis connections established")

    yield

    # Shutdown
    await DB_POOL.close()
    REDIS_CLIENT.close()
    logger.info("Connections closed")


APP = FastAPI(
    title="AI Orchestrator API",
    description="Enterprise-grade API for AI-powered project orchestration",
    version="2.0.0",
    lifespan=lifespan
)

# Middleware
APP.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

APP.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Pydantic Models


class OrganizationCreate(BaseModel):
    """Organization creation model."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100)
    subscription_tier: str = Field(default="free")


class UserCreate(BaseModel):
    """User creation model."""
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(default="member")


class ProjectCreate(BaseModel):
    """Project creation model."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    topic: str = Field(..., min_length=5, max_length=1000)
    priority: str = Field(default="medium")


class OrchestrationRequest(BaseModel):
    """Orchestration request model."""
    project_id: Optional[uuid.UUID] = None
    topic: str = Field(..., min_length=5, max_length=1000)
    integration_enabled: bool = Field(default=False)
    custom_phases: Optional[List[str]] = None
    template_id: Optional[uuid.UUID] = None


class TemplateCreate(BaseModel):
    """Template creation model."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    template_data: Dict[str, Any]
    is_public: bool = Field(default=False)

# Authentication and Authorization


async def get_current_user(_: HTTPAuthorizationCredentials = Security(security)):
    """Extract and validate user from JWT token"""
    # Implement JWT validation here
    # For now, return a mock user
    return {
        "id": uuid.uuid4(),
        "organization_id": uuid.uuid4(),
        "email": "user@example.com",
        "role": "admin"
    }


async def get_organization(user: dict = Depends(get_current_user)):
    """Get user's organization"""
    async with DB_POOL.acquire() as conn:
        org = await conn.fetchrow(
            "SELECT * FROM organizations WHERE id = $1",
            user["organization_id"]
        )
        if not org:
            raise HTTPException(
                status_code=404, detail="Organization not found")
        return dict(org)

# Rate Limiting


async def check_rate_limit(user: dict = Depends(get_current_user)):
    """Check API rate limits"""
    key = f"rate_limit:{user['id']}"
    current = await REDIS_CLIENT.get(key)

    if current is None:
        await REDIS_CLIENT.setex(key, 3600, 1)  # 1 hour window
        return True

    if int(current) >= 1000:  # 1000 requests per hour
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    await REDIS_CLIENT.incr(key)
    return True

# API Endpoints


@APP.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}


@APP.get("/api/v1/organizations/current")
async def get_current_organization(
    org: dict = Depends(get_organization),
    _: bool = Depends(check_rate_limit)
):
    """Get current user's organization"""
    return org


@APP.post("/api/v1/organizations")
async def create_organization(
    org_data: OrganizationCreate,
    _: dict = Depends(get_current_user),
    __: bool = Depends(check_rate_limit)
):
    """Create a new organization"""
    async with DB_POOL.acquire() as conn:
        try:
            org_id = await conn.fetchval(
                """INSERT INTO organizations (name, slug, subscription_tier)
                   VALUES ($1, $2, $3) RETURNING id""",
                org_data.name, org_data.slug, org_data.subscription_tier
            )
            return {"id": org_id, "message": "Organization created successfully"}
        except asyncpg.UniqueViolationError as exc:
            raise HTTPException(
                status_code=400, detail="Organization slug already exists") from exc


@APP.get("/api/v1/projects")
async def list_projects(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    user: dict = Depends(get_current_user),
    _: bool = Depends(check_rate_limit)
):
    """List projects for the organization"""
    async with DB_POOL.acquire() as conn:
        query = """
            SELECT p.*, u.username as created_by_username
            FROM projects p
            LEFT JOIN users u ON p.created_by = u.id
            WHERE p.organization_id = $1
        """
        params = [user["organization_id"]]

        if status:
            query += " AND p.status = $2"
            params.append(status)

        query += (f" ORDER BY p.created_at DESC LIMIT ${len(params) + 1} "
                  f"OFFSET ${len(params) + 2}")
        params.extend([limit, offset])

        projects = await conn.fetch(query, *params)
        return [dict(project) for project in projects]


@APP.post("/api/v1/projects")
async def create_project(
    project_data: ProjectCreate,
    user: dict = Depends(get_current_user),
    _: bool = Depends(check_rate_limit)
):
    """Create a new project"""
    async with DB_POOL.acquire() as conn:
        project_id = await conn.fetchval(
            """INSERT INTO projects (organization_id, created_by, name, description, topic, priority)
               VALUES ($1, $2, $3, $4, $5, $6) RETURNING id""",
            user["organization_id"], user["id"], project_data.name,
            project_data.description, project_data.topic, project_data.priority
        )
        return {"id": project_id, "message": "Project created successfully"}


@APP.post("/api/v1/orchestrate")
async def start_orchestration(
    request: OrchestrationRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    _: bool = Depends(check_rate_limit)
):
    """Start an orchestration run"""
    async with DB_POOL.acquire() as conn:
        # Create orchestration run record
        run_id = await conn.fetchval(
            """INSERT INTO orchestration_runs
               (project_id, user_id, topic, integration_enabled, status)
               VALUES ($1, $2, $3, $4, 'running') RETURNING id""",
            request.project_id, user["id"], request.topic, request.integration_enabled
        )

        # Start background orchestration
        background_tasks.add_task(
            run_orchestration_background,
            run_id, request.topic, request.integration_enabled
        )

        return {
            "run_id": run_id,
            "status": "started",
            "message": "Orchestration started successfully"
        }


@APP.get("/api/v1/orchestration/{run_id}")
async def get_orchestration_status(
    run_id: uuid.UUID,
    user: dict = Depends(get_current_user),
    _: bool = Depends(check_rate_limit)
):
    """Get orchestration run status and results"""
    async with DB_POOL.acquire() as conn:
        run = await conn.fetchrow(
            """SELECT * FROM orchestration_runs
               WHERE id = $1 AND user_id = $2""",
            run_id, user["id"]
        )

        if not run:
            raise HTTPException(
                status_code=404, detail="Orchestration run not found")

        # Get phase executions
        phases = await conn.fetch(
            """SELECT * FROM phase_executions
               WHERE run_id = $1 ORDER BY started_at""",
            run_id
        )

        return {
            "run": dict(run),
            "phases": [dict(phase) for phase in phases]
        }


@APP.get("/api/v1/templates")
async def list_templates(
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    user: dict = Depends(get_current_user),
    _: bool = Depends(check_rate_limit)
):
    """List orchestration templates"""
    async with DB_POOL.acquire() as conn:
        query = """
            SELECT t.*, u.username as created_by_username
            FROM orchestration_templates t
            LEFT JOIN users u ON t.created_by = u.id
            WHERE (t.organization_id = $1 OR t.is_public = true)
        """
        params = [user["organization_id"]]

        if category:
            query += " AND t.category = $2"
            params.append(category)

        if is_public is not None:
            query += f" AND t.is_public = ${len(params) + 1}"
            params.append(is_public)

        query += " ORDER BY t.usage_count DESC, t.created_at DESC"

        templates = await conn.fetch(query, *params)
        return [dict(template) for template in templates]


@APP.post("/api/v1/templates")
async def create_template(
    template_data: TemplateCreate,
    user: dict = Depends(get_current_user),
    _: bool = Depends(check_rate_limit)
):
    """Create a new orchestration template"""
    async with DB_POOL.acquire() as conn:
        template_id = await conn.fetchval(
            """INSERT INTO orchestration_templates
               (organization_id, created_by, name, description, category, template_data, is_public)
               VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id""",
            user["organization_id"], user["id"], template_data.name,
            template_data.description, template_data.category,
            json.dumps(template_data.template_data), template_data.is_public
        )
        return {"id": template_id, "message": "Template created successfully"}


@APP.get("/api/v1/analytics/usage")
async def get_usage_analytics(
    days: int = 30,
    user: dict = Depends(get_current_user),
    _: bool = Depends(check_rate_limit)
):
    """Get usage analytics for the organization"""
    async with DB_POOL.acquire() as conn:
        # API usage over time
        api_usage = await conn.fetch(
            f"""SELECT DATE(created_at) as date, COUNT(*) as requests, SUM(tokens_used) as tokens
               FROM api_usage
               WHERE organization_id = $1 AND created_at >= NOW() - INTERVAL '{days} days'
               GROUP BY DATE(created_at) ORDER BY date""",
            user["organization_id"]
        )

        # Orchestration runs summary
        runs_summary = await conn.fetchrow(
            f"""SELECT
                COUNT(*) as total_runs,
                COUNT(*) FILTER (WHERE status = 'completed') as completed_runs,
                COUNT(*) FILTER (WHERE status = 'failed') as failed_runs,
                AVG(execution_time_ms) as avg_execution_time
               FROM orchestration_runs
               WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '{days} days'""",
            user["id"]
        )

        return {
            "api_usage": [dict(row) for row in api_usage],
            "runs_summary": dict(runs_summary) if runs_summary else {}
        }

# Background Tasks


async def run_orchestration_background(run_id: uuid.UUID, topic: str, integration_enabled: bool):
    """Background task to run orchestration"""
    try:
        # Import orchestrator here to avoid circular imports
        from enhanced_orchestrator import EnhancedOrchestrator
        from config import Config

        config = Config()
        orchestrator = EnhancedOrchestrator(config)
        results = orchestrator.process_topic_enhanced(
            topic, integration_enabled)

        async with DB_POOL.acquire() as conn:
            # Update run status
            await conn.execute(
                """UPDATE orchestration_runs
                   SET status = 'completed', results = $1, completed_at = NOW(),
                       success_rate = $2, completed_phases = $3
                   WHERE id = $4""",
                json.dumps(results),
                float(results['metadata']['success_rate'].rstrip('%')),
                results['metadata']['successful_phases'],
                run_id
            )

            # Save phase executions
            for phase_code, phase_data in results['phases'].items():
                await conn.execute(
                    """INSERT INTO phase_executions
                       (run_id, phase_code, phase_name, status, response_text, completed_at)
                       VALUES ($1, $2, $3, $4, $5, NOW())""",
                    run_id, phase_code, phase_data['phase'],
                    phase_data['status'], phase_data.get('response', '')
                )

    except (IOError, json.JSONDecodeError) as e:
        logger.error("Orchestration failed for run %s: %s", run_id, e)
        async with DB_POOL.acquire() as conn:
            await conn.execute(
                """UPDATE orchestration_runs
                   SET status = 'failed', error_details = $1, completed_at = NOW()
                   WHERE id = $2""",
                json.dumps({"error": str(e)}), run_id
            )


def main():
    """Main function to run the API."""
    import uvicorn
    uvicorn.run(APP, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()