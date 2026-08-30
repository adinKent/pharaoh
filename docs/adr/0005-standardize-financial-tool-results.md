# Standardize financial tool results

All external financial data tools will return a common typed result containing the data, source, retrieval time, effective time, quality, stale status, and error information. This keeps provenance and freshness visible to the Planner and Answer Generator and prevents provider-specific response formats from leaking into routing or answer generation.

## Consequences

- The Planner can enforce freshness and distinguish critical from optional missing data.
- Answers must identify stale or incomplete data instead of silently filling gaps.
- New data providers must implement the shared result contract.
