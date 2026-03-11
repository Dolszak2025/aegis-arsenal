# Aegis Arsenal - Phase 2 Database Design

**Version:** 1.0.0  
**Status:** Design Complete - Ready for Implementation  
**Created:** March 11, 2026

---

## Overview

PostgreSQL database schema for Aegis Arsenal Phase 2, supporting Agent management, Workflow orchestration, Task scheduling, and Audit logging.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     AGENTS SYSTEM                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    1:N    ┌──────────────────────┐        │
│  │    agents    ├───────────│ agent_executions      │        │
│  ├──────────────┤           ├──────────────────────┤        │
│  │ id (PK)      │           │ id (PK)              │        │
│  │ name         │           │ agent_id (FK)        │        │
│  │ type         │           │ status               │        │
│  │ config       │           │ input/output         │        │
│  │ status       │           │ duration_ms          │        │
│  │ created_at   │           │ created_at           │        │
│  └──────────────┘           └──────────────────────┘        │
│                                                              │
│  ┌──────────────┐    1:N    ┌──────────────────────┐        │
│  │  workflows   ├───────────│workflow_executions   │        │
│  ├──────────────┤           ├──────────────────────┤        │
│  │ id (PK)      │           │ id (PK)              │        │
│  │ name         │           │ workflow_id (FK)     │        │
│  │ definition   │           │ status               │        │
│  │ status       │           │ execution_log        │        │
│  │ created_at   │           │ created_at           │        │
│  └──────────────┘           └──────────────────────┘        │
│                                                              │
│  ┌──────────────────────┐    1:N    ┌────────────────┐     │
│  │       tasks          ├───────────│  audit_logs    │     │
│  ├──────────────────────┤           ├────────────────┤     │
│  │ id (PK)              │           │ id (PK)        │     │
│  │ name                 │           │ action         │     │
│  │ task_type            │           │ entity_type    │     │
│  │ payload              │           │ entity_id      │     │
│  │ status               │           │ details        │     │
│  │ created_at           │           │ created_at     │     │
│  └──────────────────────┘           └────────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Table Specifications

### agents

**Purpose:** Store agent configurations and metadata

```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('tool', 'model', 'worker')),
    config JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'error')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255)
);

CREATE INDEX idx_agents_name ON agents(name);
CREATE INDEX idx_agents_type ON agents(type);
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_created_at ON agents(created_at);
```

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| id | UUID | PK, Default UUID | Unique agent identifier |
| name | VARCHAR(255) | UNIQUE, NOT NULL | Agent name (must be unique) |
| type | VARCHAR(50) | NOT NULL, CHECK | Type: tool, model, worker |
| config | JSONB | NOT NULL | Agent configuration object |
| status | VARCHAR(50) | NOT NULL, CHECK | Status: active, inactive, error |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |
| created_by | VARCHAR(255) | NULL | Creator identifier |

**Estimated Size:** 1MB per 10,000 agents

---

### agent_executions

**Purpose:** Track agent execution history and metrics

```sql
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    input JSONB,
    output JSONB,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agent_executions_agent_id ON agent_executions(agent_id);
CREATE INDEX idx_agent_executions_status ON agent_executions(status);
CREATE INDEX idx_agent_executions_created_at ON agent_executions(created_at);
CREATE INDEX idx_agent_executions_agent_created ON agent_executions(agent_id, created_at DESC);
```

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| id | UUID | PK | Unique execution identifier |
| agent_id | UUID | FK (agents), NOT NULL | Reference to agent |
| status | VARCHAR(50) | NOT NULL, CHECK | Status: pending, running, completed, failed |
| input | JSONB | NULL | Input parameters for execution |
| output | JSONB | NULL | Execution result |
| error_message | TEXT | NULL | Error details if failed |
| started_at | TIMESTAMP | NULL | Execution start time |
| completed_at | TIMESTAMP | NULL | Execution completion time |
| duration_ms | INTEGER | NULL | Total execution time in milliseconds |
| created_at | TIMESTAMP | NOT NULL | Record creation time |

**Estimated Size:** 10MB per 100,000 executions  
**Retention:** 90 days (configurable)

---

### workflows

**Purpose:** Store workflow definitions and orchestration logic

```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    definition JSONB NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255)
);

CREATE INDEX idx_workflows_name ON workflows(name);
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_created_at ON workflows(created_at);
```

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| id | UUID | PK | Unique workflow identifier |
| name | VARCHAR(255) | NOT NULL | Workflow name |
| definition | JSONB | NOT NULL | Workflow DAG/configuration |
| status | VARCHAR(50) | NOT NULL | Status: draft, active, archived |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |
| created_by | VARCHAR(255) | NULL | Creator identifier |

---

### workflow_executions

**Purpose:** Track workflow execution history

```sql
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    execution_log JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_workflow_executions_workflow_id ON workflow_executions(workflow_id);
CREATE INDEX idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX idx_workflow_executions_created_at ON workflow_executions(created_at);
```

---

### tasks

**Purpose:** Background task/job queue

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    payload JSONB,
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_task_type ON tasks(task_type);
```

---

### audit_logs

**Purpose:** Compliance and security audit trail

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100),
    user_id VARCHAR(100),
    details JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

---

## Data Volume Estimates

### Year 1 Projections

| Table | Daily Records | Monthly | Yearly | Storage |
|-------|---------|---------|--------|---------|
| agents | 10 | 300 | 3.6K | 5 MB |
| agent_executions | 50K | 1.5M | 18M | 5 GB |
| workflows | 5 | 150 | 1.8K | 2 MB |
| workflow_executions | 10K | 300K | 3.6M | 1 GB |
| tasks | 30K | 900K | 10.8M | 3 GB |
| audit_logs | 100K | 3M | 36M | 10 GB |

**Total Year 1:** ~19 GB (with compression)

---

## Query Patterns & Performance

### Common Queries

```sql
-- List active agents
SELECT * FROM agents WHERE status = 'active' ORDER BY created_at DESC;
-- Index: idx_agents_status, idx_agents_created_at

-- Get agent execution history
SELECT * FROM agent_executions 
WHERE agent_id = $1 
ORDER BY created_at DESC 
LIMIT 100;
-- Index: idx_agent_executions_agent_id, idx_agent_executions_created_at

-- Find failed executions in last 24 hours
SELECT * FROM agent_executions 
WHERE status = 'failed' AND created_at > NOW() - INTERVAL '1 day';
-- Index: idx_agent_executions_status, idx_agent_executions_created_at

-- Workflow execution statistics
SELECT workflow_id, status, COUNT(*) as count, AVG(duration_ms) as avg_ms
FROM workflow_executions
GROUP BY workflow_id, status;
```

### Performance Targets

| Query | Target P99 | Optimization |
|-------|-----------|--------------|
| List agents | <50ms | Index on status |
| Get executions | <100ms | Index on agent_id |
| Search tasks | <200ms | Index on task_type |
| Audit query | <500ms | Partitioning by date |

---

## Backup & Recovery Strategy

### Backup Schedule
- **Full Backup:** Daily at 2:00 AM UTC
- **Incremental:** Every 6 hours
- **Retention:** 30 days full backups, 7 days incremental
- **Storage:** AWS S3 with cross-region replication

### Recovery Procedures

**Point-in-Time Recovery (PITR)**
```bash
# Restore to specific timestamp
pg_basebackup -D /var/lib/postgresql/backup
```

**Table-Level Recovery**
```bash
# Restore specific table
pg_restore -t agents backup.dump
```

---

## Security Considerations

### Authentication
- PostgreSQL user with minimal required permissions
- Environment variable storage for credentials
- No hardcoded passwords

### Row-Level Security (RLS)
```sql
-- Example: Users can only see their own data
ALTER TABLE agent_executions ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_executions ON agent_executions
FOR SELECT USING (created_by = current_user_id());
```

### Encryption
- SSL/TLS for all connections
- Native PostgreSQL encryption for sensitive fields
- JSONB fields contain no PII

---

## Migration Strategy

### Phase 1 → Phase 2 Migration

```
Step 1: Create dev database with new schema
Step 2: Test all application code against new schema
Step 3: Create staging database
Step 4: Verify query performance
Step 5: Create production database
Step 6: Run warmup queries
Step 7: Switch application to production database
Step 8: Verify all endpoints working
Step 9: Archive Phase 1 data (if applicable)
```

### Alembic Setup

```bash
# Initialize Alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add agents table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Maintenance Plan

### Regular Tasks

| Task | Frequency | Purpose |
|------|-----------|---------|
| VACUUM | Daily | Remove dead tuples |
| ANALYZE | Daily | Update statistics |
| Reindex | Weekly | Maintain index performance |
| Backup | Daily | Data protection |
| Audit Log Rotation | Monthly | Storage management |

### Monitoring Queries

```sql
-- Database size
SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname))
FROM pg_database;

-- Table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index effectiveness
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Slow queries
SELECT query, calls, mean_exec_time, max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 10;
```

---

## PostgreSQL Configuration (Phase 2)

### Recommended Settings

```ini
# postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### Connection Pooling (PgBouncer)

```ini
# pgbouncer.ini
[databases]
aegis_arsenal = host=localhost port=5432 dbname=aegis_arsenal

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 5
```

---

## Testing Strategy

### Database Unit Tests

```python
# tests/database/test_models.py
def test_agent_creation(db_session):
    agent = Agent(name="test", type="tool", config={})
    db_session.add(agent)
    db_session.commit()
    assert agent.id is not None

def test_agent_execution_cascade_delete(db_session):
    agent = Agent(name="test2", type="model", config={})
    execution = AgentExecution(agent=agent, status="completed")
    db_session.add_all([agent, execution])
    db_session.commit()
    
    db_session.delete(agent)
    db_session.commit()
    
    assert db_session.query(AgentExecution).count() == 0
```

### Migration Testing

```bash
# Test forward migration
pytest tests/database/test_migrations.py::test_001_agents_table

# Test rollback
pytest tests/database/test_migrations.py::test_rollback_001
```

---

## Database Deployment Checklist

- [ ] PostgreSQL 14+ installed
- [ ] Database created with UTF-8 encoding
- [ ] SSL certificates configured
- [ ] Backup strategy implemented
- [ ] Monitoring alerts set up
- [ ] Table partitioning configured (for large tables)
- [ ] Connection pooling configured
- [ ] Slow query log enabled
- [ ] Regular maintenance jobs scheduled
- [ ] Documentation completed

---

**Database Design Status:** ✅ COMPLETE  
**Ready for Implementation:** YES  
**Implementation Target:** Sprint 3 (May 1-15, 2026)
