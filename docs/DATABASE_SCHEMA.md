# Database Schema Documentation
# AI Orchestrator Platform

## Overview
This document describes the comprehensive database schema for the AI Orchestrator platform, designed to support enterprise-level multi-tenancy, organizations, and complex business logic.

## Core Tables

### Organizations Table
**Purpose**: Multi-tenant support with subscription management
```sql
organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    api_quota_limit INTEGER DEFAULT 1000,
    api_quota_used INTEGER DEFAULT 0,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE NULL
)
```

**Key Features**:
- Unique slug for organization identification
- Subscription tier management (free, pro, enterprise)
- API quota tracking and limits
- Flexible settings storage via JSONB
- Soft delete support

### Users Table
**Purpose**: User management with role-based access control
```sql
users (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'member',
    permissions JSONB DEFAULT '[]',
    preferences JSONB DEFAULT '{}',
    last_login_at TIMESTAMP WITH TIME ZONE,
    email_verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE NULL
)
```

**Roles**:
- `admin`: Full organization access
- `manager`: Project and team management
- `member`: Standard user access
- `viewer`: Read-only access

### Projects Table
**Purpose**: Project management and organization
```sql
projects (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    created_by UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    topic TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    priority VARCHAR(20) DEFAULT 'medium',
    metadata JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE NULL
)
```

**Status Values**:
- `active`: Currently being worked on
- `completed`: Successfully finished
- `archived`: Stored for reference
- `failed`: Terminated due to errors

**Priority Levels**:
- `low`: Non-urgent tasks
- `medium`: Standard priority
- `high`: Important projects
- `urgent`: Critical/time-sensitive

## Orchestration Tables

### Orchestration Runs
**Purpose**: Track individual orchestration executions
```sql
orchestration_runs (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    user_id UUID REFERENCES users(id),
    topic TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'running',
    total_phases INTEGER DEFAULT 0,
    completed_phases INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.00,
    execution_time_ms INTEGER,
    integration_enabled BOOLEAN DEFAULT FALSE,
    results JSONB DEFAULT '{}',
    error_details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE NULL
)
```

### Phase Executions
**Purpose**: Detailed tracking of individual phase execution
```sql
phase_executions (
    id UUID PRIMARY KEY,
    run_id UUID REFERENCES orchestration_runs(id),
    phase_code VARCHAR(50) NOT NULL,
    phase_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    prompt_text TEXT,
    response_text TEXT,
    execution_time_ms INTEGER,
    token_usage JSONB DEFAULT '{}',
    error_details JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
)
```

### Integration Operations
**Purpose**: Log all system integration operations
```sql
integration_operations (
    id UUID PRIMARY KEY,
    run_id UUID REFERENCES orchestration_runs(id),
    operation_type VARCHAR(100) NOT NULL,
    operation_params JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    result JSONB DEFAULT '{}',
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE NULL
)
```

## Supporting Tables

### API Usage Tracking
**Purpose**: Monitor and bill API usage
```sql
api_usage (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    response_time_ms INTEGER,
    status_code INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
```

### Orchestration Templates
**Purpose**: Reusable orchestration patterns
```sql
orchestration_templates (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    created_by UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    template_data JSONB NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
```

### Webhooks
**Purpose**: External system integrations
```sql
webhooks (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    events TEXT[] DEFAULT '{}',
    secret_key VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
```

### Audit Logs
**Purpose**: Compliance and security tracking
```sql
audit_logs (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    old_values JSONB DEFAULT '{}',
    new_values JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
```

## Security Features

### Row Level Security (RLS)
All tables implement RLS to ensure data isolation between organizations:

```sql
-- Example policy for projects table
CREATE POLICY "Projects are organization-scoped" ON projects
    FOR ALL TO authenticated
    USING (organization_id = (SELECT organization_id FROM users WHERE id = auth.uid()));
```

### Indexes for Performance
Strategic indexes for optimal query performance:

```sql
-- Organization and user indexes
CREATE INDEX idx_organizations_slug ON organizations(slug);
CREATE INDEX idx_users_organization_id ON users(organization_id);
CREATE INDEX idx_users_email ON users(email);

-- Project and orchestration indexes
CREATE INDEX idx_projects_organization_id ON projects(organization_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_orchestration_runs_project_id ON orchestration_runs(project_id);
CREATE INDEX idx_orchestration_runs_status ON orchestration_runs(status);

-- Performance monitoring indexes
CREATE INDEX idx_api_usage_organization_id ON api_usage(organization_id);
CREATE INDEX idx_api_usage_created_at ON api_usage(created_at);
```

## Data Relationships

### Organization Hierarchy
```
Organization (1) -> (N) Users
Organization (1) -> (N) Projects
Organization (1) -> (N) API Usage
Organization (1) -> (N) Templates
Organization (1) -> (N) Webhooks
```

### Project Workflow
```
Project (1) -> (N) Orchestration Runs
Orchestration Run (1) -> (N) Phase Executions
Orchestration Run (1) -> (N) Integration Operations
```

### User Management
```
User (1) -> (N) Projects (created_by)
User (1) -> (N) Orchestration Runs
User (1) -> (N) Templates (created_by)
User (1) -> (N) Audit Logs
```

## JSONB Field Structures

### Organization Settings
```json
{
  "default_ai_model": "gpt-4",
  "integration_enabled": true,
  "notification_preferences": {
    "email": true,
    "slack": false
  },
  "security_settings": {
    "require_2fa": false,
    "session_timeout": 3600
  }
}
```

### User Permissions
```json
[
  "projects.create",
  "projects.edit",
  "orchestrations.run",
  "templates.create",
  "analytics.view"
]
```

### Project Metadata
```json
{
  "estimated_duration": "3 months",
  "complexity": "high",
  "technologies": ["React", "Node.js", "PostgreSQL"],
  "budget": 50000,
  "team_size": 5
}
```

### Orchestration Results
```json
{
  "phases": {
    "Phase 0": {
      "phase": "Ideation",
      "status": "completed",
      "response": "...",
      "execution_time_ms": 5000
    }
  },
  "metadata": {
    "total_phases": 7,
    "successful_phases": 6,
    "success_rate": "85.7%"
  }
}
```

### Token Usage Tracking
```json
{
  "prompt_tokens": 150,
  "completion_tokens": 800,
  "total_tokens": 950,
  "model": "gpt-4",
  "cost_usd": 0.028
}
```

## Migration Strategy

### Version Control
- All schema changes tracked in migration files
- Backward compatibility maintained
- Rollback procedures documented

### Data Migration
- Zero-downtime deployment support
- Data validation and integrity checks
- Performance impact monitoring

### Testing
- Comprehensive test coverage for all tables
- Performance benchmarking
- Security validation

## Monitoring and Maintenance

### Performance Monitoring
- Query performance tracking
- Index usage analysis
- Connection pool monitoring

### Data Retention
- Automated cleanup of old audit logs
- Archive strategy for completed projects
- Backup and recovery procedures

### Security Auditing
- Regular security assessments
- Access pattern analysis
- Compliance reporting

This schema provides a robust foundation for the AI Orchestrator platform, supporting enterprise requirements while maintaining flexibility for future enhancements.