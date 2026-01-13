import { StageRow } from "./StageRow"

type Props = {
    status: {
        current_stage: string
        completed_stages: string[]
    }
}

const STAGES = [
    "VERIFYING",
    "HUNTING",
    "MINING",
    "SYNTHESIZING",
    "JUSTIFYING",
    "KILL_SWITCH",
    "ARCHITECTING"
]

export function AnalysisProgress({ status }: Props) {
    return (
        <div className="max-w-xl mx-auto bg-white p-8 rounded-lg shadow w-full">
            <h2 className="text-2xl font-bold mb-6 text-center">Analysis in Progress</h2>
            <div className="space-y-1">
                {STAGES.map(stage => (
                    <StageRow
                        key={stage}
                        label={stage}
                        state={
                            status.completed_stages.includes(stage)
                                ? "done"
                                : status.current_stage === stage
                                    ? "active"
                                    : "pending"
                        }
                    />
                ))}
            </div>
        </div>
    )
}
