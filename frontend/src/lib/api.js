export const API_BASE = import.meta.env.VITE_API_URL;

export function authFetch(path, options = {}) {
    const token = localStorage.getItem("access_token");
    return fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            ...(options.headers || {}),
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
    });
}
