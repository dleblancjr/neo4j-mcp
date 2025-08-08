# AI Coding Guidelines (Actionable Summary)

Optimized reference for AI assistant contributions.

## Core Principles

*   Think first: plan, compare approaches, justify recommendation, consider maintainability & scalability.
*   Keep it simple (KISS): prefer clear, minimal solutions; avoid premature optimization & unnecessary abstraction.
*   Respect context limits: warn early if context may be incomplete.
*   Never modify files or tests without explicit permission.

## Clean Code Standards

*   Descriptive, self-documenting names.
    *   Variables/functions: snake\_case
    *   Classes: PascalCase
    *   Constants: UPPER\_SNAKE\_CASE
*   Single responsibility per function; keep concise (~<20 lines when reasonable).
*   Prefer ≤3 parameters; bundle extras (dict/dataclass).
*   Remove dead code/unused imports; only comment non-trivial logic.
*   Favor pure functions (no side effects) where possible.

## Error Handling

*   Never silence errors; validate inputs early (fail fast).
*   Log with contextual detail; return specific, user-friendly messages.
*   Avoid broad generic catches unless rewrapping with context.
*   Provide recovery guidance when applicable.

## Python Practices

*   Type hints for all params & returns.
*   Use f-strings; avoid mutable default args.
*   Use context managers for resources (files, sessions, locks).
*   Follow PEP 8; use list/dict comprehensions for simple transforms.

## Quality & Structure

*   DRY: extract shared logic; centralize repeated literals as constants.
*   Tests must cover new/changed logic; preserve test intent.
*   Explicitly consider and handle edge cases.
*   Organize by feature/domain; keep files focused and not excessively large.

## Dependencies

*   Minimize; select well-maintained, popular, stable versions.
*   Justify each dependency’s necessity.

## Avoid

*   Over-engineering, speculative features, unnecessary abstractions.
*   Long parameter lists, deep nesting, god objects, magic values, copy‑paste.
*   Broad excepts w/o added context, swallowing errors, assertion-based input validation.

## Communication

*   Explain architectural decisions and trade-offs.
*   Flag technical debt/risks proactively.
*   Ask for clarification on ambiguity.
*   Suggest improvements when evident.

## Pre-Submission Checklist

Before submitting code, ensure:

*   Simplicity & clarity; single responsibility.
*   Input validation & robust error handling present.
*   No debug prints/log spam; meaningful logging only.
*   Edge cases addressed (empty, large, invalid, concurrency, timeouts).
*   DRY upheld; no duplicated logic.
*   Tests updated & passing.
*   Dependencies necessary & current.

## Project Reminder

Check (if present) TECHNICAL\_REQUIREMENTS.md / REQUIREMENTS.md for:

*   Framework / database patterns
*   API & protocol constraints
*   Security & performance guidelines
*   Deployment nuances

## Guiding Heuristic

Prioritize readability, maintainability, and explicit correctness over cleverness. When in doubt: simplify, document intent briefly, and proceed with the least surprising solution.