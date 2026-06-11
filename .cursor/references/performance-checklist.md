# Performance Review Checklist

Use during the Performance axis of code review. For workflow guidance, see the `performance-optimization` rule.

## Database and Queries

- [ ] No N+1 query patterns (loop fetching related records individually)
- [ ] List endpoints use pagination or cursor-based limits
- [ ] Queries have appropriate indexes for new filter/sort fields
- [ ] No unbounded `SELECT *` or full collection scans
- [ ] Bulk operations used instead of per-row updates in loops
- [ ] Connection pooling respected (no connection leaks)

**Red flags:** `for item in items: db.query(item.id)`, missing `LIMIT`, fetching all columns when only two are needed.

**Escalate to profiling when:** Query count scales with list size, or latency reported >100ms on indexed lookups.

## API and Backend

- [ ] List/search endpoints return paginated results with sane defaults
- [ ] Response payloads trimmed to required fields
- [ ] Heavy computation moved off request path (background jobs, caching)
- [ ] Async I/O used for network and database calls in async frameworks
- [ ] No blocking sync calls inside async handlers
- [ ] Timeouts set on external HTTP calls

**Red flags:** Returning entire object graphs, synchronous file I/O in request handler, no timeout on third-party API calls.

## Frontend and UI

- [ ] List rendering uses virtualization or pagination for large datasets
- [ ] Components avoid unnecessary re-renders (stable keys, memoization where warranted)
- [ ] Expensive computations moved out of render path (`computed`, memoization where warranted)
- [ ] Images/assets lazy-loaded or appropriately sized
- [ ] Bundle impact of new dependencies assessed
- [ ] Debounce/throttle on high-frequency events (search, scroll, resize)

**Red flags:** Mapping 10k items without virtualization, inline object/array literals in props causing re-renders, importing entire library for one function.

## Memory and Hot Paths

- [ ] No large object allocation inside tight loops
- [ ] Caching considered for repeated expensive computations
- [ ] Streams used for large file processing instead of loading into memory
- [ ] Event listeners and subscriptions cleaned up on unmount/destroy
- [ ] No unbounded in-memory caches without eviction

**Red flags:** Building full arrays in memory for export, accumulating results in global state without bounds, memory leak from uncleaned listeners.

## Caching

- [ ] Cache keys include all relevant input dimensions
- [ ] TTL or invalidation strategy defined for cached data
- [ ] Cache misses don't cause thundering herd (stale-while-revalidate, locking)
- [ ] Stale data acceptable? Documented if yes

**Red flags:** Caching user-specific data with shared key, no invalidation on writes, caching errors or empty results indefinitely.

## When to Profile vs Checklist

| Situation | Action |
|-----------|--------|
| Obvious N+1 or missing pagination | Fix from checklist — no profiling needed |
| "Feels slow" but no clear pattern | Profile before optimizing |
| New endpoint with complex aggregation | Benchmark with realistic data volume |
| UI jank reported | Use browser profiler / Vue DevTools |
| Optimization without measured bottleneck | **Optional** — challenge the change |

## Severity Guide

| Finding | Severity |
|---------|----------|
| N+1 on high-traffic endpoint, unbounded data fetch | **Critical** — blocks merge |
| Missing pagination on new list endpoint | Required — must fix |
| Unnecessary re-render in low-traffic admin page | **Nit** — optional |
| Missing cache on expensive static computation | **Consider** — evaluate traffic |
