# Operations Documentation - ContraVento

Operations, monitoring, and maintenance documentation for ContraVento in production.

**Audience**: DevOps engineers, SREs, system administrators

---

## Quick Navigation

| I need to... | Go to |
|--------------|-------|
| 📊 Set up monitoring | [monitoring.md](monitoring.md) |
| 💾 Configure backups | [backups.md](backups.md) |
| 🗄️ Manage database | [database-management.md](database-management.md) |
| 🚨 Respond to incidents | [incident-response.md](incident-response.md) |

---

## Documentation

- **[Monitoring](monitoring.md)** - Logging, metrics, alerting (Prometheus, Grafana)
- **[Backups](backups.md)** - Backup strategy, S3 integration, restore procedures
- **[Database Management](database-management.md)** - Production DB admin tasks
- **[Incident Response](incident-response.md)** - Troubleshooting production issues

**Documentation Status**: ⏳ To be created in Phase 6 (Week 6)

---

## Production Deployment

For production deployment procedures, see:

- **[Production Mode](../deployment/modes/prod.md)** - High availability deployment
- **[Production Checklist](../deployment/guides/production-checklist.md)** - Pre-deployment validation
- **[Staging Mode](../deployment/modes/staging.md)** - Pre-production testing

---

## Monitoring (Planned)

### Prometheus Metrics

```yaml
# Sample metrics to collect
- http_requests_total
- http_request_duration_seconds
- db_query_duration_seconds
- active_users_count
- trips_created_total
```

### Grafana Dashboards

- **System Health**: CPU, memory, disk, network
- **Application Metrics**: Request rate, latency, errors
- **Business Metrics**: Active users, trips per day, photos uploaded

See [monitoring.md](monitoring.md) for complete setup.

---

## Backups (Planned)

### Automated Backups

```bash
# Backup schedule (production)
# - Every 6 hours: Full database backup to S3
# - RPO: 6 hours (max data loss)
# - RTO: 2 hours (max recovery time)
```

### Restore Procedure

```bash
# 1. Download latest backup from S3
aws s3 cp s3://contravento-backups/latest.sql.gz .

# 2. Restore to database
gunzip -c latest.sql.gz | psql -U postgres -d contravento

# 3. Verify data integrity
psql -U postgres -d contravento -c "SELECT COUNT(*) FROM trips;"
```

See [backups.md](backups.md) for complete procedures.

---

## Incident Response (Planned)

### Severity Levels

| Level | Response Time | Example |
|-------|---------------|---------|
| **P0** - Critical | 15 minutes | Site down, data loss |
| **P1** - High | 1 hour | Degraded performance, feature broken |
| **P2** - Medium | 4 hours | Minor bug, cosmetic issue |

### Runbooks

- **Database Failover**: Steps to switch to replica DB
- **Application Rollback**: Revert to previous version
- **Traffic Spike**: Scale up backends, enable rate limiting

See [incident-response.md](incident-response.md) for complete runbooks.

---

## Database Administration (Planned)

### Production Database

- **Engine**: PostgreSQL 16
- **Connection Pool**: pool_size=20
- **Backups**: Every 6 hours to S3
- **Replication**: 1 primary + 1 replica (HA mode)

### Common Tasks

```bash
# View active connections
psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Kill long-running query
psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = 12345;"

# Vacuum database
psql -U postgres -d contravento -c "VACUUM ANALYZE;"
```

See [database-management.md](database-management.md) for complete reference.

---

## Scaling (Planned)

### Horizontal Scaling

```yaml
# docker-compose.prod.yml
backend:
  deploy:
    replicas: 3  # Scale to 3 instances
```

### Vertical Scaling

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
```

---

## Related Documentation

- **[Production Mode](../deployment/modes/prod.md)** - Production deployment
- **[Staging Mode](../deployment/modes/staging.md)** - Pre-production testing
- **[Production Checklist](../deployment/guides/production-checklist.md)** - Validation
- **[Database Management](../deployment/guides/database-management.md)** - DB operations

---

**Last Updated**: 2026-02-06
**Consolidation Plan**: Phase 1 (Foundation) - Directory structure
**Status**: Placeholder - Full documentation to be created in Phase 6
