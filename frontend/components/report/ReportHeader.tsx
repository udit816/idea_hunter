import { useState } from 'react';

export function ReportHeader({ analysis }: { analysis: any }) {
    const [showFraming, setShowFraming] = useState(false);

    const metadata = analysis.confidence_metadata || {};
    const { band, explanation, safety_override, safety_override_reason } = metadata;

    return (
        <div className="mb-8 space-y-6">
            {/* Confidence Banner */}
            <div className={`p-4 rounded-lg border flex items-start gap-4 ${safety_override ? 'bg-red-50 border-red-200' : 'bg-slate-50 border-slate-200'}`}>
                <div className={`text-2xl ${safety_override ? 'grayscale' : ''}`}>
                    {band?.includes('High') ? '🟢' : band?.includes('Medium') ? '🟡' : '🔴'}
                </div>
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 text-xs font-bold uppercase tracking-wider rounded-sm ${analysis.verdict === 'BUILD' ? 'bg-green-600 text-white' : 'bg-slate-900 text-white'
                            }`}>
                            {analysis.verdict?.replace(/_/g, " ")}
                        </span>
                        <span className="text-slate-500 text-xs font-semibold uppercase tracking-wider">
                            • {band} Confidence ({(analysis.confidence * 100).toFixed(0)}%)
                        </span>
                    </div>

                    <p className={`text-sm font-medium ${safety_override ? 'text-red-700' : 'text-slate-700'}`}>
                        {safety_override ? safety_override_reason : explanation}
                    </p>
                </div>
            </div>

            {/* Primary: The Original Idea */}
            <div>
                <h1 className="text-3xl font-bold text-slate-900 leading-tight">
                    {analysis.original_input || analysis.raw_input}
                </h1>
                <p className="text-slate-500 text-sm mt-1">
                    Your original idea
                </p>
            </div>

            {/* Secondary: Technical Details (Collapsed) */}
            <div className="border border-slate-200 rounded-lg p-4 bg-white/50">
                <div className="flex justify-between items-center">
                    <button
                        onClick={() => setShowFraming(!showFraming)}
                        className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-2 hover:text-slate-700 focus:outline-none"
                    >
                        <span className="text-[10px]">{showFraming ? '▼' : '▶'}</span>
                        {showFraming ? 'Hide Debug Details' : 'Show Debug Details'}
                    </button>

                    {safety_override && (
                        <span className="text-xs font-bold text-red-600 uppercase tracking-wider flex items-center gap-1">
                            🛡️ Safety Override Active
                        </span>
                    )}
                </div>

                {showFraming && (
                    <div className="mt-4 space-y-6 animate-in fade-in duration-300">
                        {/* 1. Investigation Framing */}
                        <div>
                            <h3 className="text-xs font-bold text-slate-400 uppercase mb-2">Generated Investigation Prompt</h3>
                            <div className="text-sm text-slate-600 font-mono whitespace-pre-wrap leading-relaxed p-3 bg-slate-50 border border-slate-100 rounded">
                                {analysis.raw_input}
                            </div>
                        </div>

                        {/* 2. Confidence Debug */}
                        {analysis.confidence_metadata && (
                            <div className="grid grid-cols-2 gap-4">
                                <ConfidenceDebugBlock metadata={analysis.confidence_metadata} />
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

function ConfidenceDebugBlock({ metadata }: { metadata: any }) {
    const { breakdown, safety_override, band } = metadata;
    return (
        <div className="col-span-2 bg-slate-100 p-3 rounded">
            <h3 className="text-xs font-bold text-slate-500 uppercase mb-2 flex justify-between">
                <span>Confidence System Internals</span>
                <span>Band: {band}</span>
            </h3>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-xs text-slate-600">
                <div>
                    <span className="block text-slate-400">Seed Agreement</span>
                    <span className="font-mono text-lg font-semibold text-slate-800">
                        {Math.round(breakdown.seed_agreement_ratio * 100)}%
                    </span>
                    <span className="block text-[10px] text-slate-400">
                        ({breakdown.agreeing_seeds}/{breakdown.total_seeds} seeds)
                    </span>
                </div>
                <div>
                    <span className="block text-slate-400">Recurrence</span>
                    <span className="font-mono text-lg font-semibold text-slate-800">
                        {breakdown.evidence_count}
                    </span>
                    <span className="block text-[10px] text-slate-400">signals</span>
                </div>
                <div>
                    <span className="block text-slate-400">Max Severity</span>
                    <span className="font-mono text-lg font-semibold text-slate-800">
                        {breakdown.max_severity_score}/100
                    </span>
                </div>
                <div>
                    <span className="block text-slate-400">Safeguard</span>
                    <span className={`font-bold ${safety_override ? 'text-red-600' : 'text-green-600'}`}>
                        {safety_override ? 'TRIGGERED' : 'PASS'}
                    </span>
                </div>
            </div>
        </div>
    )
}
