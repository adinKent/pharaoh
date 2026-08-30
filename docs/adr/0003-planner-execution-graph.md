# Planner produces an execution graph

The Planner will convert one or more capabilities into an execution graph rather than a flat list of tools. Independent data requests may run in parallel, duplicate requests must be deduplicated, and analysis steps must declare their required inputs. This makes multi-capability requests predictable and lets the system report partial results when a non-critical source fails.

## Consequences

- Tool results need provenance, effective time, retrieval time, quality, and error information.
- The executor must distinguish critical missing data from optional missing data.
- The answer generator must not fill missing financial values by inference.
