# Performance Tests

Load testing for ContraVento API using Locust.

## Installation

```bash
pip install locust
```

## Running Tests

### Complete User Workflow Test

Simulates realistic user behavior (registration, login, profile views, stats, etc.):

```bash
locust -f tests/performance/locustfile.py --users 100 --spawn-rate 10 --host http://localhost:8000
```

Open http://localhost:8089 to view real-time stats.

### Registration Load Test

Focused test for user registration:

```bash
locust -f tests/performance/locustfile.py RegistrationLoadTest --users 100 --spawn-rate 20 --host http://localhost:8000
```

### Authentication Load Test

Focused test for login performance:

```bash
locust -f tests/performance/locustfile.py AuthenticationLoadTest --users 50 --spawn-rate 10 --host http://localhost:8000
```

## Performance Targets (per quickstart.md)

| Endpoint | Target (p95) | Notes |
|----------|-------------|-------|
| `/auth/register` | < 1000ms | 100+ concurrent registrations |
| `/auth/login` | < 500ms | High traffic endpoint |
| `/users/{username}` | < 200ms | Most frequent read operation |
| `/users/{username}/stats` | < 300ms | Medium frequency |
| `/users/{username}/follow` | < 400ms | Write operation |

## Headless Mode (CI/CD)

Run without web UI:

```bash
locust -f tests/performance/locustfile.py --headless --users 100 --spawn-rate 10 --run-time 60s --host http://localhost:8000
```

## Interpreting Results

- **Response time (ms)**: Should meet targets above
- **Requests/sec**: Higher is better
- **Failure rate**: Should be < 1%
- **50th percentile**: Typical user experience
- **95th percentile**: Worst-case for most users

## Common Issues

### Connection Refused

Ensure backend is running:
```bash
cd backend
uvicorn src.main:app --reload
```

### Too Many Open Files

Increase OS limits:
```bash
# Linux/Mac
ulimit -n 10000
```

### Database Locks

Use PostgreSQL for load testing (not SQLite):
```bash
docker-compose up -d postgres
```
