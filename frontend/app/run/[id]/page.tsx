"use client";

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { getStatus } from "@/lib/api"
import { AnalysisProgress } from "@/components/analysis/AnalysisProgress"
import { AppShell } from "@/components/layout/AppShell"

export default function RunPage({ params }: { params: { id: string } }) {
    const { id } = params
    const router = useRouter()
    const [status, setStatus] = useState<any>(null)

    useEffect(() => {
        // Initial fetch
        if (id) {
            getStatus(id).then(setStatus).catch(console.error);
        }

        const interval = setInterval(async () => {
            try {
                const data = await getStatus(id)
                setStatus(data)

                if (data.current_stage === "COMPLETED" || data.current_stage === "FAILED") {
                    clearInterval(interval)
                    router.push(`/report/${id}`)
                }
            } catch (e) {
                console.error("Polling error", e)
            }
        }, 2000)

        return () => clearInterval(interval)
    }, [id, router])

    if (!status) return (
        <AppShell>
            <div className="flex justify-center items-center h-64 text-gray-500">Initializing Intelligence Engine...</div>
        </AppShell>
    )

    return (
        <AppShell>
            <AnalysisProgress status={status} />
        </AppShell>
    )
}
