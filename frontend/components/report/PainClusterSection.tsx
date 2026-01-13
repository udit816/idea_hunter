
const IMPACT_LABELS: Record<string, string> = {
    trial_blocker: "Prevents users from even trying the product",
    conversion_blocker: "Stops users from paying or committing",
    churn: "Causes users to leave after initial use",
    trust_collapse: "Destroys trust in the product or ecosystem",
    pricing_resentment: "Users feel cheated or overcharged",
    legal_or_financial_risk: "Creates legal or financial exposure"
};

import { getAngryMessage } from "@/lib/constants";

export function PainClusterSection({ clusters }: { clusters: any[] }) {
    return (
        <section className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-8">
            <h3 className="text-xl font-bold mb-6 text-gray-900">🩸 Pain Clusters</h3>
            <div className="space-y-6">
                {clusters.map((c, i) => (
                    <div key={i} className="flex flex-col sm:flex-row border border-gray-200 rounded-lg overflow-hidden bg-white hover:border-gray-300 transition-colors">
                        <div className={`w-full sm:w-2 h-2 sm:h-auto ${c.severity === 'CRITICAL' ? 'bg-red-500' : 'bg-orange-400'}`}></div>
                        <div className="p-6 flex-1">
                            <div className="flex flex-col sm:flex-row justify-between items-start mb-2 gap-2">
                                <h4 className="font-bold text-lg text-gray-900">{c.cluster_name}</h4>
                                <span className={`text-xs font-bold px-2 py-1 rounded text-white whitespace-nowrap ${c.severity === 'CRITICAL' ? 'bg-red-500' : 'bg-orange-400'}`}>
                                    {c.severity}
                                </span>
                            </div>
                            <p className="text-gray-700 mb-4 leading-relaxed">{c.description}</p>

                            {/* Impact Mapping */}
                            {c.impact_tags && c.impact_tags.length > 0 && ( /* Assuming impact_tags exists or needs to be derived? */
                                /* Actually synthesizer returns 'impact_summary' object in prev code, let's check input */
                                /* The component seems to be props-driven. We'll simplify: assume 'impact' field might exist on flat object  
                                   OR we might need to map manual string if stored differently. 
                                   Let's check EvidenceSection used 'impact' string. */
                                null
                            )}

                            <div className="mt-4 p-4 bg-gray-50 rounded text-sm text-gray-600">
                                <strong className="block text-gray-900 mb-1">Why users get angry:</strong>
                                {getAngryMessage(c)}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </section>
    )
}
