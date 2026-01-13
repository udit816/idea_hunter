export function ProblemSection() {
    return (
        <section className="py-24 bg-surface border-y border-border">
            <div className="max-w-4xl mx-auto px-4 text-center">
                <h2 className="text-3xl font-bold text-text mb-6">
                    Most founders don’t fail because they can’t build.
                </h2>
                <p className="text-xl text-muted mb-12">
                    They fail because they build the wrong thing with confidence.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 text-left">
                    {[
                        "“The idea feels promising”",
                        "“People on Twitter liked it”",
                        "“AI said it’s a good niche”",
                        "“We’ll figure it out after MVP”"
                    ].map((trap, i) => (
                        <div key={i} className="p-6 bg-bg rounded-lg border border-border">
                            <p className="text-text font-medium italic">{trap}</p>
                        </div>
                    ))}
                </div>

                <p className="mt-12 text-lg text-text font-bold">
                    By the time reality shows up, months are gone. <br />
                    <span className="text-danger">Building is expensive. Deciding is cheaper.</span>
                </p>
            </div>
        </section>
    )
}
