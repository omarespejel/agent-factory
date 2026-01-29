# ADR-002: Perplexity as Production-Grade Auditor

## Status
Accepted

## Context
We need a reasoning-based security auditor to complement static analysis.

## Decision
Use Perplexity with `sonar-reasoning-pro` as the primary security auditor.

## Responsibilities
- Research production-grade patterns before implementation
- Validate library choices against known audits
- Provide unstuck guidance with cited sources
- Review crypto-critical code sections

## Query Triggers
- Before each module implementation
- When build fails 3x on the same error
- When the same test fails 3x
- When uncertain about approach
- Before any crypto implementation

## Consequences
- Adds latency to development loop (acceptable for security)
- Requires Perplexity API credits
- Produces documented, traceable security decisions
