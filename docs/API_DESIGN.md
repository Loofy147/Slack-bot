# API Design Document
# AI Orchestrator Platform

## 1. API Overview

### 1.1 Design Principles
- **RESTful Design**: Following REST architectural principles
- **Consistency**: Uniform naming conventions and response formats
- **Versioning**: API versioning for backward compatibility
- **Security**: Authentication and authorization for all endpoints
- **Performance**: Optimized for speed and scalability
- **Documentation**: Comprehensive OpenAPI specifications

### 1.2 Base URL Structure
```
Production: https://api.orchestrator.ai/v1
Staging: https://staging-api.orchestrator.ai/v1
Development: https://dev-api.orchestrator.ai/v1
```

### 1.3 Authentication
- **Method**: JWT Bearer tokens
- **Header**: `Authorization: Bearer <token>`
- **Refresh**: Automatic token refresh mechanism
- **Expiration**: 24-hour token lifetime

## 2. Core API Endpoints

### 2.1 Authentication & Authorization

#### POST /auth/login
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "organization_id": "uuid",
    "role": "admin"
  }
}
```

#### POST /auth/refresh
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### POST /auth/logout
```json
{
  "message": "Successfully logged out"
}
```

### 2.2 Organizations

#### GET /organizations/current
**Response:**
```json
{
  "id": "uuid",
  "name": "Acme Corporation",
  "slug": "acme-corp",
  "subscription_tier": "enterprise",
  "api_quota_limit": 10000,
  "api_quota_used": 2500,
  "settings": {
    "default_ai_model": "gpt-4",
    "integration_enabled": true
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### PUT /organizations/current
```json
{
  "name": "Updated Organization Name",
  "settings": {
    "default_ai_model": "gpt-4-turbo",
    "integration_enabled": false
  }
}
```

### 2.3 Projects

#### GET /projects
**Query Parameters:**
- `status`: Filter by status (active, completed, archived, failed)
- `priority`: Filter by priority (low, medium, high, urgent)
- `limit`: Number of results (default: 50, max: 100)
- `offset`: Pagination offset (default: 0)
- `search`: Search in name and description

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "E-commerce Platform",
      "description": "Modern e-commerce solution with AI features",
      "topic": "Build a scalable e-commerce platform with AI recommendations",
      "status": "active",
      "priority": "high",
      "created_by": {
        "id": "uuid",
        "username": "john_doe",
        "full_name": "John Doe"
      },
      "metadata": {
        "estimated_duration": "3 months",
        "complexity": "high",
        "technologies": ["React", "Node.js", "PostgreSQL"]
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "total": 150,
    "limit": 50,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  }
}
```

#### POST /projects
```json
{
  "name": "New Project",
  "description": "Project description",
  "topic": "Detailed project topic for AI processing",
  "priority": "medium",
  "metadata": {
    "estimated_duration": "2 months",
    "budget": 50000,
    "team_size": 5
  }
}
```

#### GET /projects/{project_id}
**Response:**
```json
{
  "id": "uuid",
  "name": "E-commerce Platform",
  "description": "Modern e-commerce solution",
  "topic": "Build a scalable e-commerce platform",
  "status": "active",
  "priority": "high",
  "created_by": {
    "id": "uuid",
    "username": "john_doe",
    "full_name": "John Doe"
  },
  "orchestration_runs": [
    {
      "id": "uuid",
      "status": "completed",
      "success_rate": 95.5,
      "created_at": "2024-01-10T09:00:00Z"
    }
  ],
  "metadata": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### PUT /projects/{project_id}
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "priority": "high",
  "status": "active"
}
```

#### DELETE /projects/{project_id}
**Response:**
```json
{
  "message": "Project deleted successfully"
}
```

### 2.4 Orchestration

#### POST /orchestrate
```json
{
  "project_id": "uuid",
  "topic": "Create a REST API for user management",
  "integration_enabled": true,
  "custom_phases": ["ideation", "design", "implementation"],
  "template_id": "uuid",
  "settings": {
    "ai_model": "gpt-4",
    "max_tokens": 2000,
    "temperature": 0.7
  }
}
```

**Response:**
```json
{
  "run_id": "uuid",
  "status": "started",
  "message": "Orchestration started successfully",
  "estimated_completion": "2024-01-15T11:30:00Z",
  "phases": [
    {
      "code": "Phase 0",
      "name": "Ideation",
      "status": "pending",
      "estimated_duration": "5 minutes"
    }
  ]
}
```

#### GET /orchestration/{run_id}
**Response:**
```json
{
  "run": {
    "id": "uuid",
    "project_id": "uuid",
    "topic": "Create a REST API for user management",
    "status": "running",
    "total_phases": 7,
    "completed_phases": 3,
    "success_rate": 85.7,
    "integration_enabled": true,
    "execution_time_ms": 45000,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:45:00Z"
  },
  "phases": [
    {
      "id": "uuid",
      "phase_code": "Phase 0",
      "phase_name": "Ideation",
      "status": "completed",
      "response_text": "Detailed ideation response...",
      "execution_time_ms": 5000,
      "token_usage": {
        "prompt_tokens": 150,
        "completion_tokens": 800,
        "total_tokens": 950
      },
      "started_at": "2024-01-15T10:00:00Z",
      "completed_at": "2024-01-15T10:05:00Z"
    }
  ],
  "integration_operations": [
    {
      "id": "uuid",
      "operation_type": "file_system",
      "status": "completed",
      "result": {
        "success": true,
        "message": "File created successfully"
      },
      "execution_time_ms": 100
    }
  ]
}
```

#### GET /orchestration
**Query Parameters:**
- `project_id`: Filter by project
- `status`: Filter by status
- `limit`: Number of results
- `offset`: Pagination offset

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "project": {
        "id": "uuid",
        "name": "E-commerce Platform"
      },
      "topic": "Create user authentication system",
      "status": "completed",
      "success_rate": 95.5,
      "execution_time_ms": 120000,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "pagination": {
    "total": 25,
    "limit": 10,
    "offset": 0
  }
}
```

#### POST /orchestration/{run_id}/cancel
**Response:**
```json
{
  "message": "Orchestration cancelled successfully",
  "run_id": "uuid",
  "status": "cancelled"
}
```

### 2.5 Templates

#### GET /templates
**Query Parameters:**
- `category`: Filter by category
- `is_public`: Filter public/private templates
- `search`: Search in name and description

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Web Application Starter",
      "description": "Template for creating modern web applications",
      "category": "web-development",
      "is_public": true,
      "usage_count": 150,
      "created_by": {
        "username": "template_creator",
        "full_name": "Template Creator"
      },
      "template_data": {
        "phases": ["ideation", "design", "development"],
        "integrations": ["git", "deployment"],
        "settings": {}
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### POST /templates
```json
{
  "name": "Custom Template",
  "description": "My custom orchestration template",
  "category": "custom",
  "is_public": false,
  "template_data": {
    "phases": ["research", "design", "implementation", "testing"],
    "integrations": ["github", "docker"],
    "settings": {
      "ai_model": "gpt-4",
      "integration_enabled": true
    }
  }
}
```

#### GET /templates/{template_id}
**Response:**
```json
{
  "id": "uuid",
  "name": "Web Application Starter",
  "description": "Template for creating modern web applications",
  "category": "web-development",
  "is_public": true,
  "usage_count": 150,
  "template_data": {
    "phases": ["ideation", "design", "development"],
    "integrations": ["git", "deployment"],
    "settings": {}
  },
  "created_by": {
    "username": "template_creator",
    "full_name": "Template Creator"
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-10T15:30:00Z"
}
```

### 2.6 Analytics

#### GET /analytics/usage
**Query Parameters:**
- `days`: Number of days to analyze (default: 30)
- `granularity`: Data granularity (hour, day, week, month)

**Response:**
```json
{
  "api_usage": [
    {
      "date": "2024-01-15",
      "requests": 1250,
      "tokens": 45000,
      "avg_response_time": 180
    }
  ],
  "runs_summary": {
    "total_runs": 45,
    "completed_runs": 38,
    "failed_runs": 7,
    "avg_execution_time": 85000,
    "success_rate": 84.4
  },
  "top_projects": [
    {
      "project_id": "uuid",
      "project_name": "E-commerce Platform",
      "run_count": 12,
      "success_rate": 91.7
    }
  ],
  "integration_usage": {
    "file_system": 150,
    "git_operations": 89,
    "deployment": 45
  }
}
```

#### GET /analytics/performance
**Response:**
```json
{
  "response_times": {
    "p50": 120,
    "p95": 450,
    "p99": 800
  },
  "error_rates": {
    "4xx": 2.1,
    "5xx": 0.3
  },
  "throughput": {
    "requests_per_second": 25.5,
    "peak_rps": 150
  },
  "resource_usage": {
    "cpu_utilization": 45.2,
    "memory_usage": 68.7,
    "disk_usage": 23.1
  }
}
```

### 2.7 Webhooks

#### GET /webhooks
**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Slack Notifications",
      "url": "https://hooks.slack.com/services/...",
      "events": ["orchestration.completed", "orchestration.failed"],
      "is_active": true,
      "last_triggered_at": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### POST /webhooks
```json
{
  "name": "Custom Webhook",
  "url": "https://api.example.com/webhook",
  "events": ["orchestration.started", "orchestration.completed"],
  "secret_key": "optional_secret_for_verification"
}
```

#### PUT /webhooks/{webhook_id}
```json
{
  "name": "Updated Webhook",
  "url": "https://api.example.com/new-webhook",
  "events": ["orchestration.completed"],
  "is_active": false
}
```

## 3. Error Handling

### 3.1 Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "request_id": "uuid",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### 3.2 HTTP Status Codes
- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **409**: Conflict
- **422**: Unprocessable Entity
- **429**: Too Many Requests
- **500**: Internal Server Error
- **503**: Service Unavailable

### 3.3 Error Codes
- `VALIDATION_ERROR`: Request validation failed
- `AUTHENTICATION_REQUIRED`: Authentication token required
- `INSUFFICIENT_PERMISSIONS`: User lacks required permissions
- `RESOURCE_NOT_FOUND`: Requested resource not found
- `RATE_LIMIT_EXCEEDED`: API rate limit exceeded
- `QUOTA_EXCEEDED`: Organization quota exceeded
- `INTEGRATION_ERROR`: System integration failure
- `AI_SERVICE_ERROR`: AI service unavailable

## 4. Rate Limiting

### 4.1 Rate Limit Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
X-RateLimit-Window: 3600
```

### 4.2 Rate Limit Tiers
- **Free**: 100 requests/hour
- **Pro**: 1,000 requests/hour
- **Enterprise**: 10,000 requests/hour
- **Custom**: Negotiated limits

## 5. Pagination

### 5.1 Request Parameters
- `limit`: Number of items per page (max: 100)
- `offset`: Number of items to skip
- `cursor`: Cursor-based pagination token

### 5.2 Response Format
```json
{
  "data": [...],
  "pagination": {
    "total": 1500,
    "limit": 50,
    "offset": 100,
    "has_next": true,
    "has_prev": true,
    "next_cursor": "eyJpZCI6IjEyMyJ9",
    "prev_cursor": "eyJpZCI6IjQ1NiJ9"
  }
}
```

## 6. Filtering and Sorting

### 6.1 Filtering
- **Exact match**: `?status=active`
- **Multiple values**: `?status=active,completed`
- **Date ranges**: `?created_after=2024-01-01&created_before=2024-01-31`
- **Text search**: `?search=keyword`

### 6.2 Sorting
- **Single field**: `?sort=created_at`
- **Multiple fields**: `?sort=priority,-created_at`
- **Direction**: `+` (ascending), `-` (descending)

## 7. Versioning

### 7.1 URL Versioning
- Current version: `/v1/`
- Future versions: `/v2/`, `/v3/`

### 7.2 Deprecation Policy
- **Notice Period**: 6 months minimum
- **Support Period**: 12 months after deprecation
- **Migration Guide**: Provided for breaking changes

## 8. Security

### 8.1 Authentication
- **JWT Tokens**: Stateless authentication
- **Token Rotation**: Automatic refresh mechanism
- **Multi-Factor**: Optional MFA support

### 8.2 Authorization
- **Role-Based**: Admin, Manager, Member, Viewer
- **Resource-Based**: Project and organization scoping
- **Permission Checks**: Granular permission validation

### 8.3 Data Protection
- **HTTPS Only**: All communications encrypted
- **Input Validation**: Comprehensive request validation
- **SQL Injection**: Parameterized queries
- **XSS Protection**: Output encoding and CSP headers