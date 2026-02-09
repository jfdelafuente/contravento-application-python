# GPX Processing Metrics Monitoring

**Purpose**: Collect operational metrics for evaluating Celery+Redis adoption in Q2 2026
**Feature**: `feature/gpx-metrics-monitoring`
**Related Spec**: [specs/004-celery-async-tasks/spec.md](../../specs/004-celery-async-tasks/spec.md)
**Roadmap**: [ROADMAP.md](../../ROADMAP.md) - Q2 2026 milestone

---

## Overview

This monitoring system tracks GPX file upload and processing performance to provide data-driven decision making for infrastructure upgrades. Metrics are logged as structured JSON for easy analysis.

**Current Implementation**: FastAPI `BackgroundTasks` (files >1MB)
**Evaluation Target**: Celery + Redis distributed task queue
**Decision Timeline**: Q2 2026 (after 3-6 months of data collection)

---

## Metrics Collected

### 1. GPX_UPLOAD_START

**When**: User initiates GPX file upload
**Purpose**: Track upload volume and file size distribution

```json
{
  "metric_type": "gpx_upload",
  "trip_id": "abc123",
  "user_id": "user456",
  "file_size_mb": 3.45,
  "file_name": "ruta-pirineos.gpx",
  "threshold_mb": 1
}
```

**Key Fields**:
- `file_size_mb`: File size in megabytes (decimal precision)
- `user_id`: User identifier for usage patterns
- `threshold_mb`: Current sync/async decision threshold

---

### 2. GPX_PROCESSING_MODE

**When**: System decides sync vs async processing
**Purpose**: Track processing mode distribution

```json
{
  "metric_type": "gpx_processing_mode",
  "trip_id": "abc123",
  "processing_mode": "async",
  "file_size_mb": 3.45,
  "reason": "file_size > 1MB threshold"
}
```

**Processing Modes**:
- `sync`: Files ≤1MB - immediate processing
- `async`: Files >1MB - background processing

---

### 3. GPX_PROCESSING_COMPLETE

**When**: GPX processing finishes successfully
**Purpose**: Measure processing time and resource usage

```json
{
  "metric_type": "gpx_processing_complete",
  "trip_id": "abc123",
  "gpx_file_id": "gpx789",
  "processing_mode": "async",
  "processing_time_seconds": 28.67,
  "file_size_mb": 7.82,
  "total_points": 52000,
  "simplified_points": 487,
  "distance_km": 215.3,
  "has_elevation": true,
  "status": "success"
}
```

**Critical Metrics**:
- `processing_time_seconds`: Total processing duration ⚠️ **KEY METRIC**
- `total_points`: Original GPX trackpoints
- `simplified_points`: Simplified trackpoints (Douglas-Peucker algorithm)

---

### 4. GPX_BACKGROUND_START

**When**: Background task begins processing
**Purpose**: Track async processing initiation

```json
{
  "metric_type": "gpx_background_start",
  "gpx_file_id": "gpx789",
  "trip_id": "abc123",
  "file_size_mb": 7.82
}
```

---

### 5. GPX_PROCESSING_ERROR

**When**: GPX processing fails
**Purpose**: Track error rates and failure patterns

```json
{
  "metric_type": "gpx_processing_error",
  "trip_id": "abc123",
  "gpx_file_id": "gpx789",
  "processing_mode": "async",
  "file_size_mb": 5.2,
  "processing_time_seconds": 15.3,
  "error_type": "INVALID_GPX_FORMAT",
  "error_message": "No trackpoints found in GPX file"
}
```

**Error Types**:
- `INVALID_GPX_FORMAT`: Malformed GPX file
- `INTERNAL_ERROR`: Unexpected processing error

---

## Log Location

### Development (local-dev mode)

```bash
# SQLite mode - logs to stdout
./run-local-dev.sh

# Logs appear in terminal
# Look for lines starting with: GPX_UPLOAD_START, GPX_PROCESSING_MODE, etc.
```

### Production (Docker deployment)

```bash
# View logs from backend container
docker-compose -f docker-compose.prod.yml logs -f backend | grep "GPX_"

# Save to file for analysis
docker-compose -f docker-compose.prod.yml logs backend > gpx_metrics.log
```

### Log Format

Structured JSON with `extra={}` fields:

```
2026-02-09 14:23:45 INFO GPX_UPLOAD_START {"metric_type": "gpx_upload", "file_size_mb": 3.45, ...}
```

---

## Data Analysis

### Quick Statistics (Bash)

**Total uploads**:
```bash
grep "GPX_UPLOAD_START" backend.log | wc -l
```

**Files larger than 5MB**:
```bash
grep "GPX_UPLOAD_START" backend.log | jq 'select(.file_size_mb > 5)' | wc -l
```

**Average processing time**:
```bash
grep "GPX_PROCESSING_COMPLETE" backend.log | \
  jq '.processing_time_seconds' | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count "seconds"}'
```

**Processing time >30 seconds**:
```bash
grep "GPX_PROCESSING_COMPLETE" backend.log | \
  jq 'select(.processing_time_seconds > 30)'
```

**Error rate**:
```bash
total=$(grep "GPX_UPLOAD_START" backend.log | wc -l)
errors=$(grep "GPX_PROCESSING_ERROR" backend.log | wc -l)
echo "scale=2; $errors / $total * 100" | bc
# Output: 2.50 (means 2.5% error rate)
```

---

### Python Analysis Script

Create `scripts/analyze_gpx_metrics.py`:

```python
#!/usr/bin/env python3
"""
Analyze GPX processing metrics for Celery evaluation.

Usage:
    python scripts/analyze_gpx_metrics.py backend.log
"""

import json
import sys
from collections import Counter
from datetime import datetime


def analyze_metrics(log_file):
    """Parse log file and extract GPX metrics."""
    metrics = []

    with open(log_file, 'r') as f:
        for line in f:
            try:
                # Look for structured log entries
                if 'metric_type' in line:
                    # Extract JSON portion (after timestamp and level)
                    json_start = line.find('{')
                    if json_start != -1:
                        data = json.loads(line[json_start:])
                        metrics.append(data)
            except (json.JSONDecodeError, ValueError):
                continue

    return metrics


def generate_report(metrics):
    """Generate analysis report."""
    uploads = [m for m in metrics if m.get('metric_type') == 'gpx_upload']
    completions = [m for m in metrics if m.get('metric_type') == 'gpx_processing_complete']
    errors = [m for m in metrics if m.get('metric_type') == 'gpx_processing_error']

    # File size analysis
    file_sizes = [m['file_size_mb'] for m in uploads if 'file_size_mb' in m]
    large_files = [s for s in file_sizes if s > 5]

    # Processing time analysis
    proc_times = [m['processing_time_seconds'] for m in completions if 'processing_time_seconds' in m]
    slow_processing = [t for t in proc_times if t > 30]

    # Processing mode distribution
    modes = Counter([m.get('processing_mode') for m in completions])

    print("=" * 60)
    print("GPX METRICS ANALYSIS REPORT")
    print("=" * 60)
    print()

    print(f"📊 UPLOAD STATISTICS")
    print(f"   Total uploads: {len(uploads)}")
    if file_sizes:
        print(f"   Average file size: {sum(file_sizes) / len(file_sizes):.2f} MB")
        print(f"   Max file size: {max(file_sizes):.2f} MB")
        print(f"   Min file size: {min(file_sizes):.2f} MB")
    print()

    print(f"📈 PROCESSING STATISTICS")
    print(f"   Successful: {len(completions)}")
    print(f"   Failed: {len(errors)}")
    if completions:
        success_rate = len(completions) / (len(completions) + len(errors)) * 100
        print(f"   Success rate: {success_rate:.1f}%")
    print()

    if proc_times:
        print(f"⏱️  PROCESSING TIME")
        print(f"   Average: {sum(proc_times) / len(proc_times):.2f}s")
        print(f"   Max: {max(proc_times):.2f}s")
        print(f"   Min: {min(proc_times):.2f}s")
        print(f"   >30s (slow): {len(slow_processing)} ({len(slow_processing) / len(proc_times) * 100:.1f}%)")
    print()

    print(f"🔄 PROCESSING MODE")
    for mode, count in modes.items():
        print(f"   {mode}: {count} ({count / len(completions) * 100:.1f}%)")
    print()

    print("=" * 60)
    print("🎯 CELERY ADOPTION DECISION CRITERIA")
    print("=" * 60)
    print()

    # Criterion 1: Files >5MB
    large_file_pct = (len(large_files) / len(file_sizes) * 100) if file_sizes else 0
    criterion1 = large_file_pct > 20
    status1 = "✅ PASS" if criterion1 else "❌ FAIL"
    print(f"1. Files >5MB: {len(large_files)}/{len(file_sizes)} ({large_file_pct:.1f}%) {status1}")
    print(f"   Threshold: >20% → {'IMPLEMENT CELERY' if criterion1 else 'BackgroundTasks OK'}")
    print()

    # Criterion 2: Slow processing
    slow_pct = (len(slow_processing) / len(proc_times) * 100) if proc_times else 0
    criterion2 = slow_pct > 10
    status2 = "✅ PASS" if criterion2 else "❌ FAIL"
    print(f"2. Processing >30s: {len(slow_processing)}/{len(proc_times)} ({slow_pct:.1f}%) {status2}")
    print(f"   Threshold: >10% → {'IMPLEMENT CELERY' if criterion2 else 'BackgroundTasks OK'}")
    print()

    # Criterion 3: Error rate
    error_rate = (len(errors) / (len(completions) + len(errors)) * 100) if (completions or errors) else 0
    criterion3 = error_rate > 5
    status3 = "✅ PASS" if criterion3 else "❌ FAIL"
    print(f"3. Error rate: {error_rate:.1f}% {status3}")
    print(f"   Threshold: >5% → {'INVESTIGATE' if criterion3 else 'Normal'}")
    print()

    # Final recommendation
    criteria_passed = sum([criterion1, criterion2])
    print("=" * 60)
    if criteria_passed >= 2:
        print("🚀 RECOMMENDATION: IMPLEMENT CELERY + REDIS")
        print("   Rationale: ≥2 criteria met, BackgroundTasks insufficient")
    elif criteria_passed == 1:
        print("⚠️  RECOMMENDATION: MONITOR FOR ANOTHER MONTH")
        print("   Rationale: 1 criterion met, borderline case")
    else:
        print("✅ RECOMMENDATION: KEEP BACKGROUNDTASKS")
        print("   Rationale: Current solution adequate, no action needed")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_gpx_metrics.py <log_file>")
        sys.exit(1)

    log_file = sys.argv[1]
    metrics = analyze_metrics(log_file)

    if not metrics:
        print(f"⚠️  No metrics found in {log_file}")
        sys.exit(1)

    generate_report(metrics)
```

**Usage**:
```bash
# Extract logs from Docker
docker-compose -f docker-compose.prod.yml logs backend > backend.log

# Run analysis
python scripts/analyze_gpx_metrics.py backend.log
```

---

## Decision Criteria for Celery Adoption

### Criterion 1: Large File Volume (>5MB)

**Threshold**: >20% of uploads are >5MB files
**Reasoning**: Large files (>5MB) contain 50,000+ trackpoints and take 20-30 seconds to process, blocking FastAPI workers

**Query**:
```bash
total=$(grep "GPX_UPLOAD_START" backend.log | wc -l)
large=$(grep "GPX_UPLOAD_START" backend.log | jq 'select(.file_size_mb > 5)' | wc -l)
percentage=$(echo "scale=1; $large / $total * 100" | bc)
echo "Large files: $percentage%"
```

**Decision**:
- ✅ ≥20% → Implement Celery
- ❌ <20% → BackgroundTasks sufficient

---

### Criterion 2: Slow Processing Frequency

**Threshold**: >10% of processing operations take >30 seconds
**Reasoning**: Processing >30s indicates worker blocking that could impact concurrent requests

**Query**:
```bash
total=$(grep "GPX_PROCESSING_COMPLETE" backend.log | wc -l)
slow=$(grep "GPX_PROCESSING_COMPLETE" backend.log | jq 'select(.processing_time_seconds > 30)' | wc -l)
percentage=$(echo "scale=1; $slow / $total * 100" | bc)
echo "Slow processing: $percentage%"
```

**Decision**:
- ✅ ≥10% → Implement Celery
- ❌ <10% → BackgroundTasks sufficient

---

### Criterion 3: Worker Blocking Errors

**Threshold**: >5 timeout/blocking errors per week
**Reasoning**: Errors indicate infrastructure limitations

**Query**:
```bash
grep "GPX_PROCESSING_ERROR" backend.log | grep -i "timeout\|blocked\|worker" | wc -l
```

**Decision**:
- ✅ ≥5 errors/week → Implement Celery
- ❌ <5 errors/week → BackgroundTasks sufficient

---

## Evaluation Timeline

### Phase 1: Data Collection (Q1 2026 - Current)

**Start**: After merging `feature/gpx-metrics-monitoring` to `develop`
**Duration**: 3-6 months
**Action**: Deploy to production and collect metrics

```bash
# No action required - metrics collected automatically
# Optional: Periodic manual checks
docker-compose -f docker-compose.prod.yml logs backend | tail -100 | grep "GPX_"
```

---

### Phase 2: Analysis (Q2 2026)

**Timing**: April-May 2026
**Duration**: 1 week
**Action**: Run analysis scripts and evaluate criteria

**Steps**:
1. Extract 3-6 months of logs:
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend > backend_q1_2026.log
   ```

2. Run analysis:
   ```bash
   python scripts/analyze_gpx_metrics.py backend_q1_2026.log > analysis_report.txt
   ```

3. Review report and make decision

---

### Phase 3: Decision & Implementation (Q2 2026)

**Option A - Implement Celery** (if ≥2 criteria met):
- Follow [specs/004-celery-async-tasks/spec.md](../../specs/004-celery-async-tasks/spec.md)
- Estimated effort: 2-3 days
- Tech stack: Celery, Redis, Flower (monitoring UI)

**Option B - Keep BackgroundTasks** (if <2 criteria met):
- No changes required
- Re-evaluate in Q3 2026 or when traffic increases

**Option C - Monitor Another Month** (borderline case):
- 1 criterion met, wait for more data
- Re-analyze in June 2026

---

## Troubleshooting

### No Metrics in Logs

**Problem**: Can't find `GPX_UPLOAD_START` or other metrics

**Solutions**:
1. Check log level is INFO or DEBUG:
   ```bash
   # In backend/.env or docker-compose
   LOG_LEVEL=INFO
   ```

2. Verify feature is deployed:
   ```bash
   git log --oneline | grep "gpx-metrics-monitoring"
   ```

3. Check backend is running:
   ```bash
   docker-compose ps backend
   ```

---

### JSON Parsing Errors

**Problem**: `jq` fails to parse log lines

**Cause**: Logs include non-JSON content (timestamps, levels)

**Solution**: Extract JSON portion only
```bash
# Extract JSON from log line
cat backend.log | grep "GPX_UPLOAD_START" | sed 's/.*{/{/' | jq '.'
```

---

### Incomplete Data

**Problem**: Missing metrics for some uploads

**Causes**:
- Server restarts during processing
- Uncaught exceptions
- Log rotation

**Solutions**:
1. Check for error logs around missing uploads
2. Verify log persistence across restarts
3. Consider log aggregation service (CloudWatch, Datadog)

---

## Related Documentation

- **Feature Spec**: [specs/004-celery-async-tasks/spec.md](../../specs/004-celery-async-tasks/spec.md)
- **Roadmap**: [ROADMAP.md](../../ROADMAP.md) - Q2 2026 milestones
- **GPX Service**: `backend/src/services/gpx_service.py`
- **GPX API**: `backend/src/api/gpx_routes.py`

---

## Contact

For questions about this monitoring system:
- Check implementation: `feature/gpx-metrics-monitoring` branch
- Review spec: `specs/004-celery-async-tasks/spec.md`
- Update roadmap: `ROADMAP.md` (Q2 2026 section)

---

**Last Updated**: 2026-02-09
**Maintained By**: Development Team
**Review Cycle**: Before Q2 2026 evaluation
