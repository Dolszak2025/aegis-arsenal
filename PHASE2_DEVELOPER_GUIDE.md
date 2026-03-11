# Phase 2 Developer Guide

**For:** Backend Engineers joining Aegis Arsenal Phase 2  
**Date:** March 11, 2026  
**Duration:** April 1 - June 30, 2026

---

## Quick Start for New Team Members

### 1. Environment Setup (Day 1)

```bash
# Clone repository
git clone https://github.com/Dolszak2025/aegis-arsenal.git
cd aegis-arsenal

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL (Docker recommended)
docker run --name aegis-db -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=aegis_arsenal -p 5432:5432 -d postgres:15

# Initialize database
python -c "from app.core.database import init_db; init_db()"

# Run tests to verify setup
pytest tests/ -v
```

### 2. Project Structure Overview

```
aegis-arsenal/
├── main.py                   # Phase 1: REST API core
├── app/                      # Phase 2: New application code
│   ├── core/
│   │   ├── config.py        # Settings & environment
│   │   └── database.py      # Database setup & sessions
│   ├── models/
│   │   └── database.py      # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── agents.py        # Pydantic request/response schemas
│   ├── services/            # Business logic (TBD by team)
│   └── repositories/        # Data access layer (TBD by team)
│
├── tests/
│   ├── test_main.py         # Phase 1 tests (passing)
│   ├── database/            # Database tests (TBD)
│   └── api/                 # API integration tests (TBD)
│
├── migrations/              # Alembic database migrations
├── PHASE2_SPRINT_PLAN.md    # 4-sprint roadmap
├── DATABASE_DESIGN.md       # Schema documentation
└── requirements.txt         # Updated with Phase 2 dependencies
```

### 3. Key Documents to Read

| Document | Purpose | Priority |
|----------|---------|----------|
| [PHASE2_SPRINT_PLAN.md](PHASE2_SPRINT_PLAN.md) | Sprint breakdown & tasks | 🔴 Critical |
| [DATABASE_DESIGN.md](DATABASE_DESIGN.md) | Schema & queries | 🔴 Critical |
| [PHASE2_INITIALIZATION.md](PHASE2_INITIALIZATION.md) | Phase 2 kickoff info | 🟡 Important |
| [BLUEPRINT.md](BLUEPRINT.md) | Architecture overview | 🟡 Important |
| [COMPLIANCE.md](COMPLIANCE.md) | Code standards & quality | 🟡 Important |

---

## Development Workflow

### Branch Strategy

```
main (production)
  ↑
develop (staging)
  ↑
feature/agent-integration (your work)
```

### Creating a Feature Branch

```bash
# Get latest code
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-task-name

# Make changes, test, commit
git add .
git commit -m "feat: Your descriptive message"

# Push and create PR
git push origin feature/your-task-name
# Then create PR on GitHub
```

### Pull Request Checklist

Before submitting PR:
- [ ] Tests written and passing
- [ ] Code reviewed locally
- [ ] No console errors or warnings
- [ ] Documentation updated
- [ ] Commit messages are descriptive

```bash
# Run all checks before committing
pytest tests/ -v --cov
flake8 app/ main.py
mypy app/ main.py --ignore-missing-imports
```

---

## Working with the Database

### Understanding the Models

```python
# app/models/database.py contains:
# - Agent: AI/ML agent configurations
# - AgentExecution: Execution history & metrics
# - Workflow: Workflow definitions
# - WorkflowExecution: Workflow run history
# - Task: Background jobs
# - AuditLog: Compliance & security logs

from app.models.database import Agent, AgentExecution
from app.core.database import SessionLocal

# Example: Query agents
db = SessionLocal()
agents = db.query(Agent).filter(Agent.status == "active").all()
for agent in agents:
    print(f"Agent: {agent.name} ({agent.type})")
```

### Running Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new table"

# Review generated migration in migrations/versions/

# Apply migration
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Check migration status
alembic current
```

### Database Queries

```python
# Pattern: Use repositories for data access
from app.repositories.agent_repository import AgentRepository
from app.core.database import get_db

def get_agents():
    db = next(get_db())
    repo = AgentRepository(db)
    return repo.list_active()
```

---

## API Endpoint Implementation (Sprint 1 Example)

### Creating an Agent Endpoint

```python
# app/routes/agents.py (to be created)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import Agent
from app.schemas.agents import AgentCreate, AgentResponse

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.get("/", response_model=list[AgentResponse])
async def list_agents(db: Session = Depends(get_db)):
    """List all agents"""
    agents = db.query(Agent).all()
    return agents

@router.post("/", response_model=AgentResponse)
async def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    """Create new agent"""
    db_agent = Agent(**agent.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get agent by ID"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent
```

### Testing the Endpoint

```python
# tests/api/test_agents.py

def test_create_agent(client):
    response = client.post("/api/agents", json={
        "name": "test-agent",
        "type": "tool",
        "config": {"key": "value"}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-agent"
```

---

## Configuration & Environment

### Phase 2 Environment Variables

Create `.env` file (or `.env.local` for overrides):

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/aegis_arsenal
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Application
ENVIRONMENT=development
DEBUG=True
APP_HOST=0.0.0.0
APP_PORT=8000

# JWT (Sprint 4)
JWT_SECRET_KEY=your-secret-key-change-in-production

# Monitoring (Sprint 4)
SENTRY_DSN=https://...@sentry.io/...

# Features
ENABLE_SWAGGER=True
ENABLE_SPEED_INSIGHTS=True
```

### Settings Usage in Code

```python
from app.core.config import settings

# Access settings
debug_mode = settings.DEBUG
db_url = settings.DATABASE_URL
api_version = settings.API_VERSION

# In FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)
```

---

## Testing Strategy for Phase 2

### Test Structure

```
tests/
├── test_main.py          # Phase 1 tests (existing)
├── database/
│   ├── test_models.py    # Model tests
│   ├── test_migrations.py # Migration tests
│   └── test_queries.py   # Query optimization tests
├── api/
│   ├── test_agents.py    # Agent endpoint tests
│   ├── test_workflows.py # Workflow endpoint tests
│   └── test_tasks.py     # Task endpoint tests
└── integration/
    └── test_e2e.py       # End-to-end workflow tests
```

### Writing Tests

```python
import pytest
from starlette.testclient import TestClient
from main import app
from app.core.database import SessionLocal

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db():
    db = SessionLocal()
    yield db
    db.close()

def test_agent_creation(db):
    """Test agent model creation"""
    from app.models.database import Agent
    
    agent = Agent(
        name="test",
        type="tool",
        config={"test": True}
    )
    db.add(agent)
    db.commit()
    
    fetched = db.query(Agent).filter_by(name="test").first()
    assert fetched.id is not None
    assert fetched.type == "tool"
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Focus on database tests
pytest tests/database/ -v

# With coverage
pytest tests/ --cov=app --cov=main --cov-report=html

# Watch mode (auto-rerun on changes)
pytest-watch tests/ -- -v
```

---

## Code Standards & Best Practices

### Python Style Guide

```python
# Good ✅
class AgentService:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def create_agent(self, agent_data: AgentCreate) -> Agent:
        """Create a new agent with validation."""
        agent = Agent(**agent_data.dict())
        self.db.add(agent)
        self.db.commit()
        return agent

# Bad ❌
def agent_create(db, a):
    agent = Agent(name=a["name"], type=a["type"])
    db.add(agent)
    db.commit()
    return agent
```

### Type Hints (Required)

```python
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.database import Agent

# Always include type hints
def get_agents(db: Session, status: Optional[str] = None) -> List[Agent]:
    """Get agents by status."""
    query = db.query(Agent)
    if status:
        query = query.filter(Agent.status == status)
    return query.all()
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Debug info for development")
logger.info("Important operational info")
logger.warning("Warning about potential issues")
logger.error("Error occurred", exc_info=True)
```

### Error Handling

```python
from fastapi import HTTPException, status

try:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent
except Exception as e:
    logger.error(f"Failed to fetch agent: {str(e)}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error"
    )
```

### Async/Await Pattern

```python
# FastAPI supports both sync and async
# Prefer async for I/O operations

@app.get("/api/agents")
async def list_agents(db: Session = Depends(get_db)):
    """Async endpoint for listing agents"""
    # DB calls automatically run in thread pool
    agents = db.query(Agent).all()
    return agents
```

---

## Sprint Milestones

### Sprint 1 (Apr 1-15): Agents Module
**Goal:** Expose agents/ module via REST API

- [ ] AgentService created with business logic
- [ ] 7 agent endpoints implemented
- [ ] Integration with agents/base_tool.py
- [ ] Database tests passing
- [ ] API contract tests passing

**Deliverables:**
- `app/services/agent_service.py`
- `app/routes/agents.py`
- `tests/api/test_agents.py`
- Updated documentation

### Sprint 2 (Apr 16-30): Orchestrator
**Goal:** Integrate logos_orchestrator/ as middleware

- [ ] Middleware layer created
- [ ] Service orchestration working
- [ ] Metrics collection active
- [ ] Workflow endpoints implemented
- [ ] Integration tests passing

### Sprint 3 (May 1-15): Database
**Goal:** Full database layer implementation

- [ ] PostgreSQL setup complete
- [ ] All migrations running
- [ ] Repository pattern implemented
- [ ] Query optimization done
- [ ] Backup/recovery tested

### Sprint 4 (May 16-31): Expansion
**Goal:** Additional features & optimization

- [ ] 15+ endpoints total
- [ ] Load testing passed
- [ ] Security audit completed
- [ ] Documentation finalized
- [ ] Performance targets met

---

## Debugging & Troubleshooting

### Common Issues

**Issue: Database Connection Failed**
```bash
# Check PostgreSQL is running
docker ps | grep aegis-db

# Check connection string
echo $DATABASE_URL

# Verify credentials
psql -U user -h localhost -d aegis_arsenal
```

**Issue: Tests Failing**
```bash
# Clear cache and dependencies
rm -rf .pytest_cache __pycache__
pip install --force-reinstall -r requirements.txt

# Run single test
pytest tests/test_main.py::test_name -v

# Debug with print statements
pytest tests/test_name.py -v -s
```

**Issue: Models Not Syncing with Database**
```bash
# Check SQLAlchemy models
python -c "from app.models.database import Base; print(Base.metadata.tables.keys())"

# Create migration
alembic revision --autogenerate -m "Fix schema"

# Apply migration
alembic upgrade head
```

### Debugging Commands

```python
# Interactive shell with app context
python -c "
from app.core.database import SessionLocal
from app.models.database import Agent

db = SessionLocal()
agents = db.query(Agent).all()
print(f'Total agents: {len(agents)}')
"

# Check database directly
psql -U user -d aegis_arsenal -c "SELECT * FROM agents;"
```

---

## Performance Monitoring

### Query Performance

```python
# Enable SQL logging
from app.core.config import settings
# Set DATABASE_ECHO=True in .env

# Analyze slow queries
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - conn.info['query_start_time'].pop(-1)
    if total_time > 0.1:  # Log queries > 100ms
        print(f"SLOW QUERY ({total_time:.2f}s): {statement[:100]}")
```

### Request Timing

```python
import time
from fastapi import Request

@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    if process_time > 1.0:
        print(f"SLOW REQUEST ({process_time:.2f}s): {request.url.path}")
    return response
```

---

## Getting Help

### Resources
- 📚 [FastAPI Documentation](https://fastapi.tiangolo.com/)
- 🐘 [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/)
- 🗃️ [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- 🚀 [Pydantic Docs](https://docs.pydantic.dev/)

### Team Communication
- **Daily Standup:** 10:00 AM UTC (Slack)
- **Code Review:** GitHub PR reviews
- **Weekly Sync:** Fridays 2:00 PM UTC
- **Escalation:** Tag @Dolszak2025

---

## Phase 2 Success Criteria

When you complete your tasks:
- ✅ Code compiles without errors
- ✅ All tests pass (local + CI)
- ✅ Documentation is updated
- ✅ Code review approved
- ✅ Performance targets met
- ✅ Security scan passed

---

**Welcome to Phase 2! You've got this! 🚀**

Questions? Ask in #engineering or create an issue in GitHub.
