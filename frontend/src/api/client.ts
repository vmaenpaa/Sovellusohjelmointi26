import { clearToken, getToken } from "../auth/token";

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
    status: number;
    detail: string;

    constructor(status: number, detail: string) {
        super(`${status}: ${detail}`);
        this.name = "ApiError";
        this.status = status;
        this.detail = detail;
    }
}

export async function apiFetch(path: string, options?: RequestInit) {
    const headers = new Headers(options?.headers);
    const token = getToken();

    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers,
    });

    if (response.status === 401 && path !== "/auth/login") {
        clearToken();
    }

    return response;
}

export async function apiRequest<T>(
    path: string,
    options?: RequestInit,
): Promise<T> {
    const response = await apiFetch(path, options);
    const data = await response.json().catch(() => null);

    if (!response.ok) {
        const detail =
            typeof data?.detail === "string" ? data.detail : response.statusText;
        throw new ApiError(response.status, detail);
    }

    return data as T;
}