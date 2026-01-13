export function Footer() {
    return (
        <footer className="border-t border-border bg-bg py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center">
                <p className="text-sm text-text font-medium mb-2">
                    DecideKit doesn’t help you build faster. It helps you build less — and build right.
                </p>
                <p className="text-xs text-muted">
                    © {new Date().getFullYear()} DecideKit. All rights reserved.
                </p>
            </div>
        </footer>
    )
}
