export function HowItWorks() {
    const steps = [
        { title: "You start with anything", desc: "An idea, competitors, URLs, or even a half-baked observation." },
        { title: "We gather real evidence", desc: "From Reddit, App reviews, Forums. No surveys. No opinions. No vibes." },
        { title: "We synthesize real pain", desc: "We identify repeated failure patterns, not one-off complaints." },
        { title: "The Kill-Switch decides", desc: "✅ BUILD (Defensible PRD) or ❌ DO NOT BUILD (Clear reasons)." },
    ];

    return (
        <section className="py-24 max-w-5xl mx-auto px-4">
            <h2 className="text-3xl font-bold text-text mb-16 text-center">How It Works</h2>
            <div className="relative border-l-2 border-border ml-6 lg:ml-0 space-y-12">
                {steps.map((step, i) => (
                    <div key={i} className="relative pl-12 lg:pl-0 lg:grid lg:grid-cols-12 lg:gap-8 items-start">
                        <div className="hidden lg:block lg:col-span-1 absolute lg:static left-[-9px] lg:left-auto mt-1 lg:mt-0">
                            <div className="w-4 h-4 rounded-full bg-muted lg:mx-auto"></div>
                        </div>
                        <div className="lg:col-span-11">
                            <span className="inline-block px-3 py-1 bg-bg text-muted text-xs font-bold uppercase tracking-wider rounded mb-2">
                                Step {i + 1}
                            </span>
                            <h3 className="text-xl font-bold text-text mb-2">{step.title}</h3>
                            <p className="text-muted leading-relaxed">{step.desc}</p>
                        </div>
                    </div>
                ))}
            </div>
        </section>
    )
}
