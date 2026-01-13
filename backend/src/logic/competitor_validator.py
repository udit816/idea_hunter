from typing import Set

def extract_core_intent(text: str) -> Set[str]:
    keywords = [
        "training", "simulation", "coaching", "analysis", "feedback", 
        "learning", "sales", "negotiation", "calls", "automation", 
        "platform", "dashboard", "api", "integration", "management",
        "CRM", "database", "analytics", "tracking", "monitoring"
    ]
    
    return {kw for kw in keywords if kw in text.lower()}

def extract_competitor_intent(description: str) -> Set[str]:
    keywords = [
        "training", "coaching", "analytics", "monitoring", "security", 
        "fraud", "advertising", "compliance", "sales", "marketing", 
        "calls", "automation", "platform", "management", "CRM", "database"
    ]
    
    return {kw for kw in keywords if kw in description.lower()}

def intent_overlap_score(user_intent: Set[str], competitor_intent: Set[str]) -> float:
    if not user_intent or not competitor_intent:
        return 0.0
    return len(user_intent & competitor_intent) / len(user_intent)

def is_wrong_competitor(user_intent: Set[str], competitor_intent: Set[str]) -> bool:
    overlap = intent_overlap_score(user_intent, competitor_intent)
    # Threshold < 0.4 implies invalid
    return overlap < 0.4
