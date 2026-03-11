# Aegis Arsenal

A scalable FastAPI application with comprehensive Phase 1 foundation and Phase 2 enterprise features including database integration, agent orchestration, and real-time performance monitoring.

## Status

- **Phase 1:** ✅ Complete (Production)
- **Phase 2:** 🟡 In Progress (April - June 2026)

## Features

### Phase 1 (Complete)
- 🚀 **FastAPI Backend**: High-performance Python web framework with Uvicorn
- 📊 **Vercel Speed Insights**: Real-time performance monitoring
- ⚡ **Serverless Deployment**: Ready for Vercel with auto-scaling
- ✅ **Comprehensive Testing**: 29 tests, 100% pass rate
- 📚 **Documentation**: 72+ pages including architecture, compliance, deployment

### Phase 2 (In Progress)
- 🗄️ **PostgreSQL Integration**: Enterprise database with SQLAlchemy ORM
- 🤖 **Agent Module**: AI/ML agent orchestration and execution
- 🔄 **Workflow Engine**: Workflow definition and execution
- 📈 **Monitoring**: Sentry error tracking and APM
- 🔐 **Security**: Audit logging, compliance framework
- 🚀 **Scalable Architecture**: Microservices-ready layered design

## Project Structure

```
aegis-arsenal/
├── main.py                          # Phase 1: FastAPI application
├── app/                             # Phase 2: New modular structure
│   ├── core/                        # Configuration & database
│   ├── models/                      # SQLAlchemy ORM models
│   ├── schemas/                     # Pydantic validation
│   ├── services/                    # Business logic
│   └── routes/                      # API endpoints
├── agents/                          # AI/ML agent tools
├── logos_orchestrator/              # Orchestration engine
├── db/                              # Database utilities
└── tests/                           # Test suite
```

## Quick Start

### For Phase 1 (Existing)

```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Run development server
npm run dev
# or
uvicorn main:app --reload

# Run tests
pytest tests/ -v
```

### For Phase 2 Development

**Read These First:**
1. 📘 [PHASE2_DEVELOPER_GUIDE.md](PHASE2_DEVELOPER_GUIDE.md) - Get started guide
2. 📋 [SPRINT1_TASKS.md](SPRINT1_TASKS.md) - Detailed task breakdown
3. 🗃️ [DATABASE_QUICK_REFERENCE.md](DATABASE_QUICK_REFERENCE.md) - Database patterns

**Setup Phase 2 Environment:**

```bash
# Install Phase 2 dependencies
pip install sqlalchemy psycopg2-binary alembic pydantic-settings redis sentry-sdk

# Setup PostgreSQL (Docker recommended)
docker run --name aegis-db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=aegis_arsenal \
  -p 5432:5432 -d postgres:15

# Create .env file
cp .env.example .env
# Edit .env with your database URL and settings

# Initialize database
python -c "from app.core.database import init_db; init_db()"

# Run Phase 2 tests
pytest tests/api/ -v

# Start development server
uvicorn main:app --reload
```

## API Endpoints

### Phase 1 (Existing)
- `GET /` - Main application page with Speed Insights
- `GET /api/health` - Health check endpoint
- `GET /api/info` - Application information

### Phase 2 (In Progress - Sprint 1)
- `POST /api/agents/` - Create agent
- `GET /api/agents/` - List agents
- `GET /api/agents/{id}` - Get agent details
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent
- `POST /api/agents/{id}/execute` - Start execution
- `GET /api/agents/{id}/executions` - Execution history
- `GET /api/agents/{id}/metrics` - Agent metrics

*Sprint 2-4 will add workflow, task, and additional endpoints.*

## Database

**Phase 2 uses PostgreSQL with 6 core tables:**

| Table | Purpose |
|-------|---------|
| `agents` | AI/ML agent configurations |
| `agent_executions` | Execution history & metrics |
| `workflows` | Workflow definitions |
| `workflow_executions` | Workflow execution history |
| `tasks` | Background job queue |
| `audit_logs` | Compliance & security |

See [DATABASE_DESIGN.md](DATABASE_DESIGN.md) for full schema documentation.

## Documentation

### Strategic
- 📘 [MANIFEST.md](MANIFEST.md) - Project inventory
- 🎯 [BLUEPRINT.md](BLUEPRINT.md) - Architecture & technical design
- 📊 [STRATEGY.md](STRATEGY.md) - Business roadmap  through 2027

### Phase 2
- 🚀 [PHASE2_SPRINT_PLAN.md](PHASE2_SPRINT_PLAN.md) - Sprint 1-4 detailed plan
- 📋 [SPRINT1_TASKS.md](SPRINT1_TASKS.md) - Task breakdown for engineers
- 🗃️ [DATABASE_DESIGN.md](DATABASE_DESIGN.md) - Schema documentation
- 📍 [PHASE2_INITIALIZATION.md](PHASE2_INITIALIZATION.md) - Initialization report
- 📖 [PHASE2_DEVELOPER_GUIDE.md](PHASE2_DEVELOPER_GUIDE.md) - Developer onboarding

### Operations
- 📋 [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment procedures
- ✅ [COMPLIANCE.md](COMPLIANCE.md) - Code standards & quality
- 📊 [STATUS.md](STATUS.md) - Project status report
- 🎮 [QUICKSTART.md](QUICKSTART.md) - Quick start guide

## Development Workflow

### Branch Strategy
```
main (production)
  ↑
develop (staging)
  ↑
feature/your-task (your work)
```

### Before Committing
```bash
# Run tests
pytest tests/ -v --cov

# Check code style
flake8 app/ main.py

# Type checking
mypy app/ main.py --ignore-missing-imports
```

### Create a Feature Branch
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-task-name
# Make changes...
git add .
git commit -m "feat: Describe your change"
git push origin feature/your-task-name
# Create PR on GitHub
```

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Suite
```bash
pytest tests/api/ -v          # API tests
pytest tests/database/ -v     # Database tests
pytest tests/services/ -v     # Service tests
```

### Generate Coverage Report
```bash
pytest tests/ --cov=app --cov=main --cov-report=html
open htmlcov/index.html
```

## Deployment

### Phase 1 - Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel deploy

# Enable Speed Insights in Vercel dashboard
```

### Phase 2 - Infrastructure Setup (TBD)

**Coming in May 2026:**
- Kubernetes deployment
- PostgreSQL managed database
- Redis cache layer
- Sentry monitoring
- Load testing & optimization

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed procedures.

## Performance

**Phase 1 Benchmarks:**
- API response time: < 100ms (P95)
- Test execution: 0.54s (29 tests)
- Speed Insights: Real-time RUM data

**Phase 2 Targets:**
- Agent execution: < 500ms (P95)
- Workflow completion: < 5s (typical)
- Database query: < 100ms (P95)
- Endpoint availability: 99.9% SLA

## Team

### Phase 1 (Complete)
- Architect: @Dolszak2025
- Status: ✅ Production-ready

### Phase 2 (April - June 2026)
- **Required:** 2-3 Backend Engineers
- **Optional:** DevOps (40%), QA Engineer
- Start date: April 1, 2026
- Budget: ~$190K

See [PHASE2_SPRINT_PLAN.md](PHASE2_SPRINT_PLAN.md) for details.

## Getting Help

- 📖 Read [PHASE2_DEVELOPER_GUIDE.md](PHASE2_DEVELOPER_GUIDE.md)
- 🗃️ Check [DATABASE_QUICK_REFERENCE.md](DATABASE_QUICK_REFERENCE.md)
- 📋 Review [SPRINT1_TASKS.md](SPRINT1_TASKS.md)
- 💬 Ask in GitHub Issues or Slack #engineering
- 📞 Contact @Dolszak2025

## License

MIT

---

**Last Updated:** March 11, 2026 | **Phase:** 2 (Planning/Initiation) | **Status:** 🟡 On Track
