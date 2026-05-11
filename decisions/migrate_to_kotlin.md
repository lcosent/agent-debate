# Migrate primary backend from Java 17 to Kotlin

## Context

- 380kloc primary backend on Java 17 with Spring Boot.
- 22 backend engineers; 6 have Kotlin experience.
- Recent JVM perf work is upstream-stable; no GC or throughput issues.
- Two new product lines being scoped — opportunity to start them in Kotlin.
- Existing code interops cleanly (same JVM); migration can be incremental.
- No formal hiring signal that Kotlin attracts better candidates in our domain (fintech, regulated).

## What I'm trying to decide

Whether to commit to a multi-quarter migration to Kotlin (all new code in Kotlin, opportunistic file-level conversion of old code), or stay on Java and adopt newer Java idioms (records, sealed types, pattern matching) instead.

## Constraints

- Roadmap pressure on the new product lines is high.
- A full migration takes ~18 months at current capacity.
- Reverting mid-migration is operationally painful.
