import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Button } from "@/components/ui/Button";

export default function Pricing() {
    return (
        <main className="min-h-screen bg-bg flex flex-col font-sans">
            <Navbar />

            <section className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex-grow">
                <div className="text-center mb-16">
                    <h1 className="text-4xl font-extrabold text-text mb-4">Pricing Philosophy</h1>
                    <p className="text-xl text-muted max-w-2xl mx-auto">
                        You don’t pay for dashboards. You pay for decisions that save time and money.
                        <br className="hidden sm:block" /> No subscriptions. No dark pricing. No feature baiting.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">

                    {/* Free Tier */}
                    <div className="bg-surface p-8 rounded-lg border border-border">
                        <h3 className="text-xl font-bold text-text mb-2">Free — Reality Check</h3>
                        <div className="text-3xl font-extrabold text-text mb-6">Free</div>
                        <ul className="space-y-4 mb-8 text-muted">
                            <li>• Competitor discovery</li>
                            <li>• Light pain signals</li>
                            <li>• Market surface scan</li>
                            <li className="opacity-50 line-through">• Full evidence synthesis</li>
                            <li className="opacity-50 line-through">• Kill-Switch verdict</li>
                        </ul>
                        <p className="text-sm text-muted mb-6 h-10">Best for getting a feel for how the engine thinks.</p>
                        <Button variant="outline" className="w-full">Try a free scan</Button>
                    </div>

                    {/* Decision Pass */}
                    <div className="bg-surface p-8 rounded-lg border-2 border-text shadow-xl relative transform scale-105">
                        <span className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-text text-white text-xs font-bold px-3 py-1 rounded uppercase tracking-wide">
                            Most Popular
                        </span>
                        <h3 className="text-xl font-bold text-text mb-2">Decision Pass</h3>
                        <div className="text-3xl font-extrabold text-text mb-6">$19 <span className="text-lg font-normal text-muted">/ decision</span></div>
                        <ul className="space-y-4 mb-8 text-text font-medium">
                            <li>• Full evidence mining</li>
                            <li>• Pain synthesis</li>
                            <li>• Feature justification</li>
                            <li>• <span className="font-bold">Kill-Switch verdict</span></li>
                            <li>• Clear BUILD / DO NOT BUILD report</li>
                        </ul>
                        <p className="text-sm text-muted mb-6 h-10">No PRD. Just the decision for checking ideas fast.</p>
                        <Button className="w-full py-3">Get a decision</Button>
                    </div>

                    {/* Builder Pass */}
                    <div className="bg-surface p-8 rounded-lg border border-border">
                        <h3 className="text-xl font-bold text-text mb-2">Builder Pass</h3>
                        <div className="text-3xl font-extrabold text-text mb-6">$49 <span className="text-lg font-normal text-muted">/ decision</span></div>
                        <ul className="space-y-4 mb-8 text-muted">
                            <li>• Everything in Decision Pass</li>
                            <li className="text-text font-semibold">• Full PM-grade PRD</li>
                            <li>• MVP scope & non-goals</li>
                            <li>• Risks & success metrics</li>
                        </ul>
                        <p className="text-sm text-muted mb-6 h-10">For people ready to execute immediately.</p>
                        <Button variant="outline" className="w-full">Get PRD & Decision</Button>
                    </div>

                </div>

                <div className="mt-20 max-w-3xl mx-auto bg-surface border border-border p-8 rounded-lg text-center">
                    <h3 className="text-xl font-bold text-text mb-4">Refund Policy</h3>
                    <p className="text-muted leading-relaxed">
                        We believe clarity has value — even when the answer is no. <br /><br />
                        We refund for technical failures or broken reports.<br />
                        We do <span className="font-bold text-text">not</span> refund because you "didn't like the verdict".
                        A clear "no" is a successful outcome that saved you months of work.
                    </p>
                </div>

            </section>

            <Footer />
        </main>
    );
}
