from typing import List, Dict
from .state import EvidenceSignal, PainCluster

def calculate_confidence(
    evidence_signals: List[Dict], # Passed as dicts from Orchestrator or objects
    pain_clusters: List[Dict],
    all_seeds: List[str],
    valid_competitor_count: int = 0
) -> Dict:
    """
    Calculates decision confidence based on:
    1. Seed Agreement (Convergence across independent searches)
    2. Recurrence (Volume of evidence)
    3. Severity (Crit/High pains detected)
    
    Returns:
    {
        "score": 0-100,
        "band": "High" | "Medium" | "Low",
        "breakdown": { ... },
        "safety_override": bool
    }
    """
    
    if not all_seeds:
        return {
            "score": 0, "band": "Low", 
            "breakdown": {"agreement": 0, "recurrence": 0, "severity":0}, 
            "safety_override": False
        }

    # 1. Seed Agreement (50%)
    # Count how many unique seeds contributed to at least one evidence signal
    active_seeds = set()
    for signal in evidence_signals:
        # Signals might store seeds in metadata
        meta = signal.get("metadata", {})
        seeds = meta.get("source_seeds", [])
        active_seeds.update(seeds)
    
    # Agreement Ratio = Matching Seeds / Total Seeds
    # (Cap total at len(all_seeds) in case of drift, though active should be subset)
    agreement_count = len(active_seeds.intersection(set(all_seeds)))
    agreement_ratio = agreement_count / len(all_seeds) if all_seeds else 0
    
    score_agreement = agreement_ratio * 100

    # 2. Recurrence Score (30%)
    # Simple heuristic: >10 active signals = 100%, linear scale below
    # (Assuming we have filtered for relevance roughly)
    total_evidence = len(evidence_signals)
    score_recurrence = min(total_evidence * 10, 100)

    # 3. Severity Score (20%)
    # Based on Pain Clusters
    severity_map = {"critical": 100, "high": 75, "medium": 50, "low": 25}
    current_max_severity = 0
    for cluster in pain_clusters:
        sev = cluster.get("severity", "low").lower()
        processed = severity_map.get(sev, 25)
        if processed > current_max_severity:
            current_max_severity = processed
    
    score_severity = current_max_severity

    # Composite Calculation
    raw_confidence = (
        (0.5 * score_agreement) +
        (0.3 * score_recurrence) +
        (0.2 * score_severity)
    )

    # 4. Safety Overrides
    # Check for "Trust Collapse" or "Fraud" or "Legal" keywords in HIGH severity clusters
    safety_triggered = False
    safety_triggers = ["trust", "fraud", "legal", "compliance", "scam", "lawsuit", "unauthorized"]
    
    for cluster in pain_clusters:
        if cluster.get("severity") in ["critical", "high"]:
            desc = (cluster.get("description", "") + " " + cluster.get("cluster_name", "")).lower()
            if any(t in desc for t in safety_triggers):
                safety_triggered = True
                break
    
    final_score = raw_confidence
    safety_label = False
    
    # 5. Market Grounding Cap (Precision Upgrade)
    insufficient_grounding = False
    if valid_competitor_count < 3:
        # If we couldn't find 3 valid competitors, confidence is questionable.
        final_score = min(final_score, 60.0)
        insufficient_grounding = True

    # Override Logic
    if safety_triggered:
        final_score = max(final_score, 70) # Floor at 70 (High) for Safety Defaults
        safety_label = True

    # Override Logic
    if safety_triggered:
        final_score = max(final_score, 70) # Floor at 70 (High) for Safety Defaults
        safety_label = True
    
    # Bands
    if final_score >= 85: band = "Very High"
    elif final_score >= 70: band = "High"
    elif final_score >= 50: band = "Medium"
    else: band = "Low"

    # Explanation Logic
    explanation = ""
    override_reason = None

    if safety_triggered:
        override_reason = "Critical risk signals detected (trust/legal/fraud)."
        explanation = "The system identified consistent risk signals requiring a conservative decision."
    elif final_score >= 85:
        explanation = "Strong, consistent signals across multiple independent sources."
    elif final_score >= 70:
        explanation = "Clear direction with limited uncertainty in the available data."
    elif final_score >= 50:
        explanation = "Mixed signals detected — caution and further validation advised."
    else:
        explanation = "Insufficient evidence found for a reliable decision."

    if insufficient_grounding:
        explanation += " ⚠ The system could not identify enough comparable products operating in the same category. Results may be incomplete."

    return {
        "score": round(final_score, 1),
        "band": band.replace(" (Safety Default)", ""), # Clean band name
        "explanation": explanation,
        "breakdown": {
            "seed_agreement_ratio": round(agreement_ratio, 2),
            "total_seeds": len(all_seeds),
            "agreeing_seeds": agreement_count,
            "evidence_count": total_evidence,
            "max_severity_score": score_severity
        },
        "safety_override": safety_label,
        "safety_override_reason": override_reason
    }
