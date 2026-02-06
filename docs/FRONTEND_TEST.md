# Frontend Testing Guide

**Project Chimera: The Agentic Infrastructure Challenge**

## Quick Test

### 1. Start API Server

```bash
# Using Docker (recommended)
make docker-up

# Or manually
uv run python scripts/run_api.py
```

### 2. Access Frontend Interfaces

Once the API server is running:

- **HITL Review Interface**: http://localhost:8000/static/hitl-review.html
- **API Documentation**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### 3. Test Approval API Endpoints

```bash
# List pending approvals
curl http://localhost:8000/api/v1/approvals/pending

# Get approval details (replace with actual approval_id)
curl http://localhost:8000/api/v1/approvals/00000000-0000-0000-0000-000000000001

# Approve content (replace with actual approval_id)
curl -X POST http://localhost:8000/api/v1/approvals/00000000-0000-0000-0000-000000000001/approve \
  -H "Content-Type: application/json" \
  -d '{"feedback": "Looks good!"}'

# Reject content (replace with actual approval_id)
curl -X POST http://localhost:8000/api/v1/approvals/00000000-0000-0000-0000-000000000001/reject \
  -H "Content-Type: application/json" \
  -d '{"reason": "Inappropriate content", "feedback": "Please revise"}'
```

## Frontend Verification Checklist

### HITL Review Interface (`static/hitl-review.html`)

- [ ] Page loads without errors
- [ ] CSS stylesheet loads correctly
- [ ] API calls to `/api/v1/approvals/pending` work
- [ ] Approval cards display correctly
- [ ] Confidence badges show correct colors (high/medium/low)
- [ ] "Review" button opens approval detail view
- [ ] Approve button works
- [ ] Reject button requires reason
- [ ] Auto-refresh every 30 seconds works

### API Endpoints (`/api/v1/approvals/*`)

- [ ] `GET /api/v1/approvals/pending` returns list
- [ ] `GET /api/v1/approvals/{id}` returns details
- [ ] `POST /api/v1/approvals/{id}/approve` approves content
- [ ] `POST /api/v1/approvals/{id}/reject` rejects content
- [ ] All endpoints return proper APIResponse format
- [ ] Error handling works correctly

### Static File Serving

- [ ] `/static/hitl-review.html` accessible
- [ ] `/static/css/styles.css` accessible
- [ ] CSS loads correctly in HTML

## Expected Behavior

1. **HITL Interface**:
   - Displays pending approvals from approval queue
   - Shows confidence scores with color coding
   - Allows approve/reject actions
   - Provides feedback input

2. **API Endpoints**:
   - Return JSON in APIResponse format
   - Include proper error handling
   - Log all approval actions

## Troubleshooting

### Static Files Not Loading

1. Check static directory exists: `ls -la static/`
2. Verify FastAPI mounts static files (check logs)
3. Check file permissions: `chmod 644 static/*.html static/css/*.css`

### API Endpoints Not Working

1. Check API server is running: `curl http://localhost:8000/api/v1/health`
2. Verify router is included in `main.py`
3. Check API logs for errors

### Frontend Not Displaying Data

1. Open browser console (F12) to check for JavaScript errors
2. Verify API_BASE is correct: `/api/v1`
3. Check network tab for API call failures

---

**Reference**: `specs/frontend_requirements.md`
