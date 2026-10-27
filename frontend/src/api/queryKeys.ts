export type SessionFilters = {
	from?: string;
	to?: string;
	status?: string;
	activityTypeId?: number;
	unscheduled?: boolean;
	planId?: number;
	page?: number;
	limit?: number;
};

export type ProgressFilters = {
	metric: "session_count" | "duration_min" | "distance_km" | "reps" | "weight_kg";
	granularity?: "week" | "month";
	activityTypeId?: number;
	from?: string;
	to?: string;
};

export type StatsSummaryFilters = {
	from?: string;
	to?: string;
};

export const queryKeys = {
	sessions: (filters: SessionFilters = {}) => ["sessions", filters] as const,
	session: (id: number | string) => ["sessions", "detail", id] as const,
	plans: ["plans"] as const,
	plan: (id: number | string) => ["plans", "detail", id] as const,
	calendar: (from: string, to: string, planId?: number | null) =>
		["calendar", from, to, planId ?? null] as const,
	statsProgress: (filters: ProgressFilters) => ["stats", "progress", filters] as const,
	statsSummary: (filters: StatsSummaryFilters = {}) => ["stats", "summary", filters] as const,
	activityTypes: ["activity-types"] as const,
	goals: (active?: boolean) => ["goals", active] as const,
};
