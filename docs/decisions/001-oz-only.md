# ADR-001: OpenZeppelin Only

## Status
Accepted

## Context
The project requires audited components for access control and security primitives.

## Decision
Use only OpenZeppelin Cairo v3.0.0 for security-related patterns and components.

## Consequences
- Improves security by relying on audited code.
- Limits flexibility if a required pattern is not available.
- May require waiting for new OZ releases.
