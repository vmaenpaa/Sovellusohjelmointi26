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

export const queryKeys = {
	sessions: (filters: SessionFilters = {}) => ["sessions", filters] as const,
	session: (id: number | string) => ["sessions", "detail", id] as const,
	plans: ["plans"] as const,
	plan: (id: number | string) => ["plans", "detail", id] as const,
	calendar: (from: string, to: string, planId?: number | null) =>
		["calendar", from, to, planId ?? null] as const,
	activityTypes: ["activity-types"] as const,
	goals: (active?: boolean) => ["goals", active] as const,
};
