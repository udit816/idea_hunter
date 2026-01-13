const API_BASE = "http://localhost:8000";

export async function fetchAnalysis(id: string) {
    const res = await fetch(`${API_BASE}/api/report/${id}`);
    if (!res.ok) throw new Error("Failed to fetch report");
    return res.json();
}

export async function startAnalysis(userId: number, rawInput: string, originalInput?: string) {
    const res = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: userId,
            raw_input: rawInput,
            original_input: originalInput
        }),
    });
    return res.json();
}

export async function frameInvestigation(input: string) {
    const res = await fetch(`${API_BASE}/api/frame-investigation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ raw_input: input })
    })
    return res.json()
}

export async function getStatus(analysisId: string) {
    const res = await fetch(`${API_BASE}/api/status/${analysisId}`)
    return res.json()
}
