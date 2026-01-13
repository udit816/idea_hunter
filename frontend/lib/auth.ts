export function getUserId(): number {
    if (typeof window === 'undefined') return 1;
    const stored = localStorage.getItem('user_id');
    return stored ? parseInt(stored) : 1;
}

export function setUserId(id: number) {
    if (typeof window !== 'undefined') {
        localStorage.setItem('user_id', id.toString());
    }
}
