import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                bg: "#F9FAFB",
                surface: "#FFFFFF",
                border: "#E5E7EB",

                text: "#111827",
                muted: "#6B7280",

                danger: "#DC2626",
                dangerBg: "#FEE2E2",

                success: "#16A34A",
                successBg: "#DCFCE7",

                accent: "#2563EB",
            },
        },
    },
    plugins: [],
};
export default config;
