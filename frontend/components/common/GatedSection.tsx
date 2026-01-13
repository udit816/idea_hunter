import React from 'react';
import { Button } from '@/components/ui/Button';

interface GatedSectionProps {
    isLocked: boolean;
    title: string;
    children: React.ReactNode;
    onUnlock?: () => void;
}

export function GatedSection({ isLocked, title, children, onUnlock }: GatedSectionProps) {
    if (!isLocked) {
        return <>{children}</>;
    }

    return (
        <div className="relative group overflow-hidden rounded-xl border border-slate-200">
            {/* Blurred Content */}
            <div className="blur-sm select-none opacity-50 pointer-events-none p-6 bg-slate-50" aria-hidden="true">
                {children}
            </div>

            {/* Lock Overlay */}
            <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-white/60 backdrop-blur-[1px] p-6 text-center">
                <div className="bg-white p-6 rounded-xl shadow-xl border border-slate-100 max-w-sm w-full transform transition-all hover:scale-105">
                    <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">
                        🔒
                    </div>
                    <h3 className="text-lg font-bold text-slate-900 mb-2">
                        Pro Insight Locked
                    </h3>
                    <p className="text-sm text-slate-600 mb-6 leading-relaxed">
                        {title}
                        <br />
                        <span className="text-xs text-slate-400 mt-2 block">
                            (Confidence: directionally reliable, details gated)
                        </span>
                    </p>
                    <Button
                        onClick={onUnlock}
                        className="w-full bg-gradient-to-r from-slate-900 to-slate-800 text-white shadow-lg hover:shadow-xl transition-all"
                    >
                        Unlock Full Report
                    </Button>
                </div>
            </div>
        </div>
    );
}
