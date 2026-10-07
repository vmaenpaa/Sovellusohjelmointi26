import { clearToken, getToken } from "../auth/token";
import type { SessionFilters } from "./queryKeys";

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

export type Measurement = {
    id: number;
    unit_type_id: number;
    planned_value: string | null;
    actual_value: string | null;
    set_index: number | null;
};

export type SessionItem = {
    id: number;
    activity_type_id: number;
    sort_order: number;
    notes: string | null;
    measurements: Measurement[];
};

export type SessionSummary = {
    id: number;
    name: string;
    session_at: string | null;
    status: string;
    plan_id: number | null;
    items: SessionItem[];
};

export type SessionDetail = SessionSummary & {
    notes: string | null;
    intensity: number | null;
};

export type SessionWrite = {
    name: string;
    session_at: string | null;
    status: string;
    notes: string | null;
    intensity: number | null;
    plan_id: number | null;
    items: {
        activity_type_id: number;
        sort_order: number;
        notes: string | null;
        measurements: {
            unit_type_id: number;
            planned_value: number | null;
            actual_value: number | null;
            set_index: number | null;
        }[];
    }[];
};

export type Plan = {
    id: number;
    name: string;
};

export type UnitLink = {
    unit_type_id: number;
    sort_order: number;
    is_required: boolean;
    per_set: boolean;
    unit_type: { name: string; slug: string; label: string | null };
};

export type ActivityType = {
    id: number;
    name: string;
    unit_links: UnitLink[];
};

export function listSessions(filters: SessionFilters = {}) {
    const params = new URLSearchParams();

    if (filters.from) params.set("from", filters.from);
    if (filters.to) params.set("to", filters.to);
    if (filters.status) params.set("status", filters.status);
    if (filters.activityTypeId !== undefined) {
        params.set("activity_type_id", String(filters.activityTypeId));
    }
    if (filters.unscheduled !== undefined) {
        params.set("unscheduled", String(filters.unscheduled));
    }
    if (filters.planId !== undefined) {
        params.set("plan_id", String(filters.planId));
    }

    const query = params.toString();
    return apiRequest<SessionSummary[]>(`/sessions${query ? `?${query}` : ""}`);
}

export function listPlans() {
    return apiRequest<Plan[]>("/plans");
}

export function listActivityTypes() {
    return apiRequest<ActivityType[]>("/activity-types");
}

export function getSession(id: number) {
    return apiRequest<SessionDetail>(`/sessions/${id}`);
}

export function createSession(body: SessionWrite) {
    return apiRequest<SessionDetail>("/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
}

export type SessionClone = {
    name?: string;
    session_at?: string | null;
};

export function cloneSession(id: number, body: SessionClone) {
    return apiRequest<SessionDetail>(`/sessions/${id}/clone`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
}

export function deleteSession(id: number) {
    return apiRequest<null>(`/sessions/${id}`, { method: "DELETE" });
}

export function updateSession(id: number, body: SessionWrite) {
    return apiRequest<SessionDetail>(`/sessions/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
}