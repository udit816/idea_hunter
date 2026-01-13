"use client";

import { AppShell } from "@/components/layout/AppShell";
import { InputGuidance } from "@/components/analysis/InputGuidance";

export default function NewAnalysis() {
    return (
        <AppShell>
            <div className="flex flex-col items-center">
                <h1 className="text-3xl font-extrabold text-gray-900 mb-2">New Analysis</h1>
                <p className="text-gray-500 mb-8">We will try to kill this idea via deep market mining.</p>

                <div className="w-full max-w-2xl">
                    <InputGuidance />
                </div>
            </div>
        </AppShell>
    );
}
