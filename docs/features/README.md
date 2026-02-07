# Features - ContraVento

Deep-dive technical documentation for implemented features.

**Last Updated**: 2026-02-07
**Status**: 🔄 In Progress (Phase 8 - Documentation Consolidation)

---

## Quick Navigation

| Feature | Documentation | Status |
|---------|--------------|--------|
| **Stats Integration** | [stats-integration.md](stats-integration.md) | ✅ Complete |
| **Cycling Types** | [cycling-types-overview.md](cycling-types-overview.md) + [cycling-types-implementation.md](cycling-types-implementation.md) | ✅ Complete |

---

## Available Feature Documentation

### 📊 Stats Integration

**File**: [stats-integration.md](stats-integration.md)

Automatic user statistics updates when trip operations occur (publish, edit, delete, add/remove photos).

**Topics**:
- Trigger workflow (publish trip, upload photo, delete photo, edit trip, delete trip)
- StatsService integration with TripService
- Automatic achievement verification
- Update patterns and examples

**Use Cases**:
- Understanding how stats are calculated
- Debugging stats inconsistencies
- Adding new stats metrics

---

### 🚴 Cycling Types

**Files**:
- [cycling-types-overview.md](cycling-types-overview.md) - Architecture and usage guide
- [cycling-types-implementation.md](cycling-types-implementation.md) - Implementation details

Dynamic management of cycling types (bikepacking, gravel, road, mountain, touring, commuting).

**Topics**:
- Database table structure (cycling_types)
- Configuration file (config/cycling_types.yaml)
- Admin API endpoints (CRUD operations)
- Public API endpoints (list active types)
- Dynamic validation
- Seed scripts

**Use Cases**:
- Adding new cycling types
- Managing cycling types via API
- Understanding type validation

---

## Related Documentation

- **[Architecture](../architecture/README.md)** - System design and patterns
- **[API Reference](../api/README.md)** - API endpoints for features
- **[Testing](../testing/README.md)** - Testing strategies
- **[User Guides](../user-guides/README.md)** - End-user documentation

---

## Contributing

To add feature documentation:

1. Create markdown file in `docs/features/`
2. Follow naming convention: `feature-name.md` (lowercase, hyphens)
3. Include:
   - **Overview**: What the feature does
   - **Architecture**: How it's implemented
   - **Usage**: How to use/configure it
   - **Related Code**: Links to key files with line numbers
   - **Examples**: Code examples and use cases
4. Update this README.md with link and description
5. Cross-reference from other docs (architecture, API, user guides)

See [docs/CONTRIBUTING.md](../CONTRIBUTING.md) for complete guidelines.

---

**Total Features Documented**: 2 (stats-integration, cycling-types)
**Coverage**: Core features with technical complexity
**Maintenance**: Update when feature changes or new features added
