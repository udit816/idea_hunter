export function PRDSection({ prd }: { prd: any }) {
    if (!prd) return null;

    return (
        <section className="bg-white p-6 rounded shadow border-l-4 border-blue-500 mb-6">
            <h3 className="text-2xl font-bold mb-4 text-blue-900">📄 Product Requirements Document</h3>

            <div className="space-y-6">
                <div>
                    <h4 className="font-bold uppercase text-xs text-gray-500 mb-2">Problem Statement</h4>
                    <p className="italic text-gray-800">{prd.product_overview?.problem_statement}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h4 className="font-bold uppercase text-xs text-green-700 mb-2">Goals</h4>
                        <ul className="list-disc ml-5 space-y-1 text-sm">
                            {prd.goals?.map((g: string, i: number) => <li key={i}>{g}</li>)}
                        </ul>
                    </div>
                    <div>
                        <h4 className="font-bold uppercase text-xs text-red-700 mb-2">Non-Goals</h4>
                        <ul className="list-disc ml-5 space-y-1 text-sm">
                            {prd.non_goals?.map((g: string, i: number) => <li key={i}>{g}</li>)}
                        </ul>
                    </div>
                </div>

                <div>
                    <h4 className="font-bold uppercase text-xs text-gray-500 mb-2">MVP Features</h4>
                    <div className="space-y-3">
                        {prd.mvp_features?.map((f: any, i: number) => (
                            <div key={i} className="bg-gray-50 p-3 rounded">
                                <strong className="block text-gray-900">{f.name}</strong>
                                <span className="text-sm text-gray-600">{f.description}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    )
}
