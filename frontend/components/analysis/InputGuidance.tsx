"use client";

import { useState } from "react"
import { useRouter } from "next/navigation"
import { startAnalysis, frameInvestigation } from "@/lib/api"
import { Tooltip } from "@/components/ui/Tooltip"
import { Button } from "@/components/ui/Button"

export function InputGuidance() {
    // State
    const [context, setContext] = useState("") // The original user idea
    const [generatedPrompt, setGeneratedPrompt] = useState("") // The framed prompt
    const [step, setStep] = useState<"INPUT" | "REVIEW">("INPUT")
    const [loading, setLoading] = useState(false)
    const [editable, setEditable] = useState(false)

    const router = useRouter()

    // Derived state
    const wordCount = context.trim().split(/\s+/).filter(Boolean).length
    const isTooLong = wordCount > 400
    const showWarning = wordCount > 250

    // Handlers
    async function handleGeneratePlan() {
        if (!context.trim() || isTooLong) return;
        setLoading(true);
        try {
            const res = await frameInvestigation(context);
            setGeneratedPrompt(res.generated_prompt);
            setStep("REVIEW");
        } catch (e) {
            console.error(e);
            alert("Failed to generate investigation plan");
        }
        setLoading(false);
    }

    async function handleStartAnalysis() {
        const finalPrompt = generatedPrompt.trim();
        if (!finalPrompt) return;

        setLoading(true);
        const userId = localStorage.getItem('user_id') ? parseInt(localStorage.getItem('user_id')!) : 1;

        try {
            // Pass the Framed Prompt as raw_input (the prompt used for analysis)
            // Pass the Context as original_input (the user's idea for display)
            const { analysis_id } = await startAnalysis(userId, finalPrompt, context);
            router.push(`/run/${analysis_id}`);
        } catch (e) {
            console.error(e);
            alert("Failed to start analysis");
            setLoading(false);
        }
    }

    return (
        <div className="w-full max-w-2xl mx-auto bg-white p-6 rounded-xl shadow-sm border border-slate-100">
            <h2 className="text-2xl font-bold mb-6 text-slate-900">
                {step === "INPUT" ? "What are you exploring?" : "Review Investigation Plan"}
            </h2>

            {step === "INPUT" && (
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
                            Describe your idea
                            <Tooltip text="You can enter a product idea, market, workflow, or problem space. Avoid pitching features — we’ll frame the investigation correctly." />
                        </label>
                        <p className="text-slate-500 text-sm mb-4">
                            Don't worry about framing. Just dump your raw idea, audience, or problem. <br />
                            We will structure the investigation for you.
                        </p>
                    </div>

                    <div className="space-y-2">
                        <textarea
                            className={`w-full h-32 p-3 text-slate-700 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none resize-none ${isTooLong ? 'border-red-300 bg-red-50' : 'border-slate-200'}`}
                            placeholder="e.g. A B2B dashboard for tracking brand mentions in LLM outputs..."
                            value={context}
                            onChange={(e) => setContext(e.target.value)}
                        />

                        <div className="flex justify-between items-center text-xs">
                            <span className={`${isTooLong ? 'text-red-600 font-bold' : showWarning ? 'text-amber-600 font-medium' : 'text-slate-400'}`}>
                                {wordCount} words {isTooLong ? '(Too long - please shorten)' : showWarning ? '(Getting long...)' : ''}
                            </span>
                            {isTooLong && <span className="text-red-500">Max 400 words.</span>}
                        </div>

                        <div className="flex justify-end pt-2">
                            <Button
                                onClick={handleGeneratePlan}
                                disabled={loading || !context.trim() || isTooLong}
                                className="px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 disabled:opacity-50 transition-all flex items-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Architecting...
                                    </>
                                ) : (
                                    <>
                                        Generate Investigation Plan <span className="text-slate-400">→</span>
                                    </>
                                )}
                            </Button>
                        </div>
                    </div>
                </div>
            )}

            {step === "REVIEW" && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                            Investigation Framing
                        </label>
                        <p className="text-xs text-slate-500 mb-4 leading-relaxed">
                            We’ve translated your input into a neutral, evidence-seeking investigation.
                            This helps avoid bias and ensures a fair BUILD / DO NOT BUILD decision.
                        </p>
                        <textarea
                            rows={10}
                            readOnly={!editable}
                            className={`w-full bg-transparent p-2 text-slate-800 text-sm font-medium focus:ring-0 resize-none ${editable ? 'border border-slate-300 rounded bg-white' : 'border-none'}`}
                            value={generatedPrompt}
                            onChange={(e) => setGeneratedPrompt(e.target.value)}
                        />
                    </div>

                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setEditable(!editable)}
                            className="text-xs text-slate-500 underline hover:text-slate-800 mr-auto"
                        >
                            {editable ? "Done Editing" : "Edit framing (Advanced)"}
                        </button>

                        <Button variant="secondary" onClick={() => setStep("INPUT")} disabled={loading} className="w-1/3">
                            ← Back
                        </Button>
                        <Button onClick={handleStartAnalysis} disabled={loading} className="w-2/3 bg-blue-600 hover:bg-blue-700 text-white">
                            {loading ? "Starting Analysis..." : "Run Analysis"}
                        </Button>
                    </div>
                </div>
            )}
        </div>
    )
}
