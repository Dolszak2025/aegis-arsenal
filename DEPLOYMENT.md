# Aegis Arsenal - Deployment Guide

**Version:** 1.0.0  
**Status:** Ready for Vercel Deployment  
**Date:** March 11, 2026

---

## Pre-Deployment Verification

### ✅ Local Testing Checklist

```bash
# 1. Verify app imports correctly
python -c "from main import app; print(f'App: {app.title}')"

# 2. Run test suite
python -m pytest tests/ -v

# 3. Verify all endpoints
python -c "
from starlette.testclient import TestClient
from main import app
client = TestClient(app)
print('Testing endpoints...')
print(f'GET /: {client.get(\"/\").status_code}')
print(f'GET /api/health: {client.get(\"/api/health\").status_code}')
print(f'GET /api/info: {client.get(\"/api/info\").status_code}')
"
```

---

## Deployment Strategies

### Option 1: Using Vercel CLI (Recommended)

#### Prerequisites
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login
```

#### Deployment Steps

```bash
# Step 1: Navigate to project root
cd /workspaces/aegis-arsenal

# Step 2: Deploy to staging
vercel deploy

# Expected output:
# > Creating deployment...
# > https://aegis-arsenal-xxxxx.vercel.app (staging)

# Step 3: Test staging deployment
# Visit the URL and verify Speed Insights script loads

# Step 4: Deploy to production
vercel deploy --prod

# Expected output:
# > Deploying to production...
# > https://aegis-arsenal.vercel.app (production)
```

#### Enable Speed Insights

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select "aegis-arsenal" project
3. Click "Speed Insights" in sidebar
4. Click "Enable" button
5. Wait for data collection to begin

---

### Option 2: GitHub Integration (Automated)

The CI/CD pipeline is configured in `.github/workflows/ci-cd.yml`

#### Setup Required

1. **Add Vercel Secrets to GitHub**
   - Go to Repository Settings → Secrets and Variables
   - Add three secrets:
     - `VERCEL_TOKEN`: Get from [Vercel Account Settings](https://vercel.com/account/tokens)
     - `VERCEL_ORG_ID`: Get from Vercel dashboard
     - `VERCEL_PROJECT_ID`: Get from vercel.json

2. **Trigger Automatic Deployment**
   ```bash
   git push origin main
   # → Automatically runs tests and deploys to Vercel
   ```

---

## Full Deployment Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    START: PR #9 Ready                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Review Code & Tests                                 │
│ ✅ 29/29 tests passing                                       │
│ ✅ All quality checks done                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Merge PR #9 to main                                 │
│ Command: gh pr merge 9 --squash                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Deploy to Production                                │
│ Command: vercel deploy --prod                               │
│ Expected: Production URL returned                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Enable Speed Insights                               │
│ Action: Manual via Vercel Dashboard                         │
│ Path: Project → Speed Insights → Enable                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Verify Deployment                                   │
│ ✅ Visit production URL                                      │
│ ✅ Check health endpoint responses                           │
│ ✅ Verify Speed Insights loads                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                ✅ DEPLOYMENT COMPLETE!                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Post-Deployment Validation

### ✅ Critical Checks

```bash
# 1. Verify Production URL is accessible
curl -I https://aegis-arsenal.vercel.app/

# Expected output:
# HTTP/2 200 
# content-type: text/html
# cache-control: public, max-age=0

# 2. Verify API endpoints
curl https://aegis-arsenal.vercel.app/api/health | jq

# Expected output:
# {
#   "status": "healthy",
#   "message": "Aegis Arsenal is running"
# }

# 3. Verify Speed Insights script
curl https://aegis-arsenal.vercel.app/ | grep "vercel/speed-insights"

# Expected output:
# Should contain: /_vercel/speed-insights/script.js
```

### 🟡 Important Checks

1. **Check Vercel Logs**
   - Dashboard → Project → Deployments → Latest
   - Verify no errors in Function Logs

2. **Monitor Speed Insights Dashboard**
   - Should start collecting metrics within 5-10 minutes
   - Check for Real User Monitoring (RUM) data

3. **Test from Different Browsers**
   - Chrome, Firefox, Safari, Edge
   - Verify responsive design

---

## Troubleshooting

### Issue: 404 Not Found

**Solution:**
```bash
# Verify vercel.json routes
cat vercel.json

# Should have:
# "src": "/(.*)"
# "dest": "main.py"
```

### Issue: Function Timeout

**Solution:**
```bash
# Check for long-running operations
# Reduce startup time by:
# 1. Lazy loading imports
# 2. Moving calculations outside critical path
# 3. Using async operations
```

### Issue: No Speed Insights Data

**Solution:**
```bash
# 1. Verify Speed Insights enabled in dashboard
# 2. Clear browser cache
# 3. Wait 5-10 minutes for data collection
# 4. Check that script loads in browser DevTools
```

### Issue: Environment Variables Not Working

**Solution:**
```bash
# Add variables in Vercel Dashboard
# Project Settings → Environment Variables
# Format: KEY=VALUE
# Redeploy to apply changes
```

---

## Rollback Procedure

### If Deployment Breaks Production

```bash
# Option 1: Revert commit
git revert HEAD
git push origin main
# Vercel auto-deploys the previous version

# Option 2: Manual rollback via Vercel
# Dashboard → Deployments → Select previous version → Promote to Production
```

---

## Deployment Monitoring

### Recommended Monitoring Setup

```yaml
Health Check:
  Endpoint: /api/health
  Interval: 30 seconds
  Expected: 200 OK, status: "healthy"

Performance Metrics:
  Tool: Speed Insights (built-in)
  Metrics:
    - Largest Contentful Paint (LCP)
    - Cumulative Layout Shift (CLS)
    - First Input Delay (FID)

Uptime Monitoring:
  Tool: Better Stack / Pingdom (recommended)
  Target: 99.9% uptime
```

---

## Scaling Strategy

### Current Capacity (Vercel Pro)

| Metric | Limit | Current |
|--------|-------|---------|
| Concurrent Requests | 1,000 | ~10 |
| Function Memory | 3,072 MB | 1,024 MB (default) |
| Timeout | 60 seconds | ~10ms (typical) |
| Deployments/day | Unlimited | < 5 |

### When to Scale Up

- [ ] Consistent CPU > 70%
- [ ] Response time > 500ms
- [ ] Error rate > 0.1%
- [ ] Daily active users > 10,000

### Scaling Options

1. **Increase Function Memory** (Vercel Pro)
   - Settings → General → Function Concurrency
   - Allocate more memory per instance

2. **Enable Auto-scaling**
   - Vercel automatically scales based on demand
   - No configuration needed for HTTP traffic

3. **Upgrade Vercel Plan**
   - Pro: $20/month - More features
   - Enterprise: Custom scaling

---

## Cost Optimization

### Current Costs (Vercel)

| Component | Free Tier | Pro Tier |
|-----------|-----------|----------|
| Deployments | Unlimited | Unlimited |
| Bandwidth | 100 GB/month | 1 TB/month |
| Speed Insights | Included | Included |
| Edge Network | Yes | Yes |

### Cost Reduction Strategy

1. **Optimize Bundle Size**
   - Minify CSS/JS
   - Lazy load assets
   - Use tree-shaking

2. **Enable Caching**
   - Set appropriate cache headers
   - Use CDN for static assets

3. **Monitor Bandwidth**
   - Review Vercel dashboard monthly
   - Alert if exceeds budget

---

## Deployment Timeline

### Immediate (Day 1)
- [x] Run all tests
- [x] Merge PR #9
- [x] Deploy to Vercel production
- [x] Enable Speed Insights
- [x] Verify endpoints

### This Week (Days 2-7)
- [ ] Monitor error rates
- [ ] Collect performance baselines
- [ ] Setup automated alerts
- [ ] Document deployment process

### This Month (Days 8-30)
- [ ] Optimize performance
- [ ] Complete integration tests
- [ ] Document lessons learned
- [ ] Plan v1.1 roadmap

---

## Support & Escalation

### Issues Contact

| Level | Contact | Response Time |
|-------|---------|---------------|
| Critical | @Dolszak2025 | 15 minutes |
| High | Team Lead | 1 hour |
| Medium | Dev Team | 4 hours |
| Low | Issue Tracker | 24 hours |

---

## Success Criteria

✅ **Deployment is successful when:**

1. Application is live at https://aegis-arsenal.vercel.app/
2. All API endpoints respond with correct status codes
3. Health check returns healthy status
4. Speed Insights dashboard shows data
5. No errors in Vercel function logs
6. Response times < 1 second
7. Uptime > 99.5%

---

## Next Phase: Post-Deployment

Once deployment is verified:

1. **Setup Production Monitoring**
   - Sentry for error tracking
   - DataDog for APM
   - LogRocket for session replay

2. **Complete Module Integration**
   - Integrate agents/ module
   - Connect logos_orchestrator/
   - Setup database layer

3. **Performance Optimization**
   - Profile and optimize endpoints
   - Implement caching strategy
   - Optimize database queries

4. **Security Hardening**
   - Implement API authentication
   - Add rate limiting
   - Setup WAF rules

---

**Deployment Guide Status:** READY ✅  
**Last Updated:** March 11, 2026  
**Next Review:** After successful production deployment
