"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '@/components/layout/AppShell';
import { Button } from '@/components/ui/Button';

export default function Dashboard() {
    const [analyses, setAnalyses] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const userId = localStorage.getItem('user_id') || '1';
        fetch(`http://localhost:8000/api/analyses?user_id=${userId}`)
            .then(res => res.json())
            .then(data => {
                setAnalyses(data);
                setLoading(false);
            })
            .catch(e => console.error(e));
    }, []);

    return (
        <AppShell>
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-10 border-b border-border pb-6">
                    <h1 className="text-3xl font-bold text-text">Analysis Dashboard</h1>
                    <Link href="/new">
                        <Button className="font-semibold">+ New Analysis</Button>
                    </Link>
                </div>

                {loading ? (
                    <div className="text-muted text-center py-10">Loading workspace...</div>
                ) : analyses.length === 0 ? (
                    <div className="text-center py-24 bg-surface rounded-lg border border-border shadow-sm">
                        <h3 className="text-xl font-medium text-text mb-2">No analyses found</h3>
                        <p className="text-muted mb-8">Start your first market deep dive to get a verdict.</p>
                        <Link href="/new"><Button>Start First Analysis</Button></Link>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {analyses.map((a: any) => (
                            <Link href={`/report/${a.id}`} key={a.id} className="block group">
                                <div className="flex justify-between items-center bg-surface border border-border p-6 rounded-lg shadow-sm transition-all hover:border-muted hover:shadow-md">
                                    <div className="flex items-center space-x-4">
                                        <div className="min-w-[140px]">
                                            {a.verdict === 'DO_NOT_BUILD' ? (
                                                <span className="text-danger font-bold text-sm">❌ DO NOT BUILD</span>
                                            ) : a.verdict === 'BUILD' ? (
                                                <span className="text-success font-bold text-sm">✅ BUILD</span>
                                            ) : (
                                                <span className="text-muted font-bold text-sm">⏳ {a.status}</span>
                                            )}
                                        </div>
                                        <div className="border-l border-border h-6 mx-4"></div>
                                        <div>
                                            <h3 className="text-lg font-medium text-text group-hover:text-black truncate w-96">
                                                {a.raw_input || "Untitled Analysis"}
                                            </h3>
                                        </div>
                                    </div>

                                    <div className="text-sm text-muted">
                                        {new Date(a.created_at).toLocaleDateString()}
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </AppShell>
    );
}
