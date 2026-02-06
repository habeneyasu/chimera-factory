# ADR-001: Hybrid Database Architecture

**Status**: Accepted  
**Date**: 2026-02-06  
**Deciders**: Architecture Team  
**Tags**: architecture, database, weaviate, postgresql, redis

---

## Context

Project Chimera requires storing and retrieving diverse data types with different access patterns, performance requirements, and integrity constraints:

1. **Semantic Memory**: Agent memories, persona definitions, and world knowledge requiring semantic search and RAG (Retrieval-Augmented Generation)
2. **Transactional Data**: Campaigns, approvals, audit logs requiring ACID guarantees
3. **Ephemeral Cache**: Short-term memory (conversation history), task queues, rate limiting requiring sub-millisecond access
4. **Financial Ledger**: Immutable, cryptographically-verified transaction records

Traditional single-database approaches (e.g., PostgreSQL-only or MongoDB-only) cannot efficiently handle all these requirements simultaneously.

---

## Decision

We will use a **hybrid multi-database architecture** with specialized databases for each data pattern:

- **Weaviate**: Semantic memory (vector database, RAG for long-term agent persona consistency)
- **PostgreSQL**: Transactional data (campaigns, approvals, audit logs, structured data)
- **Redis**: Episodic cache & task queuing (short-term memory, task queues, rate limiting)
- **On-Chain Storage** (Base, Ethereum, Solana): Financial ledger (immutable financial transactions)

---

## Alternatives Considered

### Alternative 1: PostgreSQL with pgvector Extension

**Approach**: Use PostgreSQL with the `pgvector` extension for vector similarity search.

**Pros**:
- Single database to manage
- ACID guarantees for all data
- Strong consistency model
- Familiar technology stack

**Cons**:
- **Performance**: Vector search in PostgreSQL is slower than specialized vector databases
- **Scalability**: Limited horizontal scaling for vector operations
- **RAG Limitations**: Less optimized for complex semantic retrieval patterns
- **Resource Contention**: Vector operations compete with transactional queries
- **Feature Gaps**: Missing advanced RAG features (hierarchical memory, semantic clustering)

**Rejected Because**: Performance and scalability limitations for semantic memory operations. Weaviate provides specialized vector search capabilities optimized for RAG workflows.

---

### Alternative 2: MongoDB for All Data

**Approach**: Use MongoDB as the primary database for all data types (document store with flexible schema).

**Pros**:
- Flexible schema for semi-structured data
- Horizontal scaling capabilities
- Good for content drafts and trend snapshots

**Cons**:
- **No Vector Search**: MongoDB lacks native vector similarity search (would require external service)
- **ACID Limitations**: Weaker transactional guarantees than PostgreSQL
- **Semantic Memory**: Not optimized for RAG or semantic retrieval
- **Financial Ledger**: Not suitable for immutable, cryptographically-verified records

**Rejected Because**: Cannot efficiently handle semantic memory requirements or provide strong ACID guarantees for transactional data.

---

### Alternative 3: Single Vector Database (Weaviate Only)

**Approach**: Use Weaviate for all data storage, including transactional data.

**Pros**:
- Single database to manage
- Excellent semantic search capabilities
- Good for RAG workflows

**Cons**:
- **ACID Limitations**: Weaviate provides eventual consistency, not strong ACID guarantees
- **Transactional Data**: Not optimized for complex relational queries (joins, transactions)
- **Financial Ledger**: Cannot provide immutable, cryptographically-verified records
- **Cache Performance**: Slower than Redis for ephemeral data (task queues, rate limiting)

**Rejected Because**: Cannot provide ACID guarantees required for transactional data (campaigns, approvals, audit logs) or sub-millisecond performance for caching.

---

### Alternative 4: PostgreSQL + Redis Only

**Approach**: Use PostgreSQL for persistent data and Redis for caching, without a vector database.

**Pros**:
- Simpler architecture (two databases)
- PostgreSQL provides strong ACID guarantees
- Redis provides fast caching

**Cons**:
- **No Semantic Memory**: Cannot efficiently store or retrieve agent memories with semantic search
- **No RAG**: Cannot implement Retrieval-Augmented Generation for long-term agent persona consistency
- **Limited AI Capabilities**: Agents cannot maintain coherent long-term memory across sessions

**Rejected Because**: Semantic memory and RAG are core requirements for autonomous agents. Without vector search, agents cannot maintain persona consistency or leverage long-term knowledge effectively.

---

## Consequences

### Positive

1. **Optimized Performance**: Each database is optimized for its specific use case
   - Weaviate: Fast semantic search and RAG
   - PostgreSQL: Fast relational queries with ACID guarantees
   - Redis: Sub-millisecond cache access

2. **Scalability**: Each database can scale independently based on workload
   - Weaviate: Horizontal scaling for vector operations
   - PostgreSQL: Vertical scaling or read replicas for transactional queries
   - Redis: Cluster mode for distributed caching

3. **Feature Richness**: Each database provides specialized features
   - Weaviate: Hierarchical memory, semantic clustering, advanced RAG
   - PostgreSQL: Complex joins, transactions, referential integrity
   - Redis: Pub/sub, sorted sets, atomic operations

4. **Data Integrity**: Strong guarantees where needed
   - PostgreSQL: ACID for critical transactional data
   - On-Chain: Immutable, cryptographically-verified financial records

### Negative

1. **Operational Complexity**: Managing multiple databases requires:
   - Multiple connection pools
   - Different backup strategies
   - Monitoring multiple systems
   - More complex deployment (Docker Compose handles this)

2. **Data Consistency**: Cross-database consistency requires careful design
   - Solution: Use event-driven patterns or eventual consistency where appropriate
   - Critical data (campaigns, approvals) stays in PostgreSQL with ACID guarantees

3. **Learning Curve**: Team must understand multiple database systems
   - Mitigation: Clear documentation and examples in `docs/`

4. **Cost**: Multiple database instances (mitigated by Docker Compose for development)

### Neutral

- **Development Setup**: Docker Compose simplifies local development with all databases
- **Testing**: Test containers can spin up all databases for integration tests
- **Migration Path**: Each database can be migrated independently

---

## Implementation Notes

### Data Velocity & Integrity Matrix

| Data Type | Velocity | Integrity | Database | Rationale |
|-----------|----------|-----------|----------|-----------|
| Agent Memories | Medium | Semantic | Weaviate | Requires semantic search and RAG |
| Persona Definitions | Low | Semantic | Weaviate | Long-term consistency via RAG |
| Campaigns | Low | High (ACID) | PostgreSQL | Transactional integrity required |
| Approvals | Low | High (ACID) | PostgreSQL | Audit trail and compliance |
| Audit Logs | Medium | High (ACID) | PostgreSQL | Immutable audit records |
| Task Queues | High | Medium | Redis | Sub-millisecond access, eventual consistency OK |
| Rate Limiting | High | Low | Redis | Ephemeral, fast access required |
| Conversation History | High | Low | Redis | Short-term (1 hour), fast access |
| Financial Transactions | Low | Maximum | On-Chain | Immutable, cryptographically-verified |

### Connection Management

- **PostgreSQL**: Connection pooling via SQLAlchemy
- **Weaviate**: Client connection with retry logic
- **Redis**: Connection pool for high-throughput operations

### Migration Strategy

- **PostgreSQL**: Alembic for schema migrations
- **Weaviate**: Schema versioning via class definitions
- **Redis**: No schema migrations (key-value store)

---

## References

- **Spec-Driven Alignment**: This decision aligns with `specs/_meta.md` Database Architecture section
- **Research**: Based on Task 1 research findings in `research/submission_report_feb4_task_1.md`
- **Implementation**: See `docker-compose.yml` for database service definitions
- **Documentation**: See `docs/DOCKER.md` for database setup instructions

---

## Related ADRs

- None (this is the first ADR)

---

**Decision Record Template**: Based on [adr.github.io](https://adr.github.io/) format.
