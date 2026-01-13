"use client";

import Link from 'next/link';
import { AppShell } from "@/components/layout/AppShell";
import { VerdictBanner } from "@/components/analysis/VerdictBanner";
import { EvidenceSection } from "@/components/report/EvidenceSection";
import { PainClusterSection } from "@/components/report/PainClusterSection";
import { FeatureDecisionSection } from "@/components/report/FeatureDecisionSection";
import { KillSwitchSection } from "@/components/report/KillSwitchSection";

export default function SampleReport() {
    // Static Mock Data for "Uber for Dog Walking" (Failed Idea)
    const report = {
        kill_switch: {
            verdict: "DO_NOT_BUILD",
            confidence: 0.92,
            primary_reason: "Unit Economics Collapse",
            failed_criteria: [
                "Customer Acquisition Cost > Lifetime Value",
                "Low frequency of use vs high operational drag",
                "Market saturation by generalist competitors (Rover, Wag)"
            ],
            recommendation: "Pivot to B2B: Software for existing dog walking agencies instead of a consumer marketplace."
        },
        evidence: [
            { source_type: "Reddit", description: "Walkers complain about taking 20% cut when they can just steal the client after one walk.", platform: "r/startups", impact: "high" },
            { source_type: "App Store", description: "Users hate paying booking fees for the same walker every day.", platform: "App Store", impact: "medium" },
            { source_type: "Competitor Analysis", description: "Rover and Wag have strong network effects; new entrants burn cash on ads.", platform: "G2", impact: "critical" }
        ],
        clusters: [
            { cluster_name: "Platform Leakage", severity: "CRITICAL", description: "Walkers and owners take the transaction offline immediately to save fees.", why_users_get_angry: "They feel taxed for no ongoing value." },
            { cluster_name: "Trust & Safety Costs", severity: "HIGH", description: "Insurance and vetting costs are prohibitively high for low-margin starts.", why_users_get_angry: "Safety incidents cause massive churn." }
        ],
        feature_decisions: [
            { feature_name: "GPS Tracking", mvp_priority: true, complexity: "High", success_metric: "Trust Score" },
            { feature_name: "In-app Payment", mvp_priority: true, complexity: "Medium", success_metric: "Transaction Vol" }
        ]
    };

    return (
        <AppShell>
            <div className="mb-4">
                <Link href="/" className="text-gray-500 hover:text-gray-900">← Back Home</Link>
            </div>

            <div className="mb-8 flex items-center justify-between">
                <h1 className="text-3xl font-bold font-gray-900">Sample Analysis Report</h1>
                <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded font-bold uppercase">Static Preview</span>
            </div>

            <VerdictBanner verdict="DO_NOT_BUILD" confidence={report.kill_switch.confidence} />

            <KillSwitchSection killSwitch={report.kill_switch} />

            <EvidenceSection evidence={report.evidence} />
            <PainClusterSection clusters={report.clusters} />
            <FeatureDecisionSection decisions={report.feature_decisions} />
        </AppShell>
    );
}
