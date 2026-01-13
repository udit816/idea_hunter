"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const router = useRouter();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();

        // Call API (In a real app, use sessions/cookies/tokens)
        const res = await fetch('http://localhost:8000/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('user_id', data.user_id);
            router.push('/dashboard');
        } else {
            alert('Invalid credentials. (Hint: demo / demo123)');
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center">
            <div className="bg-white p-8 rounded shadow-md w-full max-w-sm">
                <h1 className="text-2xl font-bold mb-6 text-center">DecideKit Login</h1>
                <form onSubmit={handleLogin} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium">Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={e => setUsername(e.target.value)}
                            className="mt-1 block w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            className="mt-1 block w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>
                    <button className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
                        Sign In
                    </button>
                    <p className="text-xs text-center text-gray-500">Hint: demo / demo123</p>
                </form>
            </div>
        </div>
    );
}
