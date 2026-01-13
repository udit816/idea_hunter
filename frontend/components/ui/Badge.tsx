import React from 'react';

type Props = {
    label: string;
    variant?: "default" | "success" | "warning" | "error";
};

export function Badge({ label, variant = "default" }: Props) {
    const styles = {
        default: "bg-gray-100 text-gray-800",
        success: "bg-green-100 text-green-800",
        warning: "bg-orange-100 text-orange-800",
        error: "bg-red-100 text-red-800"
    };

    return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[variant]}`}>
            {label}
        </span>
    )
}
