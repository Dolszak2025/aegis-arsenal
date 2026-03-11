# Phase 2 Database Quick Reference

**For:** Backend Engineers working with Aegis Arsenal Phase 2  
**Database:** PostgreSQL 15+  
**ORM:** SQLAlchemy 2.0

---

## Database Connection

### Setup

```python
# All database operations use this pattern:
from app.core.database import SessionLocal, get_db
from app.models.database import Agent, AgentExecution
from sqlalchemy.orm import Session

# In FastAPI endpoints (automatic)
@app.get("/agents")
async def list_agents(db: Session = Depends(get_db)):
    return db.query(Agent).all()

# In scripts (manual)
db = SessionLocal()
try:
    agents = db.query(Agent).all()
finally:
    db.close()
```

### Environment Variables

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/aegis_arsenal
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
```

---

## Schema Overview

### 6 Core Tables

```
┌─────────────────┐
│     AGENTS      │ AI/ML agent configurations
├─────────────────┤
│ id (UUID PK)    │
│ name (UNIQUE)   │
│ type (enum)     │ tool | model | worker
│ config (JSONB)  │ Agent-specific settings
│ status (enum)   │ active | inactive | error
│ created_at      │
│ updated_at      │
└─────────────────┘
         │
         ├──────────┐
         │          │
    ┌────▼──────────┴──┐
    │ AGENT_EXECUTIONS │ Execution history & metrics
    ├──────────────────┤
    │ id (UUID PK)     │
    │ agent_id (FK)    │
    │ status (enum)    │ pending | running | completed | failed
    │ input (JSONB)    │ Input parameters
    │ output (JSONB)   │ Execution result
    │ error_message    │ NULL if successful
    │ duration_ms      │ Execution time
    │ created_at       │
    └──────────────────┘

┌──────────────────┐
│   WORKFLOWS      │ Agent orchestration definitions
├──────────────────┤
│ id (UUID PK)     │
│ name             │
│ definition (JSON)│ Workflow DAG/steps
│ status (enum)    │ draft | active | archived
│ created_at       │
└──────────────────┘
         │
         ├──────────────┐
         │              │
    ┌────▼────────────┬─┐
    │WORKFLOW_EXECUTIONS
    ├──────────────────┤
    │ id (UUID PK)     │
    │ workflow_id (FK) │
    │ status (enum)    │ pending | running | completed | failed
    │ execution_log    │ Execution trace
    └──────────────────┘

┌──────────────────┐
│      TASKS       │ Background job queue
├──────────────────┤
│ id (UUID PK)     │
│ name             │
│ task_type        │ agent_exec | workflow | cleanup
│ status (enum)    │ pending | running | completed | failed
│ payload (JSONB)  │ Task parameters
│ result (JSONB)   │ Execution result
│ created_at       │
└──────────────────┘

┌──────────────────┐
│   AUDIT_LOGS     │ Compliance & security
├──────────────────┤
│ id (UUID PK)     │
│ action           │ CREATE | UPDATE | DELETE | EXECUTE
│ entity_type      │ agent | workflow | execution
│ entity_id (FK)   │ Associated entity ID
│ details (JSONB)  │ Change details
│ created_at       │
└──────────────────┘
```

---

## Common Queries

### Agent Queries

```python
from app.models.database import Agent
from app.core.database import SessionLocal

db = SessionLocal()

# 1. Get all active agents
active_agents = db.query(Agent).filter(Agent.status == "active").all()

# 2. Get agent by name
agent = db.query(Agent).filter(Agent.name == "my-agent").first()
if agent:
    print(f"Found: {agent.name} ({agent.type})")

# 3. Count agents by type
from sqlalchemy import func
type_counts = db.query(
    Agent.type,
    func.count(Agent.id).label("count")
).group_by(Agent.type).all()

for agent_type, count in type_counts:
    print(f"{agent_type}: {count}")

# 4. Get agents with most executions
from app.models.database import AgentExecution
agents_with_counts = db.query(
    Agent,
    func.count(AgentExecution.id).label("execution_count")
).outerjoin(AgentExecution).group_by(Agent.id).order_by(
    func.count(AgentExecution.id).desc()
).all()
```

### Execution Queries

```python
from app.models.database import AgentExecution
from sqlalchemy import desc, func
from datetime import datetime, timedelta

db = SessionLocal()

# 1. Get recent executions for agent
agent_id = "123e4567-e89b-12d3-a456-426614174000"
recent = db.query(AgentExecution).filter(
    AgentExecution.agent_id == agent_id
).order_by(desc(AgentExecution.created_at)).limit(10).all()

# 2. Get failed executions
failed = db.query(AgentExecution).filter(
    AgentExecution.status == "failed"
).all()

# 3. Average execution time by agent
avg_times = db.query(
    AgentExecution.agent_id,
    func.avg(AgentExecution.duration_ms).label("avg_duration")
).group_by(AgentExecution.agent_id).all()

# 4. Executions in last 24 hours
from datetime import datetime, timedelta
yesterday = datetime.utcnow() - timedelta(days=1)
recent_24h = db.query(AgentExecution).filter(
    AgentExecution.created_at >= yesterday
).all()

# 5. Success rate calculation
all_executions = db.query(AgentExecution).all()
completed = len([e for e in all_executions if e.status == "completed"])
success_rate = (completed / len(all_executions) * 100) if all_executions else 0
print(f"Success Rate: {success_rate:.1f}%")

# 6. Performance metrics
metrics = db.query(
    func.count(AgentExecution.id).label("total"),
    func.sum(case([
        (AgentExecution.status == "completed", 1)
    ], else_=0)).label("completed"),
    func.avg(AgentExecution.duration_ms).label("avg_duration_ms"),
    func.max(AgentExecution.duration_ms).label("max_duration_ms")
).first()

print(f"Total: {metrics.total}")
print(f"Completed: {metrics.completed}")
print(f"Avg Duration: {metrics.avg_duration_ms}ms")
```

### Workflow Queries

```python
from app.models.database import Workflow, WorkflowExecution

db = SessionLocal()

# 1. Get active workflows
active = db.query(Workflow).filter(Workflow.status == "active").all()

# 2. Get workflow with execution history
workflow = db.query(Workflow).filter(Workflow.name == "my-workflow").first()
if workflow:
    executions = db.query(WorkflowExecution).filter(
        WorkflowExecution.workflow_id == workflow.id
    ).all()
    print(f"{workflow.name}: {len(executions)} executions")

# 3. Workflow success rate
workflow_id = "..."
executions = db.query(WorkflowExecution).filter(
    WorkflowExecution.workflow_id == workflow_id
).all()
success_count = len([e for e in executions if e.status == "completed"])
success_rate = (success_count / len(executions) * 100) if executions else 0
```

### Audit Log Queries

```python
from app.models.database import AuditLog

db = SessionLocal()

# 1. Get all changes to specific agent
agent_id = "..."
changes = db.query(AuditLog).filter(
    AuditLog.entity_id == agent_id,
    AuditLog.entity_type == "agent"
).order_by(desc(AuditLog.created_at)).all()

for change in changes:
    print(f"{change.action}: {change.details}")

# 2. Audit trail for compliance
compliance_logs = db.query(AuditLog).filter(
    AuditLog.action.in_(["DELETE", "UPDATE"])
).order_by(desc(AuditLog.created_at)).all()

# 3. Changes in last 7 days
from datetime import datetime, timedelta
seven_days_ago = datetime.utcnow() - timedelta(days=7)
recent_changes = db.query(AuditLog).filter(
    AuditLog.created_at >= seven_days_ago
).all()
```

### Advanced Queries

```python
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

db = SessionLocal()

# 1. Agents with error status and their recent failed executions
from app.models.database import Agent, AgentExecution

problematic = db.query(Agent).filter(
    Agent.status == "error"
).options(
    joinedload(Agent.executions).joinedload(AgentExecution.agent)
).all()

# 2. Bulk update agent status
db.query(Agent).filter(
    Agent.status == "inactive"
).update({"status": "active"})
db.commit()

# 3. Delete old execution records (older than 30 days)
from datetime import datetime, timedelta
cutoff = datetime.utcnow() - timedelta(days=30)
db.query(AgentExecution).filter(
    AgentExecution.created_at < cutoff
).delete()
db.commit()

# 4. Batch create test data
from app.models.database import Agent

test_agents = [
    Agent(name=f"agent-{i}", type="tool", config={"index": i})
    for i in range(10)
]
db.add_all(test_agents)
db.commit()
```

---

## Indexes & Performance

### Key Indexes

```sql
-- Automatically created by SQLAlchemy

-- agents table
CREATE INDEX idx_agents_name ON agents(name);
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_type ON agents(type);

-- agent_executions table
CREATE INDEX idx_agent_executions_agent_id ON agent_executions(agent_id);
CREATE INDEX idx_agent_executions_status ON agent_executions(status);
CREATE INDEX idx_agent_executions_created_at ON agent_executions(created_at);

-- workflows table
CREATE INDEX idx_workflows_status ON workflows(status);

-- audit_logs table
CREATE INDEX idx_audit_logs_entity_id ON audit_logs(entity_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

### Query Optimization Tips

```python
# ❌ Bad: N+1 query problem
agents = db.query(Agent).all()
for agent in agents:
    # Triggers SELECT for each agent
    count = len(agent.executions)

# ✅ Good: Eager loading
from sqlalchemy.orm import joinedload
agents = db.query(Agent).options(
    joinedload(Agent.executions)
).all()

# ✅ Good: Use count() instead of len()
from sqlalchemy import func
count = db.query(func.count(AgentExecution.id)).filter(
    AgentExecution.agent_id == agent_id
).scalar()

# ✅ Good: Limit results
recent_10 = db.query(AgentExecution).order_by(
    desc(AgentExecution.created_at)
).limit(10).all()

# ✅ Good: Use pagination
page = 0
per_page = 50
skip = page * per_page
limit = per_page
paginated = db.query(Agent).offset(skip).limit(limit).all()
```

---

## Data Modification

### Create

```python
from app.models.database import Agent

db = SessionLocal()

# Single creation
new_agent = Agent(
    name="my-new-agent",
    type="tool",
    config={"setting1": "value1"},
    status="active"
)
db.add(new_agent)
db.commit()
db.refresh(new_agent)
print(f"Created agent with ID: {new_agent.id}")

# Bulk creation
agents = [
    Agent(name=f"agent-{i}", type="tool", config={})
    for i in range(5)
]
db.add_all(agents)
db.commit()
```

### Update

```python
db = SessionLocal()

# Update single record
agent = db.query(Agent).filter(Agent.name == "my-agent").first()
if agent:
    agent.status = "inactive"
    agent.config = {"updated": True}
    db.commit()

# Bulk update
db.query(Agent).filter(
    Agent.status == "error"
).update({"status": "inactive"})
db.commit()
```

### Delete

```python
db = SessionLocal()

# Delete single
agent = db.query(Agent).filter(Agent.name == "my-agent").first()
if agent:
    db.delete(agent)
    db.commit()

# Delete cascade (related records auto-deleted)
# When agent is deleted, all related agent_executions are deleted too

# Bulk delete
db.query(Agent).filter(
    Agent.status == "error"
).delete()
db.commit()
```

---

## Transactions & Error Handling

### Basic Transaction Pattern

```python
from app.core.database import SessionLocal
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

db = SessionLocal()

try:
    # Multiple operations in transaction
    agent = Agent(name="new-agent", type="tool", config={})
    db.add(agent)
    
    execution = AgentExecution(
        agent_id=agent.id,
        status="pending",
        input={"data": "test"}
    )
    db.add(execution)
    
    db.commit()  # All-or-nothing
    db.refresh(agent)
    print(f"Success: {agent.id}")
    
except IntegrityError as e:
    # Duplicate key, unique constraint violated
    db.rollback()
    print(f"Integrity error: {e}")
    
except SQLAlchemyError as e:
    # Other database errors
    db.rollback()
    print(f"Database error: {e}")
    
finally:
    db.close()
```

### Using Context Manager (Recommended)

```python
from contextlib import contextmanager

@contextmanager
def get_db_context():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# Usage
with get_db_context() as db:
    agent = Agent(name="test", type="tool", config={})
    db.add(agent)
    # Auto-commits on success, auto-rollsback on error
```

---

## Monitoring & Debugging

### Check Database Status

```python
import psycopg2

conn = psycopg2.connect(
    dbname="aegis_arsenal",
    user="user",
    password="password",
    host="localhost"
)

cur = conn.cursor()

# 1. Check table sizes
cur.execute("""
    SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
    FROM pg_tables WHERE schemaname != 'pg_catalog'
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
""")

for row in cur.fetchall():
    print(f"{row[0]}.{row[1]}: {row[2]}")

# 2. Check active connections
cur.execute("""
    SELECT client_addr, usename, state, count(*) as connection_count
    FROM pg_stat_activity
    GROUP BY client_addr, usename, state;
""")

# 3. Check slow queries (requires logging enabled)
cur.execute("""
    SELECT query, calls, mean_exec_time
    FROM pg_stat_statements
    ORDER BY mean_exec_time DESC
    LIMIT 10;
""")

conn.close()
```

### Database Statistics

```python
from sqlalchemy import text
from app.core.database import SessionLocal

db = SessionLocal()

# 1. Row counts
for table in ["agents", "agent_executions", "workflows", "tasks", "audit_logs"]:
    count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
    print(f"{table}: {count} rows")

# 2. Storage usage
result = db.execute(text("""
    SELECT 
      schemaname,
      tablename,
      pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
    FROM pg_tables 
    WHERE schemaname = 'public'
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
""")).fetchall()

for schema, table, size in result:
    print(f"{table}: {size}")

db.close()
```

---

## Migration Guide

### Adding a New Column

```bash
# 1. Modify SQLAlchemy model
# In app/models/database.py, add to Agent class:
# new_field = Column(String(255), nullable=True)

# 2. Create migration
alembic revision --autogenerate -m "Add new_field to agents"

# 3. Review migration in migrations/versions/
# 4. Apply migration
alembic upgrade head
```

### Adding a New Table

```bash
# 1. Create new model class in app/models/database.py
# 2. Create migration
alembic revision --autogenerate -m "Create new_table"

# 3. Apply
alembic upgrade head
```

### Rollback Changes

```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <version_hash>

# Rollback to beginning
alembic downgrade base
```

---

## Best Practices

✅ **DO**
- [ ] Use SessionLocal() in scripts, Depends(get_db) in FastAPI
- [ ] Always commit() or rollback() transactions
- [ ] Use type hints in functions
- [ ] Close database connections in finally block
- [ ] Use eager loading for related objects
- [ ] Use pagination for large queries
- [ ] Log database operations
- [ ] Index frequently filtered columns

❌ **DON'T**
- [ ] Don't create N+1 queries (load related objects upfront)
- [ ] Don't leave connections open
- [ ] Don't ignore exceptions
- [ ] Don't use string concatenation for queries (use parameters)
- [ ] Don't commit in loops (batch operations)
- [ ] Don't load entire tables into memory
- [ ] Don't modify objects after commit without refresh

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "psycopg2.OperationalError: could not connect" | Check PostgreSQL is running and credentials are correct |
| "IntegrityError: duplicate key" | Check uniqueness constraints, use filter().first() to find existing |
| "AttributeError: object has no attribute" | Refresh object after commit: `db.refresh(obj)` |
| "Slow queries" | Add indexes, use joinedload(), limit results |
| "Transaction deadlock" | Reduce scope, order updates consistently, reduce transaction time |
| "Connection pool exhausted" | Increase POOL_SIZE or are connections not being closed? |

---

## Quick Reference

```python
# Import standard pattern
from app.core.database import SessionLocal
from app.models.database import Agent, AgentExecution
from sqlalchemy import desc, func

# Session lifecycle
db = SessionLocal()
try:
    # Query
    agents = db.query(Agent).all()
    
    # Modify
    agent = agents[0]
    agent.status = "inactive"
    
    # Commit
    db.commit()
finally:
    db.close()

# FastAPI pattern
from fastapi import Depends
from app.core.database import get_db

@app.get("/agents")
async def list_agents(db: Session = Depends(get_db)):
    return db.query(Agent).all()
```

**For more help, see [PHASE2_DEVELOPER_GUIDE.md](PHASE2_DEVELOPER_GUIDE.md)**
