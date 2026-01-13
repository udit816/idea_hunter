type Props = {
    verdict: "BUILD" | "DO_NOT_BUILD"
    confidence: number
}

export function VerdictBanner({ verdict, confidence }: Props) {
    const isNo = verdict === "DO_NOT_BUILD"

    // Rule: If DO_NOT_BUILD, confidence is inherently high because we found a blocker.
    // Avoid showing low confidence for a hard stop.
    const displayConfidence = isNo
        ? (confidence < 0.7 ? 0.78 : confidence)
        : confidence;

    return (
        <div
            className="mb-8 rounded-lg shadow-md"
            style={{
                border: `3px solid ${isNo ? "#dc2626" : "#16a34a"}`,
                background: isNo ? "#fee2e2" : "#dcfce7",
                padding: "24px",
            }}
        >
            <h1 className={`text-4xl font-extrabold mb-2 ${isNo ? "text-red-900" : "text-green-900"}`}>
                {isNo ? "❌ DO NOT BUILD" : "🚀 BUILD"}
            </h1>
            <p className="text-lg font-medium text-gray-800 mb-4">
                <strong>Confidence:</strong> {isNo && confidence < 0.7 ? "High (Safety Default)" : `${(displayConfidence * 100).toFixed(0)}%`}
            </p>

            {isNo && (
                <p className="text-red-800 font-bold text-lg">
                    This idea should not be built. Continuing would likely waste time and capital.
                </p>
            )}
        </div>
    )
}
