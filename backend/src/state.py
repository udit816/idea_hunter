from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum

# --- ENUMS (For Logic Control) ---
class ResearchStage(str, Enum):
    INIT = "init"
    HUNTING = "hunting"
    HUNTING_REVIEW = "hunting_review"  # HITL Checkpoint
    MINING = "mining"
    SYNTHESIZING = "synthesizing"
    JUSTIFYING = "justifying"
    ARCHITECTING = "architecting"
    COMPLETED = "completed"

# --- SUB-MODELS (Data Structures) ---
class Competitor(BaseModel):
    name: str
    url: str
    pricing_page: Optional[str] = None
    is_relevant: bool = True  # User can toggle this to False
    metadata: Optional[Dict] = Field(default_factory=dict) # For storing seeds etc.

class EvidenceSignal(BaseModel):
    source_type: str
    platform: str
    pain_theme: str
    pain_description: str
    example_evidence: str
    impact: str  # trial_blocker, conversion_blocker, churn, trust_collapse
    severity: str  # low, medium, high, critical
    confidence: float
    metadata: Optional[Dict] = Field(default_factory=dict) # For storing source_seed etc.

class ValidatedIdea(BaseModel):
    description: str
    target_keyword: str
    search_volume: int
    cpc: float
    difficulty: int
    opportunity_score: float  # Calculated metric

# --- MASTER STATE (The "Context") ---

class FeatureDecision(BaseModel):
    feature_id: str
    feature_name: str
    solves_pain_clusters: List[str]
    user_problem: str
    why_existing_solutions_fail: str
    mvp_priority: bool
    expected_user_outcome: str
    success_metric: str
    if_we_dont_build: str
    complexity: str

class KillSwitchVerdict(BaseModel):
    verdict: str  # BUILD | DO_NOT_BUILD
    confidence: float
    primary_reason: str
    supporting_reasons: List[str]
    failed_criteria: List[str]
    what_would_change_verdict: List[str]
    recommendation: str

class ProductOverview(BaseModel):
    name: str
    one_liner: str
    target_user: str
    problem_statement: str

class MVPFeature(BaseModel):
    feature_id: str
    name: str
    description: str
    user_pain_addressed: str
    success_metric: str
    complexity: str

class PRD(BaseModel):
    product_overview: ProductOverview
    problem_statement: str

class Risk(BaseModel):
    risk: str
    impact: str
    mitigation: str

class LaunchScope(BaseModel):
    included: List[str]
    excluded: List[str]

class SuccessDefinition(BaseModel):
    leading_indicators: List[str]
    lagging_indicators: List[str]

class PRD(BaseModel):
    product_overview: ProductOverview
    goals: List[str]
    non_goals: List[str]
    mvp_features: List[MVPFeature]
    user_flow: List[str]
    risks_and_unknowns: List[Risk]
    launch_scope: LaunchScope
    success_definition: SuccessDefinition

class ProductSpec(BaseModel):
    # Legacy fields (kept for compatibility or derived)
    mvp_name: str = ""
    tagline: str = ""
    core_features: List[str] = []
    user_stories: List[str] = []
    marketing_hook: str = ""
    
    # New Structured Data
    prd: Optional[PRD] = None
    feature_roadmap: List[FeatureDecision] = Field(default_factory=list)
    tech_stack_recommendation: List[str] = Field(default_factory=list)

class ProblemStatement(BaseModel):
    who: str
    problem: str
    why_now: str

class DiscoveryData(BaseModel):
    interpreted_domain: str
    problem_statements: List[ProblemStatement]

class ImpactSummary(BaseModel):
    trial_blocker: bool
    conversion_blocker: bool
    trust_collapse: bool

class PainCluster(BaseModel):
    cluster_id: str
    cluster_name: str
    description: str
    affected_personas: List[str]
    evidence_count: int
    platforms_affected: List[str]
    impact_summary: ImpactSummary
    severity: str
    why_users_get_angry: str
    representative_quotes: List[str]

class ProductIntent(BaseModel):
    primary_problem: str
    non_negotiable_user_expectation: str
    current_market_failure: str
    opportunity_statement: str

class ResearchState(BaseModel):
    # Inputs
    project_id: str
    niche: str
    country_code: str = "in"
    
    # Flow Control
    current_stage: ResearchStage = ResearchStage.INIT
    logs: List[str] = Field(default_factory=list) # Audit trail of agent actions
    
    # Data Accumulation
    discovery_data: Optional[DiscoveryData] = None
    competitors: List[Competitor] = Field(default_factory=list)
    evidence_signals: List[EvidenceSignal] = Field(default_factory=list)
    pain_clusters: List[PainCluster] = Field(default_factory=list)
    product_intent: Optional[ProductIntent] = None
    feature_decisions: List[FeatureDecision] = Field(default_factory=list)
    kill_switch: Optional[KillSwitchVerdict] = None
    final_ideas: List[ValidatedIdea] = Field(default_factory=list)
    product_spec: Optional[ProductSpec] = None
    prd: Optional[Dict] = None

    # Human Feedback Slot
    user_feedback: Optional[str] = None

    def add_log(self, message: str):
        self.logs.append(message)