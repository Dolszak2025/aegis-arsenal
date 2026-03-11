# Aegis Arsenal - Technical Blueprint

**Architecture Document v1.0**  
**Created:** March 11, 2026  
**Framework:** FastAPI + Vercel

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    VERCEL DEPLOYMENT                    │
├───────────┬───────────────────────────────────────────┤
│           │     Speed Insights (Real-time monitoring) │
│           └───────────────────────────────────────────┘
│
├─────────────────────────────────────────────────────────┐
│                   FASTAPI APPLICATION                   │
├──────────────────┬──────────────────────────────────────┤
│  Static Routes   │     REST API Layer                  │
│  • /             │     • /api/health                  │
│  • /static/*     │     • /api/info                    │
│                  │     • /api/* (future expansion)    │
├──────────────────┴──────────────────────────────────────┤
│         Middleware Layer (To be implemented)            │
│  • Authentication                                       │
│  • Rate Limiting                                        │
│  • Error Handling                                       │
│  • CORS Management                                      │
├──────────────────────────────────────────────────────────┤
│           Service Layer (Integration Pending)            │
│  • agents/ - AI/ML tools                               │
│  • logos_orchestrator/ - Orchestration                 │
│  • db/ - Data persistence                              │
│  • scripts/ - Utility functions                        │
├──────────────────────────────────────────────────────────┤
│          External Services (Future)                      │
│  • Database (PostgreSQL/MongoDB)                       │
│  • Cache (Redis)                                        │
│  • Message Queue (RabbitMQ/Kafka)                      │
└──────────────────────────────────────────────────────────┘
```

## Application Flow

### Request Lifecycle

```
1. INCOMING REQUEST
   ↓
2. MIDDLEWARE CHAIN
   ├─ Authentication
   ├─ Request Validation
   └─ Rate Limiting
   ↓
3. ROUTER DISPATCH
   ├─ GET /           → read_root()
   ├─ GET /api/health → health_check()
   └─ GET /api/info   → info()
   ↓
4. HANDLER EXECUTION
   ├─ Business Logic
   ├─ Service Integration
   └─ Data Processing
   ↓
5. RESPONSE GENERATION
   ├─ JSON Serialization
   └─ Status Code
   ↓
6. SPEED INSIGHTS TRACKING
   └─ Client-side metric collection
   ↓
7. CLIENT RECEIVES RESPONSE
```

## Module Integration Architecture

### Phase 1: Current
```
main.py (FastAPI core)
├── Routes: /, /api/health, /api/info
└── Static files: /static
```

### Phase 2: Integration (Next Sprint)
```
main.py
├── agents/
│   └── /api/agents/* endpoints
├── logos_orchestrator/
│   └── Service middleware layer
├── db/
│   └── Database connection pool
└── scripts/
    └── /api/tasks/* endpoints
```

## Data Flow

### Primary Request Path

```
Client Browser
    ↓
GET /
    ↓
FastAPI read_root()
    ↓
Generate HTML with Speed Insights script
    ↓
Return HTMLResponse
    ↓
Browser renders page
    ↓
Speed Insights script loads async
    ↓
Real-time metrics collection
```

### Health Check Path

```
Monitoring System
    ↓
GET /api/health
    ↓
health_check() function
    ↓
Return status JSON
    ↓
Status indicator updated
```

## API Specification

### 1. Main Page
```
GET /

Response: HTML/text
Status: 200 OK
Purpose: Application interface with Speed Insights

Returns:
- Full HTML page with gradient styling
- Vercel Speed Insights script injection
- async defer script loading
```

### 2. Health Check
```
GET /api/health

Response: JSON
Status: 200 OK
Purpose: Liveness probe for monitoring

Returns:
{
  "status": "healthy",
  "message": "Aegis Arsenal is running"
}

Future extensions:
- Database connectivity
- Service health
- Memory usage
- Response time metrics
```

### 3. Application Info
```
GET /api/info

Response: JSON
Status: 200 OK
Purpose: Application metadata and capabilities

Returns:
{
  "name": "Aegis Arsenal",
  "version": "1.0.0",
  "framework": "FastAPI",
  "features": [
    "Vercel Speed Insights",
    "RESTful API",
    "Static File Serving"
  ]
}

Future extensions:
- Module versions
- Available endpoints
- Configuration info
- Performance metrics
```

## Deployment Architecture

### Development Environment
```
Local Machine (./venv)
├── Python 3.9+
├── FastAPI + Uvicorn
├── npm packages
└── Speed Insights SDK
```

### Production Environment (Vercel)
```
Vercel Serverless (Python Runtime)
├── Auto-scaling functions
├── CDN for static assets
├── Speed Insights integrated
├── Environment variables managed
└── Automatic HTTPS + DNS
```

### Deployment Configuration (vercel.json)
```json
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

## Performance Optimization Strategy

### Current Optimizations
- [x] Async request handlers (async/await)
- [x] Static file serving ready (Static files mounting)
- [x] Response compression configured
- [x] Speed Insights script deferred loading

### Planned Optimizations
- [ ] Database query caching (Redis)
- [ ] Response caching headers
- [ ] Gzip compression
- [ ] CDN integration for static assets
- [ ] Database connection pooling
- [ ] Request batching for bulk operations

## Security Architecture

### Current Security
- [x] HTTPS enforced (Vercel automatic)
- [x] CORS policy ready for configuration
- [x] Environment variables isolated

### Planned Security
- [ ] API key authentication
- [ ] JWT token validation
- [ ] Rate limiting per endpoint
- [ ] Input validation & sanitization
- [ ] SQL injection prevention (ORM)
- [ ] XSS protection headers
- [ ] CSRF token validation

## Monitoring & Observability

### Speed Insights Metrics
```javascript
// Automatically collected by Vercel
- Web Vitals
  ├─ Largest Contentful Paint (LCP)
  ├─ Cumulative Layout Shift (CLS)
  └─ First Input Delay (FID)
- Core Web Vitals
  ├─ Page load time
  ├─ Interaction to next paint
  └─ Time to first byte (TTFB)
```

### Recommended Additions
- Application Performance Monitoring (APM): New Relic / DataDog
- Error Tracking: Sentry
- Log Aggregation: LogRocket / ELK Stack
- Uptime Monitoring: Better Stack / Pingdom

## Database Architecture (Phase 2)

```
PostgreSQL/MongoDB
├── Users table
├── Agents table
├── Tasks table
├── Feedback inbox (from db/feedback_inbox.sql)
└── Audit logs
```

## Scaling Strategy

### Horizontal Scaling (Vercel)
- Auto-scaling serverless functions
- CDN distribution globally
- Automatic load balancing

### Vertical Scaling (Future)
- Database optimization
- Query indexing strategy
- Caching layer (Redis)
- Microservices separation

## CI/CD Pipeline Architecture

```
Code Commit
    ↓
GitHub Actions Trigger
    ├─ Run tests
    ├─ Lint code
    ├─ Check coverage
    └─ Build artifacts
    ↓
If tests pass:
    ├─ Merge to main
    └─ Trigger Vercel deployment
    ↓
If tests fail:
    └─ Notify developer
       (Deployment blocked)
    ↓
Production Deployment
    ├─ Deploy to Vercel
    ├─ Run smoke tests
    └─ Enable monitoring
```

## Technology Decision Matrix

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Language** | Python | Existing codebase, Fast development |
| **Framework** | FastAPI | High performance, Built-in async, Great docs |
| **Server** | Uvicorn | ASGI standard, Production ready |
| **Deployment** | Vercel | Serverless, Speed Insights native, Free tier |
| **Monitoring** | Speed Insights | Native Vercel integration, Real-time RUM |
| **Testing** | pytest | Python standard, Rich plugins available |
| **CI/CD** | GitHub Actions | Native GitHub integration, Free tier |

## Error Handling Strategy

### HTTP Status Codes
```
200 OK - Successful request
201 Created - Resource created
400 Bad Request - Invalid input
401 Unauthorized - Auth required
403 Forbidden - Insufficient permissions
404 Not Found - Resource not found
500 Internal Server Error - Server fault
503 Service Unavailable - Maintenance
```

### Error Response Format
```json
{
  "error": "error_code",
  "message": "Human readable message",
  "status": 400,
  "timestamp": "2026-03-11T12:00:00Z"
}
```

## Version Strategy

- **Semantic Versioning:** MAJOR.MINOR.PATCH
- **Current:** 1.0.0
- **API Versioning:** /api/v1/*, /api/v2/* (future)

## Rollback Strategy

1. Revert commit on main branch
2. Vercel automatically re-deploys previous version
3. Notification sent to team
4. Performance metrics reviewed

## Disaster Recovery

- **RPO (Recovery Point Objective):** < 1 hour
- **RTO (Recovery Time Objective):** < 15 minutes
- **Backup Strategy:** GitHub (code), Vercel (deployments)
- **Failover:** Automatic via Vercel redundancy

---

**Blueprint Status:** APPROVED FOR PHASE 1  
**Dependencies:** All satisfied  
**Ready for Deployment:** YES ✅
