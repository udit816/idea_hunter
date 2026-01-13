"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from "@/components/layout/AppShell";
import { ReportHeader } from "@/components/report/ReportHeader";
import { EvidenceSection } from "@/components/report/EvidenceSection";
import { PainClusterSection } from "@/components/report/PainClusterSection";
import { FeatureDecisionSection } from "@/components/report/FeatureDecisionSection";
import { KillSwitchSection } from "@/components/report/KillSwitchSection";
import { PRDSection } from "@/components/report/PRDSection";

import { GatedSection } from "@/components/common/GatedSection";

export default function ReportPage({ params }: { params: { id: string } }) {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [userTier, setUserTier] = useState<"FREE" | "PRO">("FREE");

    useEffect(() => {
        fetch(`http://localhost:8000/api/report/${params.id}`)
            .then(res => res.json())
            .then(data => {
                setData(data);
                setLoading(false);
            })
            .catch(e => console.error(e));
    }, [params.id]);

    if (loading) return <div className="p-8 text-center text-gray-500">Loading Report...</div>;
    if (!data) return <div className="p-8 text-center text-red-500">Error loading report.</div>;

    const { analysis, evidence, clusters, feature_decisions, kill_switch, prd } = data;
    const verdict = kill_switch?.verdict === "DO_NOT_BUILD" ? "DO_NOT_BUILD" : "BUILD";

    const isPro = userTier === "PRO";

    const isHighConfidenceReject = verdict === "DO_NOT_BUILD" && analysis.confidence >= 0.7;
    const isKillSwitchLocked = !isPro && !isHighConfidenceReject;

    return (
        <AppShell>
            <div className="mb-4 flex justify-between items-center">
                <Link href="/dashboard" className="text-gray-500 hover:text-gray-900">← Back to Dashboard</Link>

                {/* Debug Toggle for Demo */}
                <button
                    onClick={() => setUserTier(isPro ? "FREE" : "PRO")}
                    className="text-xs bg-slate-100 px-2 py-1 rounded border hover:bg-slate-200"
                >
                    Simulate {isPro ? "Free User" : "Pro Upgrade"}
                </button>
            </div>

            <ReportHeader analysis={analysis} />

            <GatedSection
                isLocked={isKillSwitchLocked}
                title="Upgrade to Pro to see the Kill Switch Analysis"
                onUnlock={() => setUserTier("PRO")}
            >
                <KillSwitchSection killSwitch={kill_switch} />
            </GatedSection>

            {verdict === "BUILD" && (
                <GatedSection
                    isLocked={!isPro}
                    title="Upgrade to Pro to see the Product Requirements Document (PRD)"
                    onUnlock={() => setUserTier("PRO")}
                >
                    <PRDSection prd={prd} />
                </GatedSection>
            )}

            <GatedSection
                isLocked={!isPro}
                title="Upgrade to Pro to see Real User Quotes & Evidence"
                onUnlock={() => setUserTier("PRO")}
            >
                <EvidenceSection evidence={evidence} />
            </GatedSection>

            <GatedSection
                isLocked={!isPro}
                title="Upgrade to Pro to see Detailed Pain Clusters"
                onUnlock={() => setUserTier("PRO")}
            >
                <PainClusterSection clusters={clusters} />
            </GatedSection>

            <GatedSection
                isLocked={!isPro}
                title="Upgrade to Pro to see Feature Justifications"
                onUnlock={() => setUserTier("PRO")}
            >
                <FeatureDecisionSection decisions={feature_decisions} />
            </GatedSection>
        </AppShell>
    );
}
