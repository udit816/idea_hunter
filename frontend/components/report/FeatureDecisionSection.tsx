import { Card } from "../ui/Card";
import { Badge } from "../ui/Badge";

type FeatureDecision = {
    feature_name: string;
    mvp_priority: boolean;
    success_metric: string;
    complexity: string;
}

type Props = {
    decisions: FeatureDecision[] | null
}

export function FeatureDecisionSection({ decisions }: Props) {
    if (!decisions || decisions.length === 0) {
        return (
            <section className="mb-12">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Feature Justification</h2>
                <Card className="bg-gray-50 border-gray-200">
                    <div className="text-center py-6">
                        <p className="text-gray-500 font-medium text-lg">No features proposed.</p>
                        <div className="mt-2 text-left bg-red-50 p-4 rounded-md inline-block max-w-lg border border-red-100">
                            <p className="font-bold text-red-800 text-sm mb-1">Reason:</p>
                            <p className="text-red-700 text-sm leading-relaxed">
                                Core trust, legal, and financial risks cannot be resolved through an MVP.
                                Building features would not meaningfully reduce user risk or improve outcomes.
                            </p>
                        </div>
                    </div>
                </Card>
            </section>
        )
    }

    return (
        <section className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Feature Justification</h2>
            <div className="overflow-x-auto">
                <table className="min-w-full bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Feature</th>
                            <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">MVP?</th>
                            <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Metric</th>
                            <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Complexity</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {decisions.map((d, i) => (
                            <tr key={i}>
                                <td className="px-6 py-4 text-sm font-medium text-gray-900">{d.feature_name}</td>
                                <td className="px-6 py-4 text-sm">
                                    <Badge
                                        label={d.mvp_priority ? "MUST HAVE" : "LATER"}
                                        variant={d.mvp_priority ? "error" : "default"}
                                    />
                                </td>
                                <td className="px-6 py-4 text-sm text-gray-500">{d.success_metric}</td>
                                <td className="px-6 py-4 text-sm text-gray-500">{d.complexity}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </section>
    );
}
