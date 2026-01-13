import React from 'react';

export function Tooltip({ text }: { text: string }) {
    return (
        <span className="group relative ml-1 cursor-help inline-block">
            <span className="text-gray-400 hover:text-gray-600">ℹ️</span>
            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block w-64 bg-black text-white text-xs rounded p-2 z-10 text-center">
                {text}
            </div>
        </span>
    )
}
