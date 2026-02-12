# Performance Testing Guide

Comprehensive guide for running performance tests and benchmarks in ContraVento.

## Overview

ContraVento uses two complementary tools for performance testing:

1. **pytest-benchmark** - For microbenchmarks and latency testing
2. **Locust** - For load testing and concurrent user simulation

## Success Criteria

From `specs/001-testing-qa/spec.md`:

### Response Time Targets (p95)
- Simple queries (health, public feed): **<200ms**
- Auth endpoints (login, register): **<500ms**
- Trip creation/updates: **<1000ms**
- Database queries: **<100ms**

### Load Targets
- Support **100+ concurrent users**
- Maintain response times under load
- Failure rate: **<1%**

## 1. Pytest-Benchmark (Microbenchmarks)

### Overview

`pytest-benchmark` measures endpoint latency in isolation (without concurrent load).

**Use Cases**:
- Endpoint response time validation
- Database query performance
- Password hashing benchmarks
- Regression detection

### Running Benchmarks

```bash
cd backend

# Run all benchmarks
poetry run pytest tests/performance/test_api_benchmarks.py -v

# Run benchmark-only mode (skip non-benchmark tests)
poetry run pytest tests/performance/test_api_benchmarks.py --benchmark-only

# Save baseline for comparison
poetry run pytest tests/performance/test_api_benchmarks.py --benchmark-save=baseline

# Compare against baseline
poetry run pytest tests/performance/test_api_benchmarks.py --benchmark-compare=baseline

# Generate histogram
poetry run pytest tests/performance/test_api_benchmarks.py --benchmark-histogram
```

### Benchmark Output

```
--------------------------------- benchmark: 8 tests ---------------------------------
Name (time in ms)                          Min     Max    Mean  StdDev  Median  Ops/s
---------------------------------------------------------------------------------------
test_health_endpoint_latency            50.23   75.12   55.34    5.21   54.12  18.07
test_login_endpoint_latency            245.67  498.23  312.45   48.12  301.23   3.20
test_public_feed_latency_empty          89.34  145.67  105.23   12.34   98.45   9.50
test_create_trip_latency               456.78  987.23  678.34   89.12  654.23   1.47
---------------------------------------------------------------------------------------
```

### Interpreting Results

**Pass Criteria**:
- Mean should be well below target (e.g., <150ms for <200ms target)
- StdDev should be low (consistent performance)
- Max (worst case) should not exceed 2x target

**Fail Indicators**:
- Mean exceeds target
- High StdDev (inconsistent performance)
- Max >> Mean (occasional severe slowdowns)

### Benchmark Categories

#### Health Check (T068)
```python
test_health_endpoint_latency()
Target: <200ms p95
```

#### Authentication (T068)
```python
test_login_endpoint_latency()
test_token_refresh_latency()
Target: <500ms p95
```

#### Public Feed (T068)
```python
test_public_feed_latency_empty()
test_public_feed_latency_with_data()
Target: <200ms p95
```

#### Trip Operations (T069)
```python
test_create_trip_latency()
test_publish_trip_latency()
test_user_trips_latency_with_data()
Target: <1000ms p95 (create), <500ms p95 (publish), <200ms p95 (list)
```

#### Database Queries (T068-T069)
```python
test_user_lookup_by_username()
test_trip_query_with_relationships()
Target: <50ms (lookup), <100ms (joins)
```

#### Security (T069)
```python
test_password_hashing_latency()
test_password_verification_latency()
Target: <500ms (intentionally slow for security)
```

## 2. Locust (Load Testing)

### Overview

Locust simulates concurrent users to test system behavior under realistic load.

**Use Cases**:
- Concurrent user capacity testing
- Stress testing
- Sustained load testing
- Bottleneck identification

### Running Load Tests

#### Interactive Mode (Web UI)

```bash
cd backend

# Start Locust web interface
poetry run locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Open browser at http://localhost:8089
# Configure:
#   - Number of users: 100
#   - Spawn rate: 10 users/second
#   - Run time: 5 minutes
```

#### Headless Mode (CLI)

```bash
# 100 users, spawn 10/second, run for 60 seconds
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 60s \
    --headless

# Generate HTML report
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 60s \
    --headless \
    --html=load-test-report.html

# Generate CSV reports
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 60s \
    --headless \
    --csv=load-test
```

### User Scenarios

#### ContraVentoUser (T070-T071)
Simulates realistic user workflow:
- Registration (on_start)
- Login (on_start)
- View profile (task weight: 10)
- View stats (task weight: 5)
- View achievements (task weight: 3)
- Update profile (task weight: 2)
- List achievements (task weight: 1)

```bash
# Run mixed load test
poetry run locust -f tests/performance/locustfile.py \
    ContraVentoUser \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --headless
```

#### RegistrationLoadTest (T070)
Focused on registration endpoint:
- 100+ concurrent registrations
- Target: <1000ms p95

```bash
# Test registration under load
poetry run locust -f tests/performance/locustfile.py \
    RegistrationLoadTest \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 20 \
    --run-time 2m \
    --headless
```

#### AuthenticationLoadTest (T071)
Focused on login endpoint:
- Repeated login requests
- Target: <500ms p95

```bash
# Test authentication under load
poetry run locust -f tests/performance/locustfile.py \
    AuthenticationLoadTest \
    --host=http://localhost:8000 \
    --users 50 \
    --spawn-rate 10 \
    --run-time 2m \
    --headless
```

### Interpreting Locust Results

#### Success Metrics
- **Requests/second (RPS)**: System throughput
- **Response time percentiles**: p50, p75, p95, p99
- **Failure rate**: Should be <1%

#### Sample Output
```
Type     Name                       # reqs  # fails  Avg  Min  Max  p95  RPS
--------------------------------------------------------------------------
GET      /health                      5000      0    52   15   180   78  83.3
POST     /auth/login                  2500      2   315  120   890  487  41.7
GET      /users/[username] (own)      10000     5   145   45   540  198  166.7
--------------------------------------------------------------------------
Aggregated                            17500     7   154   15   890  312  291.7

Response time percentiles (approximated):
 Type     Name                       50%  66%  75%  80%  90%  95%  98%  99% 100%
--------------------------------------------------------------------------------
 GET      /health                     50   55   60   65   72   78   85   90  180
 POST     /auth/login                305  350  380  410  455  487  520  550  890
 GET      /users/[username] (own)    140  155  168  180  190  198  210  225  540
```

#### Pass Criteria
- **p95 < target**: 95% of requests meet latency targets
- **Failure rate < 1%**: Less than 1% errors
- **Consistent throughput**: RPS stable over test duration

#### Fail Indicators
- **p95 > target**: Performance degradation under load
- **High failure rate**: System overload
- **Increasing response times**: Resource exhaustion
- **Timeouts**: Database connection pool exhausted

### Load Testing Strategies

#### Baseline Test (T070)
```bash
# Establish baseline performance
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users 10 \
    --spawn-rate 5 \
    --run-time 2m \
    --headless
```

#### Stress Test (T071)
```bash
# Find breaking point
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users 500 \
    --spawn-rate 50 \
    --run-time 5m \
    --headless
```

#### Soak Test (T072)
```bash
# Test sustained load over long duration
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 30m \
    --headless
```

#### Spike Test
```bash
# Sudden traffic spike
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users 200 \
    --spawn-rate 100 \  # Spawn all users quickly
    --run-time 2m \
    --headless
```

## Environment Setup

### Local Testing (SQLite)
```bash
# Start backend with SQLite
./run-local-dev.sh

# Run benchmarks
cd backend
poetry run pytest tests/performance/test_api_benchmarks.py --benchmark-only

# Run light load test
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users 20 \
    --spawn-rate 5 \
    --run-time 2m \
    --headless
```

### Docker Testing (PostgreSQL)
```bash
# Start full stack
./deploy.sh local

# Run benchmarks
cd backend
poetry run pytest tests/performance/test_api_benchmarks.py --benchmark-only

# Run full load test
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --headless \
    --html=load-test-report.html
```

### Staging/Production
```bash
# NEVER run load tests against production without approval!

# Staging load test
poetry run locust -f tests/performance/locustfile.py \
    --host=https://staging.contravento.com \
    --users 50 \
    --spawn-rate 5 \
    --run-time 5m \
    --headless
```

## Monitoring During Tests

### Backend Metrics
```bash
# Monitor server logs
tail -f backend/logs/uvicorn.log

# Monitor database connections (PostgreSQL)
docker exec -it contravento_postgres psql -U contravento -d contravento_db \
    -c "SELECT count(*) FROM pg_stat_activity WHERE datname='contravento_db';"

# Monitor memory usage
docker stats contravento_backend
```

### Database Query Profiling
```python
# Enable query logging in .env
LOG_LEVEL=DEBUG
SQLALCHEMY_ECHO=true
```

### System Resources
```bash
# CPU and memory
htop

# Network connections
netstat -an | grep :8000 | wc -l
```

## Troubleshooting

### High Latency (>target)

**Possible Causes**:
- Database connection pool exhausted
- Missing indexes on queries
- N+1 query problem
- Slow external API calls
- Memory leaks

**Solutions**:
1. Enable SQL query logging
2. Check for N+1 queries (use `joinedload()`)
3. Add database indexes
4. Increase connection pool size
5. Profile with `cProfile`

### High Failure Rate (>1%)

**Possible Causes**:
- Database connection timeouts
- Rate limiting triggered
- Application errors
- Resource exhaustion

**Solutions**:
1. Check application logs for errors
2. Monitor database connections
3. Increase timeout values
4. Scale resources (CPU, memory)

### Inconsistent Results

**Possible Causes**:
- Other processes competing for resources
- Database cache warming
- Network latency

**Solutions**:
1. Run tests in isolated environment
2. Warm up database cache first
3. Run tests multiple times and average

## Best Practices

1. **Always baseline first**: Establish normal performance before changes
2. **Test in isolation**: Close other applications during testing
3. **Warm up caches**: Run warm-up requests before measurement
4. **Use realistic data**: Seed database with production-like data volumes
5. **Monitor resources**: Track CPU, memory, database connections
6. **Document findings**: Record results for future comparison
7. **Automate regression tests**: Run benchmarks in CI/CD pipeline

## CI/CD Integration

### GitHub Actions Workflow (T073)

```yaml
# .github/workflows/performance-tests.yml
name: Performance Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Nightly at 2 AM
  workflow_dispatch:

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run benchmarks
        run: |
          cd backend
          poetry run pytest tests/performance/test_api_benchmarks.py \
            --benchmark-only \
            --benchmark-json=benchmark-results.json

      - name: Store benchmark result
        uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: 'pytest'
          output-file-path: backend/benchmark-results.json
          fail-on-alert: true
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

## References

- [pytest-benchmark docs](https://pytest-benchmark.readthedocs.io/)
- [Locust docs](https://docs.locust.io/)
- [Performance testing guide](https://martinfowler.com/articles/practical-test-pyramid.html)
