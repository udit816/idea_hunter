export const IMPACT_INTERPRETATIONS: Record<string, { label: string; description: string }> = {
    // Core tags
    trial_blocker: {
        label: "Prevents trial",
        description: "Users are unwilling or unable to even try the product due to fear, friction, or lack of trust."
    },
    conversion_blocker: {
        label: "Prevents payment",
        description: "Users hesitate or refuse to pay, even if they explore the product."
    },
    churn: {
        label: "Causes abandonment",
        description: "Users disengage or leave shortly after initial use."
    },
    trust_collapse: {
        label: "Destroys trust",
        description: "The ecosystem is perceived as unsafe, deceptive, or unreliable."
    },
    pricing_resentment: {
        label: "Creates pricing resentment",
        description: "Users feel overcharged, misled, or financially exploited."
    },
    legal_or_financial_risk: {
        label: "Creates legal or financial risk",
        description: "Users face potential legal exposure or unexpected financial consequences."
    },

    // Potential variations / missed tags
    friction: {
        label: "High Friction",
        description: "Users struggle to complete basic tasks, reducing adoption."
    },
    trust_safety: {
        label: "Safety Risk",
        description: "Users feel unsafe or exposed to fraud."
    },
    missing_capability: {
        label: "Critical Gap",
        description: "Comparison with competitors reveals missing baseline features."
    },

    // Fallback
    unknown: {
        label: "Creates friction",
        description: "This issue negatively impacts user experience and adoption."
    }
}

export function getAngryMessage(cluster: any): string {
    if (cluster.why_users_get_angry && cluster.why_users_get_angry.length > 10) {
        return cluster.why_users_get_angry;
    }

    // Fallback logic based on text analysis
    const text = (cluster.cluster_name + " " + cluster.description).toLowerCase();

    if (text.includes("fraud") || text.includes("scam") || text.includes("trust")) {
        return "Users feel betrayed and unsafe, perceiving the platform as complicit in fraud.";
    }
    if (text.includes("price") || text.includes("cost") || text.includes("pay") || text.includes("charge")) {
        return "Users feel resentful about hidden costs and value perception, leading to chargebacks.";
    }
    if (text.includes("bug") || text.includes("broken") || text.includes("slow")) {
        return "Users feel frustrated by unreliability, leading to immediate abandonment.";
    }
    if (text.includes("legal") || text.includes("risk") || text.includes("compliance")) {
        return "Users feel exposed to unnecessary legal or financial liability.";
    }

    return "Users feel misled and exposed to risk after committing, with no clear support when things go wrong.";
}
