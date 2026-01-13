import { Card } from "../ui/Card";

export function KillSwitchSection({ killSwitch }: { killSwitch: any }) {
    if (!killSwitch) return null;

    const isNo = killSwitch.verdict === "DO_NOT_BUILD";

    let failures: string[] = [];
    try {
        const parsed = JSON.parse(killSwitch.failed_criteria || "[]");
        failures = Array.isArray(parsed) ? parsed : [parsed];
    } catch (e) {
        // Fallback for raw strings or legacy data
        if (killSwitch.failed_criteria) {
            failures = [killSwitch.failed_criteria];
        }
    }

    const mapFailure = (f: string) => {
        if (f === "system_error" || f === "insufficient_confident_evidence") {
            return {
                label: "Safety Threshold Not Met",
                desc: "The system could not reach a safe, high-confidence decision due to uncertainty and risk signals. By design, the engine defaults to DO NOT BUILD."
            }
        }
        return { label: f, desc: null }
    }

    return (
        <section className="mb-8">
            <Card className="p-8 border-l-4 border-l-gray-900 shadow-sm">
                <h3 className="text-xl font-bold mb-4 text-gray-900 border-b pb-2">🚨 Kill-Switch Analysis</h3>
                <p className="text-lg font-medium mb-6 text-gray-800 leading-relaxed">{killSwitch.primary_reason}</p>

                {isNo && (
                    <div className="bg-red-50 p-6 rounded-lg border border-red-100 mb-6">
                        <h4 className="font-bold text-red-900 uppercase text-xs tracking-wider mb-4">Critical Failures</h4>
                        <ul className="space-y-3">
                            {failures.map((r: string, i: number) => {
                                const { label, desc } = mapFailure(r);
                                return (
                                    <li key={i} className="flex flex-col">
                                        <span className="font-bold text-red-800">• {label}</span>
                                        {desc && <span className="text-red-700 text-sm mt-1 ml-3">{desc}</span>}
                                    </li>
                                )
                            })}
                        </ul>
                    </div>
                )}
                <div className="p-4 bg-gray-50 rounded-md border border-gray-200">
                    <strong className="text-gray-900 block mb-1">Recommendation:</strong>
                    <p className="text-gray-700">{killSwitch.recommendation}</p>
                </div>
            </Card>
        </section>
    )
}
