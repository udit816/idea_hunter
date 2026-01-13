import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Hero } from "@/components/marketing/Hero";
import { ProblemSection } from "@/components/marketing/ProblemSection";
import { HowItWorks } from "@/components/marketing/HowItWorks";

export default function Home() {
    return (
        <main className="flex min-h-screen flex-col bg-bg">
            <Navbar />
            <Hero />
            <ProblemSection />
            <HowItWorks />
            <Footer />
        </main>
    );
}
