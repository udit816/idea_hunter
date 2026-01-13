import Link from 'next/link';

export function Navbar() {
    return (
        <header className="border-b border-border bg-surface">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex justify-between items-center">
                <div className="flex items-center">
                    <Link href="/" className="text-xl font-bold text-text tracking-tight hover:opacity-80 transition-opacity">
                        DecideKit
                    </Link>
                </div>

                <nav className="flex space-x-8">
                    <Link href="/pricing" className="text-sm font-medium text-muted hover:text-text transition-colors">
                        Pricing
                    </Link>
                    <Link href="/new" className="text-sm font-medium text-muted hover:text-text transition-colors">
                        New Analysis
                    </Link>
                    <Link href="/dashboard" className="text-sm font-medium text-muted hover:text-text transition-colors">
                        Dashboard
                    </Link>
                </nav>
            </div>
        </header>
    )
}
