# Financial AI Chatbot Context

This context defines the domain language for routing and answering finance-related requests in the personal LINE chatbot.

## Request routing

**Capability**:
The user-visible financial job required to answer a request, such as market data, company analysis, or security comparison. A request may require multiple capabilities.
_Avoid_: Intent category, agent

**Workflow**:
A stateful, multi-step interaction that collects information or guides the user through a financial task. A workflow is not a capability and may be suspended when the user changes topic.
_Avoid_: Agent

**Workflow state**:
The current, explicitly named step and collected information within a workflow, including whether the workflow is active, suspended, completed, cancelled, or expired.
_Avoid_: Active workflow string

**Entity**:
A referenced financial object, such as an issuer, security, index, currency, or fund.
_Avoid_: Ticker string, symbol

**Entity reference**:
A resolved reference to an entity that includes its kind and canonical identity; an unresolved or ambiguous reference must not be treated as confirmed.
_Avoid_: Entity name, ticker

**Entity Resolver**:
The domain boundary that maps user-provided names, symbols, and aliases to canonical entity references or requests clarification when resolution is ambiguous.
_Avoid_: Router entity guessing

## Data requirements

**Freshness**:
The required recency of information for answering a request: static, recent, or realtime. Freshness is a data requirement, not a model preference.
_Avoid_: Latest, current (without a defined age)

**Static**:
Information that does not require retrieval of changing external data, such as a general definition.

**Recent**:
Information tied to a recent reporting period, event, or bounded age that must be identified in the answer.

**Realtime**:
Information expected to reflect the current market or current moment and therefore requiring an observable effective time and source.

**Execution plan**:
A validated description of the capabilities, resolved entities, freshness requirements, data requirements, and model work needed to answer a request.

**Execution graph**:
An execution plan whose steps explicitly record dependencies, allowing independent data retrieval to run in parallel and analysis to wait for required inputs.

**Compatibility layer**:
The boundary that preserves existing fixed LINE commands while delegating unmatched natural-language requests to the new financial router.
_Avoid_: Legacy mode (when referring to the boundary itself)

**Data quality**:
The trustworthiness of a tool result, including its source, effective time, retrieval time, completeness, and error state.

## Operating modes

**Personal-use mode**:
The default operating mode for the owner’s private use. Safety restrictions such as advice refusal or disclaimers are configurable rather than mandatory in this mode.
_Avoid_: Production mode, public mode

**Safety mode**:
An optional operating mode that enables configured safeguards for broader or more cautious use, including advice boundaries, refusal behavior, and disclosures.
_Avoid_: Compliance mode (unless legally defined)

Safety mode is configured at deployment scope in the initial implementation.
