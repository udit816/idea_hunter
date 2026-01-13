export interface Analysis {
    id: string;
    user_id: number;
    raw_input: string;
    status: string;
    created_at: string;
    verdict?: "BUILD" | "DO_NOT_BUILD";
}

export interface Report {
    analysis_id: string;
    kill_switch: {
        verdict: "BUILD" | "DO_NOT_BUILD";
        confidence: number;
        primary_reason: string;
        failed_criteria?: string; // JSON string
        recommendation: string;
    };
    evidence: Array<{
        source_type: string;
        description: string;
        platform?: string;
        impact?: string;
    }>;
    clusters: Array<{
        cluster_name: string;
        severity: string;
        description: string;
        why_users_get_angry?: string;
    }>;
    feature_decisions: Array<{
        feature_name: string;
        mvp_priority: boolean;
        success_metric: string;
        complexity: string;
    }>;
    prd?: any;
}
