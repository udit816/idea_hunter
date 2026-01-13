import { Navbar } from "./Navbar";
import { Footer } from "./Footer";

export function AppShell({ children }: { children: React.ReactNode }) {
    return (
        <div className="min-h-screen flex flex-col bg-gray-50">
            <Navbar />
            <main className="flex-1 py-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    {children}
                </div>
            </main>
            <Footer />
        </div>
    )
}
