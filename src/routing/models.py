from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Capability(str, Enum):
    KNOWLEDGE = "knowledge"
    MARKET_DATA = "market_data"
    COMPANY_ANALYSIS = "company_analysis"
    SECURITY_ANALYSIS = "security_analysis"
    SECURITY_COMPARISON = "security_comparison"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    DIVIDEND_ANALYSIS = "dividend_analysis"
    BOND_ANALYSIS = "bond_analysis"
    FINANCIAL_NEWS = "financial_news"
    WEB_RESEARCH = "web_research"
    CLARIFICATION = "clarification"


class EntityKind(str, Enum):
    ISSUER = "issuer"
    SECURITY = "security"
    INDEX = "index"
    CURRENCY = "currency"
    FUND = "fund"


class Freshness(str, Enum):
    STATIC = "static"
    RECENT = "recent"
    REALTIME = "realtime"


class Message(BaseModel):
    role: str
    content: str


class EntityReference(BaseModel):
    kind: EntityKind
    canonical_id: str
    symbol: str | None = None
    market: str | None = None
    display_name: str
    confidence: float = Field(ge=0, le=1)


class WorkflowState(BaseModel):
    workflow_id: str
    workflow_type: str
    state: str
    current_step: str
    collected_inputs: dict[str, object] = Field(default_factory=dict)
    pending_question: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    expires_at: str | None = None


class FinancialContext(BaseModel):
    user_id: str
    message: str
    recent_messages: list[Message] = Field(default_factory=list)
    conversation_summary: str | None = None
    current_capabilities: list[Capability] = Field(default_factory=list)
    active_workflow: WorkflowState | None = None
    known_entities: list[EntityReference] = Field(default_factory=list)
    conversation_id: str | None = None


class RouteCandidate(BaseModel):
    capability: Capability
    confidence: float = Field(ge=0, le=1)


class RouteDecision(BaseModel):
    capabilities: list[Capability] = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    freshness: Freshness = Freshness.STATIC
    requires_market_data: bool = False
    requires_news_search: bool = False
    requires_financial_statements: bool = False
    entities: list[EntityReference] = Field(default_factory=list)
    reasoning_summary: str = ""


class ExecutionRequirements(BaseModel):
    freshness: Freshness
    requires_market_data: bool = False
    requires_financial_filings: bool = False
    requires_news: bool = False
    requires_web_research: bool = False


class ExecutionPlan(BaseModel):
    capabilities: list[Capability] = Field(min_length=1)
    entities: list[EntityReference] = Field(default_factory=list)
    freshness: Freshness
    tools: list[str] = Field(default_factory=list)
    workflow: WorkflowState | None = None
    model_tier: str

    @field_validator("model_tier")
    @classmethod
    def validate_model_tier(cls, value: str) -> str:
        if value not in {"cheap", "medium", "strong"}:
            raise ValueError("model_tier must be cheap, medium, or strong")
        return value


class ExecutionNode(BaseModel):
    node_id: str
    kind: str
    operation: str
    depends_on: list[str] = Field(default_factory=list)
    required: bool = True
    inputs: list[str] = Field(default_factory=list)


class ExecutionGraph(BaseModel):
    nodes: list[ExecutionNode] = Field(min_length=1)
