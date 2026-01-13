import React from 'react';

type Props = {
    label: string
    state: "pending" | "active" | "done"
}

export function StageRow({ label, state }: Props) {
    const icon =
        state === "done" ? "✅" :
            state === "active" ? "⏳" : "⬜";

    const textClass =
        state === "done" ? "text-gray-900 font-medium" :
            state === "active" ? "text-blue-700 font-bold animate-pulse" :
                "text-gray-400";

    return (
        <div className="flex items-center py-3 border-l-2 pl-4 border-gray-100">
            <span className="mr-3 text-xl">{icon}</span>
            <strong className={textClass}>{label}</strong>
        </div>
    )
}
