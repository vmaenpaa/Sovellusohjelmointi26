const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function apiFetch(path: string, options?: RequestInit) {
    return fetch(`${API_BASE_URL}${path}`, options);
}