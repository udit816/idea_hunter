import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { KillSwitchPreview } from './KillSwitchPreview';

export function Hero() {
    return (
        <section className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                <div className="text-left">
                    <h1 className="text-5xl font-extrabold text-text tracking-tight mb-6 leading-tight">
                        Build less. <br />Decide better.
                    </h1>
                    <p className="text-xl text-muted mb-8 max-w-lg leading-relaxed">
                        DecideKit is an AI product manager that analyzes real user evidence and tells you whether a product should exist before you build it.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 items-start">
                        <Link href="/new">
                            <Button className="px-8 py-4 text-lg">Run your idea through the engine</Button>
                        </Link>
                        <Link href="/sample-report">
                            <Button variant="outline" className="px-6 py-4 text-lg border-border text-text hover:bg-gray-50">
                                View a sample DO NOT BUILD report →
                            </Button>
                        </Link>
                    </div>
                    <p className="mt-4 text-sm text-muted">
                        No hype. No optimism bias. Just a clear BUILD or DO NOT BUILD decision.
                    </p>
                </div>

                <div className="flex justify-center lg:justify-end">
                    <div className="w-full max-w-md transform transition-all duration-300 hover:scale-[1.01]">
                        <KillSwitchPreview />
                        {/* Decorative element to show depth/stacking if needed, but keeping calm for now */}
                    </div>
                </div>
            </div>
        </section>
    );
}
