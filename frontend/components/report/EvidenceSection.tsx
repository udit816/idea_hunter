import { IMPACT_INTERPRETATIONS } from "@/lib/constants";

export function EvidenceSection({ evidence }: { evidence: any[] }) {
    return (
        <section className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-8">
            <h3 className="text-xl font-bold mb-6 text-gray-900 flex items-center">
                🔎 Evidence Summary
                <span className="ml-3 bg-gray-100 text-gray-600 text-xs font-bold px-2.5 py-1 rounded-full">{evidence.length} Signals</span>
            </h3>

            <div className="grid grid-cols-1 gap-6 mb-8">
                {evidence.slice(0, 6).map((e, i) => {
                    const key = e.impact?.toLowerCase().replace(/ /g, "_") || "unknown";
                    const impact = IMPACT_INTERPRETATIONS[key] || IMPACT_INTERPRETATIONS["unknown"];

                    return (
                        <div key={i} className="flex flex-col md:flex-row gap-6 border border-gray-200 p-6 rounded-lg bg-gray-50/50 hover:bg-white transition-colors">
                            <div className="md:w-1/2">
                                <div className="font-bold text-[10px] tracking-wider text-gray-500 uppercase mb-2">
                                    {e.source_type} • {e.platform}
                                </div>
                                <p className="text-gray-900 text-base leading-relaxed font-medium">"{e.description}"</p>
                            </div>

                            <div className="md:w-1/2 bg-white md:bg-transparent rounded border md:border-0 border-gray-200 p-4 md:p-0">
                                <h4 className="text-sm font-bold text-gray-900 mb-2">Impact on users:</h4>
                                <div className="flex items-start">
                                    <span className="text-red-500 mr-2 mt-1.5 text-[6px]">●</span>
                                    <div>
                                        <span className="font-bold text-gray-900 text-sm">{impact.label}</span>
                                        <span className="text-gray-500 text-sm"> — {impact.description}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="bg-gray-900 text-white p-4 rounded-md text-sm font-medium text-center">
                What this means: These signals indicate structural trust and risk failures, not surface-level usability issues.
            </div>
        </section>
    )
}
