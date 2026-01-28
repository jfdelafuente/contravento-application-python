# Feature 004: Celery + Redis for Asynchronous GPX Processing

**Status**: Planned (Not Started)
**Priority**: Medium (Performance Optimization)
**Estimated Effort**: 2-3 days
**Related Feature**: 003-gps-routes

---

## Overview

Add Celery + Redis distributed task queue infrastructure to handle asynchronous processing of large GPX files (>5MB), improving scalability, reliability, and monitoring capabilities.

### Problem Statement

Current implementation uses FastAPI BackgroundTasks for files >1MB, which has several limitations:
- ❌ No task persistence (tasks lost if server restarts)
- ❌ No automatic retry mechanism
- ❌ No monitoring/visibility into background job status
- ❌ Cannot scale horizontally (tied to single process)
- ❌ No priority queuing or resource management

For large GPX files (5-10MB with 50,000+ trackpoints), processing can take 20-30 seconds, blocking the FastAPI worker thread.

### Proposed Solution

Implement Celery worker infrastructure with Redis as message broker:
- Files ≤5MB: Continue using FastAPI BackgroundTasks (simple, fast)
- Files >5MB: Route to Celery workers (scalable, persistent, retryable)

---

## User Stories

### US1: Large File Processing with Persistence
**As a** cyclist uploading a large GPX file (>5MB)
**I want** the processing to continue even if the server restarts
**So that** I don't lose my upload progress

**Acceptance Criteria**:
- AC1: Files >5MB are processed by Celery workers
- AC2: If worker crashes, task is automatically re-queued
- AC3: Processing status persists in Redis
- AC4: User can poll `/gpx/{id}/status` to check progress

### US2: Automatic Retry on Transient Failures
**As a** system administrator
**I want** failed GPX processing tasks to retry automatically
**So that** temporary issues don't require manual intervention

**Acceptance Criteria**:
- AC1: Failed tasks retry up to 3 times
- AC2: Retry uses exponential backoff (60s, 120s, 240s)
- AC3: After 3 failures, task is marked as permanently failed
- AC4: Error messages are saved in database in Spanish

### US3: Worker Monitoring and Observability
**As a** DevOps engineer
**I want** to monitor task queue health and worker status
**So that** I can proactively identify and resolve issues

**Acceptance Criteria**:
- AC1: Flower UI accessible at http://localhost:5555 (local dev)
- AC2: Can view active tasks, completed tasks, and failed tasks
- AC3: Can see worker health (uptime, memory, task count)
- AC4: Task logs are structured with task_id, gpx_file_id, duration

### US4: Horizontal Scaling for High Traffic
**As a** system administrator
**I want** to scale GPX processing workers independently
**So that** upload traffic spikes don't degrade performance

**Acceptance Criteria**:
- AC1: Can run multiple worker containers simultaneously
- AC2: Workers autoscale from 2 to 10 based on queue size
- AC3: Tasks are distributed evenly across workers
- AC4: Adding/removing workers doesn't lose tasks

---

## Functional Requirements

### FR-1: Celery Task Queue Setup
- Install Celery 5.3+ with Redis transport
- Configure Redis as message broker and result backend
- Create `backend/src/celery_app.py` with app configuration
- Set task time limits: 5 minutes hard, 4.5 minutes soft

### FR-2: GPX Processing Task
- Create `backend/src/tasks/gpx_tasks.py` with task definition
- Task signature: `process_gpx_file_async(gpx_file_id, trip_id, file_content_b64, filename)`
- Use base64 encoding for file content (JSON serialization requirement)
- Reuse existing `GPXService.parse_gpx_file()` logic

### FR-3: Upload Endpoint Integration
- Modify `backend/src/api/trips.py` upload endpoint
- Add routing logic: BackgroundTasks (≤5MB) vs Celery (>5MB)
- Threshold configurable via `GPX_ASYNC_THRESHOLD_MB` env var
- Return 202 Accepted for both async modes

### FR-4: Database Session Management
- Create `DatabaseTask` base class for async session handling
- Support both PostgreSQL (production) and SQLite (dev/test)
- Implement proper connection pooling for workers
- Ensure sessions are cleaned up after task completion

### FR-5: Retry Policy
- Max retries: 3 attempts
- Backoff strategy: Exponential with jitter
- Retry delays: 60s, 120s, 240s
- Update `processing_status` to "failed" after exhausting retries

### FR-6: Docker Infrastructure
- Update `docker-compose.local.yml` with Redis, worker, Flower services
- Update `docker-compose.prod.yml` with autoscaling configuration
- Add health checks for Redis and workers
- Configure resource limits (1 CPU, 2GB RAM per worker)

---

## Non-Functional Requirements

### NFR-1: Performance
- **Target**: Process 10MB GPX file in <30s (95th percentile)
- **Scalability**: Support 100 concurrent uploads without degradation
- **Worker efficiency**: Each worker processes 100 tasks before restart (prevent memory leaks)

### NFR-2: Reliability
- **Task persistence**: 100% of tasks survive worker crashes (via `task_acks_late=True`)
- **Retry success rate**: >90% of transient failures resolved by retries
- **Worker uptime**: >99.5% availability

### NFR-3: Monitoring
- **Task visibility**: All tasks visible in Flower UI within 5 seconds
- **Metrics retention**: Task results kept in Redis for 1 hour
- **Logging**: Structured JSON logs with correlation IDs

### NFR-4: Security
- **JSON-only serialization**: Reject pickle format (prevent code execution)
- **Flower authentication**: Basic auth (local), OAuth2 (production)
- **Redis authentication**: Password-protected in production

### NFR-5: Backward Compatibility
- **Testing mode**: All files use BackgroundTasks (avoid SQLite isolation issues)
- **Graceful degradation**: If Redis unavailable, fall back to BackgroundTasks
- **Existing API**: No changes to `/gpx/{id}/status` polling endpoint

---

## Success Criteria

### SC-1: Infrastructure Deployment
- ✅ Redis, Celery worker, and Flower running in docker-compose
- ✅ Worker health check passes: `celery -A src.celery_app inspect ping`
- ✅ Flower UI accessible and shows worker status

### SC-2: Task Execution
- ✅ Large file (6MB) triggers Celery task (visible in Flower)
- ✅ Small file (4MB) uses BackgroundTasks (not in Flower)
- ✅ Task completes successfully within 5 minutes
- ✅ Trackpoints saved to database correctly

### SC-3: Retry Mechanism
- ✅ Simulate transient failure → task retries automatically
- ✅ 3 retries executed with correct delays (60s, 120s, 240s)
- ✅ After 3 failures, `processing_status = "failed"`
- ✅ Error message persisted in Spanish

### SC-4: Horizontal Scaling
- ✅ Start 2 worker containers → tasks distributed across both
- ✅ Stop 1 worker → remaining worker takes all tasks
- ✅ Add 3rd worker → new tasks routed to it
- ✅ No tasks lost during scaling operations

### SC-5: Monitoring
- ✅ Flower shows real-time task progress
- ✅ Worker logs contain structured JSON with task_id
- ✅ Failed tasks show full error traceback in Flower

---

## Technical Design

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ POST /trips/{id}/gpx                                   │ │
│  │                                                        │ │
│  │  ┌──────────────────────────────────────────┐        │ │
│  │  │ File size check                          │        │ │
│  │  │  ≤5MB → BackgroundTasks                 │        │ │
│  │  │  >5MB → Celery (via Redis)              │        │ │
│  │  └──────────────────────────────────────────┘        │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  Redis (Broker) │
         │                 │
         │  - Message Queue│
         │  - Result Store │
         │  - Task Metadata│
         └────────┬────────┘
                  │
         ┌────────┴────────┬────────────────┬──────────────┐
         ▼                 ▼                ▼              ▼
    ┌─────────┐      ┌─────────┐     ┌─────────┐   ┌──────────┐
    │ Worker 1│      │ Worker 2│     │ Worker N│   │  Flower  │
    │         │      │         │     │         │   │ Monitor  │
    │ Celery  │      │ Celery  │     │ Celery  │   │   UI     │
    │ Process │      │ Process │     │ Process │   │  :5555   │
    └────┬────┘      └────┬────┘     └────┬────┘   └──────────┘
         │                │               │
         └────────────────┴───────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │  PostgreSQL   │
                  │               │
                  │ - GPXFile     │
                  │ - TrackPoint  │
                  │ - Statistics  │
                  └───────────────┘
```

### Data Flow

1. **Upload Request**:
   ```
   User → POST /trips/{id}/gpx (7MB file)
   API → Check file_size > 5MB
   API → Base64 encode file content
   API → Submit to Celery: task.delay(gpx_file_id, trip_id, content_b64, filename)
   API → Return 202 Accepted {"processing_status": "processing"}
   ```

2. **Task Execution** (in Celery worker):
   ```
   Worker → Receive task from Redis queue
   Worker → Update status: "processing"
   Worker → Decode base64 content
   Worker → Parse GPX (Douglas-Peucker simplification)
   Worker → Save to storage/gpx_files/{year}/{month}/{trip_id}/
   Worker → Save trackpoints to database (bulk insert)
   Worker → Calculate route statistics (if timestamps)
   Worker → Update status: "completed"
   Worker → Acknowledge task (remove from queue)
   ```

3. **Status Polling** (by frontend):
   ```
   Frontend → GET /gpx/{id}/status (every 5 seconds)
   API → SELECT processing_status FROM gpx_files WHERE ...
   API → Return {"processing_status": "completed", "distance_km": 45.2, ...}
   Frontend → Display route on map
   ```

### Key Components

#### 1. Celery App (`backend/src/celery_app.py`)
```python
celery = Celery(
    "contravento",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

celery.conf.update(
    task_serializer="json",              # Security
    task_time_limit=300,                 # 5 minutes hard
    task_soft_time_limit=270,            # 4.5 minutes warning
    task_acks_late=True,                 # Persistence
    task_reject_on_worker_lost=True,     # Re-queue on crash
    worker_prefetch_multiplier=4,        # Concurrency
    worker_max_tasks_per_child=100,      # Restart after 100 tasks
)
```

#### 2. GPX Task (`backend/src/tasks/gpx_tasks.py`)
```python
@celery.task(
    base=DatabaseTask,
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
async def process_gpx_file_async(
    self, gpx_file_id, trip_id, file_content_b64, filename
):
    # 1. Decode base64
    # 2. Parse GPX
    # 3. Save to storage
    # 4. Update database
    # 5. Calculate statistics
    pass
```

#### 3. Upload Endpoint Update (`backend/src/api/trips.py`)
```python
# Line 1448: Update threshold
ASYNC_THRESHOLD_MB = settings.gpx_async_threshold_mb  # 5MB

# Line 1853: Add routing logic
if settings.celery_enabled and file_size > (5 * 1024 * 1024):
    # Celery
    content_b64 = base64.b64encode(file_content).decode()
    task = process_gpx_file_async.delay(
        gpx_file_id, trip_id, content_b64, filename
    )
else:
    # BackgroundTasks
    background_tasks.add_task(process_gpx_background, ...)
```

---

## Implementation Plan

### Phase 1: Dependencies & Config (2 hours)
- [ ] Add `celery`, `redis`, `flower` to `pyproject.toml`
- [ ] Add Celery settings to `config.py`
- [ ] Add environment variables to `.env.example`
- [ ] Run `poetry install` and verify packages

### Phase 2: Celery App Setup (3 hours)
- [ ] Create `backend/src/celery_app.py`
- [ ] Configure signal handlers (task_prerun, task_postrun, task_failure)
- [ ] Add structured logging with correlation IDs
- [ ] Test: `celery -A src.celery_app worker` starts successfully

### Phase 3: Task Definition (4 hours)
- [ ] Create `backend/src/tasks/__init__.py`
- [ ] Create `backend/src/tasks/gpx_tasks.py`
- [ ] Implement `DatabaseTask` base class
- [ ] Implement `process_gpx_file_async` task
- [ ] Add route statistics calculation
- [ ] Test: Task runs manually with test data

### Phase 4: API Integration (2 hours)
- [ ] Update upload endpoint routing logic
- [ ] Add base64 encoding for file content
- [ ] Add Celery import with conditional check
- [ ] Test: Upload triggers Celery task (mock)

### Phase 5: Docker Infrastructure (3 hours)
- [ ] Update Redis service in `docker-compose.local.yml`
- [ ] Add `celery_worker` service
- [ ] Add `flower` service
- [ ] Add `redis_data` volume
- [ ] Update backend service with Redis env vars
- [ ] Test: `./deploy.sh local` starts all services

### Phase 6: Testing (4 hours)
- [ ] Write unit tests: `test_gpx_tasks.py`
- [ ] Write integration test: Celery routing logic
- [ ] Manual test: Upload 6MB file, verify in Flower
- [ ] Manual test: Simulate worker crash, verify re-queue
- [ ] Manual test: Upload invalid GPX, verify 3 retries
- [ ] Load test: 100 concurrent uploads

### Phase 7: Documentation & Deployment (2 hours)
- [ ] Update CLAUDE.md with Celery setup instructions
- [ ] Add monitoring guide (Flower UI usage)
- [ ] Update deployment scripts with Celery info
- [ ] Create production `docker-compose.prod.yml` config
- [ ] Deploy to staging and monitor for 1 week

**Total**: ~20 hours (2.5 days)

---

## Testing Strategy

### Unit Tests
```python
# backend/tests/unit/test_gpx_tasks.py

async def test_process_gpx_file_async_success(db_session):
    """Test successful GPX processing."""
    content_b64 = base64.b64encode(valid_gpx_bytes).decode()
    result = await process_gpx_file_async(
        gpx_file_id="123",
        trip_id="456",
        file_content_b64=content_b64,
        filename="test.gpx"
    )
    assert result["success"] is True

async def test_process_gpx_file_async_retry(mock_gpx_service):
    """Test retry mechanism on transient failure."""
    mock_gpx_service.parse_gpx_file.side_effect = [
        Exception("Transient error"),  # Retry 1
        Exception("Transient error"),  # Retry 2
        {"distance_km": 45.2}          # Success on retry 3
    ]
    result = await process_gpx_file_async(...)
    assert mock_gpx_service.parse_gpx_file.call_count == 3
```

### Integration Tests
```python
# backend/tests/integration/test_gpx_api.py

async def test_large_file_uses_celery(client, auth_headers):
    """Verify >5MB files route to Celery."""
    with patch('src.api.trips.process_gpx_file_async') as mock:
        mock.delay.return_value = MagicMock(id="task-123")

        large_file = create_gpx_file(size_mb=6)
        response = await client.post(
            f"/trips/{trip_id}/gpx",
            headers=auth_headers,
            files={"file": large_file}
        )

    assert response.status_code == 202
    mock.delay.assert_called_once()
```

### Manual Testing Checklist
- [ ] Start services: `./deploy.sh local`
- [ ] Verify Flower UI: http://localhost:5555 (admin/admin123)
- [ ] Upload 4MB file → Check NOT in Flower (BackgroundTasks)
- [ ] Upload 6MB file → Check in Flower "Active" tab
- [ ] Wait for completion → Check in Flower "Succeeded" tab
- [ ] Verify trackpoints saved in database
- [ ] Stop worker → Upload file → Restart worker → Verify task processed
- [ ] Upload corrupted GPX → Verify 3 retries in Flower

---

## Deployment Strategy

### Local Development
```bash
# 1. Start all services (includes Redis, worker, Flower)
./deploy.sh local

# 2. Access Flower monitoring
open http://localhost:5555
# Login: admin / admin123

# 3. Check worker logs
docker logs contravento-celery_worker-1 -f

# 4. Upload test file
curl -X POST http://localhost:8000/trips/{id}/gpx \
  -H "Authorization: Bearer {token}" \
  -F "file=@test_large.gpx"
```

### Staging Deployment (Week 1)
```bash
# Deploy with Celery infrastructure
./deploy.sh staging

# Monitor Flower (internal only)
ssh staging
docker logs contravento-celery_worker-1 -f
open http://localhost:5555  # SSH tunnel

# Keep threshold at 5MB (only very large files)
# Monitor task success rate for 1 week
```

### Production Rollout (Week 2-3)
```bash
# Week 2: Deploy with feature flag at 10%
export CELERY_ROLLOUT_PERCENTAGE=10
./deploy.sh prod

# Week 2: Gradually increase
export CELERY_ROLLOUT_PERCENTAGE=25  # Day 2
export CELERY_ROLLOUT_PERCENTAGE=50  # Day 4
export CELERY_ROLLOUT_PERCENTAGE=100 # Day 7

# Week 3: Optimization
# - Lower threshold if performance good: 5MB → 3MB → 1MB
# - Tune worker concurrency based on load
# - Add CloudWatch alarms for failed tasks
```

### Rollback Plan
```bash
# Emergency rollback (no code changes needed)
export CELERY_ENABLED=false
docker-compose up -d backend

# All files will use BackgroundTasks
# Existing queued tasks will complete when re-enabled
```

---

## Risks & Mitigations

### Risk 1: Redis Single Point of Failure
**Impact**: High - All async processing stops
**Probability**: Medium
**Mitigation**:
- Redis health checks with automatic restart
- Redis persistence (AOF + RDB)
- Production: Redis Sentinel or Cluster for HA
- Graceful degradation: Fall back to BackgroundTasks if Redis unavailable

### Risk 2: Worker Memory Leaks
**Impact**: Medium - Workers crash after processing many tasks
**Probability**: Low
**Mitigation**:
- `worker_max_tasks_per_child=100` (restart after 100 tasks)
- Resource limits in docker-compose (2GB RAM per worker)
- Monitoring: Alert if worker memory >80%

### Risk 3: Database Connection Pool Exhaustion
**Impact**: High - Workers can't connect to database
**Probability**: Low
**Mitigation**:
- Proper session cleanup in `DatabaseTask` base class
- Connection pool size: 10 per worker (configurable)
- Monitor active connections: Alert if >80% capacity

### Risk 4: Task Queue Backlog
**Impact**: Medium - Slow processing during traffic spikes
**Probability**: Medium
**Mitigation**:
- Autoscaling: 2-10 workers based on queue size
- Horizontal scaling: Add more worker containers
- Monitoring: Alert if queue depth >50 tasks

### Risk 5: Breaking Changes in Celery Dependencies
**Impact**: Low - Upgrade breaks task execution
**Probability**: Low
**Mitigation**:
- Pin versions: `celery==5.3.4` (not `^5.3.0`)
- Test upgrades in staging first
- Keep Celery version in sync across all environments

---

## Monitoring & Alerting

### Flower UI Metrics
- **Tasks**: View active, succeeded, failed, retried tasks
- **Workers**: Monitor health, concurrency, uptime, memory
- **Broker**: Check queue size, message rate
- **Graphs**: Real-time throughput and latency charts

### CloudWatch Alarms (Production)
```yaml
alarms:
  - CeleryWorkerDown:
      metric: celery.worker.heartbeat
      threshold: 0
      duration: 5 minutes
      action: PagerDuty critical

  - TaskQueueDepth:
      metric: celery.queue.depth
      threshold: 100
      duration: 10 minutes
      action: Slack #ops-alerts

  - TaskFailureRate:
      metric: celery.tasks.failed
      threshold: 10%
      duration: 15 minutes
      action: Email ops-team@contravento.com
```

### Structured Logging
```python
logger.info(
    "GPX task completed",
    extra={
        "event": "task.completed",
        "task_id": task_id,
        "gpx_file_id": gpx_file_id,
        "trip_id": trip_id,
        "distance_km": distance_km,
        "processing_time_ms": duration,
        "retry_count": self.request.retries,
    }
)
```

---

## Future Enhancements (Out of Scope)

### Phase 2: Advanced Features
- **Task prioritization**: VIP users get higher priority queue
- **Progress tracking**: WebSocket updates instead of polling
- **Batch processing**: Process multiple GPX files in single task
- **Task scheduling**: Periodic cleanup of old task results

### Phase 3: Scalability
- **Multi-region workers**: Deploy workers in EU and US regions
- **S3 storage**: Store large GPX files in S3 instead of local disk
- **CDN integration**: Serve processed trackpoints from CDN
- **Database sharding**: Separate database for GPX data

---

## References

### Documentation
- [Celery Documentation](https://docs.celeryq.dev/)
- [Flower Documentation](https://flower.readthedocs.io/)
- [Redis Documentation](https://redis.io/docs/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

### Internal
- Feature 003 Implementation: `backend/src/api/trips.py` (lines 1323-1900)
- GPX Service: `backend/src/services/gpx_service.py`
- Current Background Task: `process_gpx_background()` (lines 1095-1313)
- Code Review: `docs/CODE_REVIEW_003.md` (recommendation for async processing)

### Related Features
- **003-gps-routes**: Current GPX upload implementation
- **002-travel-diary**: Trip photo uploads (could also use Celery)
- **013-public-trips-feed**: High-traffic endpoint (could benefit from caching)

---

**Last Updated**: 2026-01-28
**Prepared By**: Claude Code
**Review Status**: Pending stakeholder approval
