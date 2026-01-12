from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum

# --- ENUMS (For Logic Control) ---
class ResearchStage(str, Enum):
    INIT = "init"
    HUNTING = "hunting"
    HUNTING_REVIEW = "hunting_review"  # HITL Checkpoint
    MINING = "mining"
    VALIDATING = "validating"
    ARCHITECTING = "architecting"
    COMPLETED = "completed"

# --- SUB-MODELS (Data Structures) ---
class Competitor(BaseModel):
    name: str
    url: str
    pricing_page: Optional[str] = None
    is_relevant: bool = True  # User can toggle this to False

class PainPoint(BaseModel):
    source: str  # e.g., "Reddit", "G2"
    quote: str
    pain_category: str  # e.g., "Pricing", "UX", "Missing Feature"
    sentiment_score: float  # -1.0 to 1.0
    frequency: int = 1

class ValidatedIdea(BaseModel):
    description: str
    target_keyword: str
    search_volume: int
    cpc: float
    difficulty: int
    opportunity_score: float  # Calculated metric

# --- MASTER STATE (The "Context") ---

class ProductSpec(BaseModel):
    mvp_name: str
    tagline: str
    core_features: List[str]
    tech_stack_recommendation: List[str]
    user_stories: List[str]
    marketing_hook: str

class ResearchState(BaseModel):
    # Inputs
    project_id: str
    niche: str
    country_code: str = "in"
    
    # Flow Control
    current_stage: ResearchStage = ResearchStage.INIT
    logs: List[str] = Field(default_factory=list) # Audit trail of agent actions
    
    # Data Accumulation
    competitors: List[Competitor] = Field(default_factory=list)
    pain_points: List[PainPoint] = Field(default_factory=list)
    final_ideas: List[ValidatedIdea] = Field(default_factory=list)
    product_specs: Optional[ProductSpec] = None

    # Human Feedback Slot
    user_feedback: Optional[str] = None

    def add_log(self, message: str):
        self.logs.append(message)