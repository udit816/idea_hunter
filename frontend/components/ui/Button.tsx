import React from 'react';
import Link from 'next/link';

type ButtonProps = {
    children: React.ReactNode;
    onClick?: (e: React.FormEvent) => void;
    disabled?: boolean;
    className?: string;
    variant?: 'primary' | 'secondary' | 'danger' | 'outline';
    href?: string;
}

export function Button({
    children,
    onClick,
    disabled = false,
    className = "",
    variant = "primary",
    href
}: ButtonProps) {
    const baseStyle = "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background px-4 py-2";

    const variants = {
        primary: "bg-black text-white hover:bg-gray-900 border border-transparent shadow-sm",
        secondary: "bg-surface text-text border border-border hover:bg-gray-50",
        danger: "bg-danger text-white hover:bg-red-700",
        outline: "bg-transparent border border-border text-text hover:bg-bg"
    };

    const finalClass = `${baseStyle} ${variants[variant]} ${className}`;

    if (href) {
        return (
            <Link href={href} className={finalClass}>
                {children}
            </Link>
        );
    }

    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={finalClass}
        >
            {children}
        </button>
    );
}
