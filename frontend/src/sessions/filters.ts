import type { SessionFilters } from "../api/queryKeys";

export type ScheduleFilter = "all" | "dated" | "unscheduled";

export type FilterDraft = {
	from: string;
	to: string;
	status: string;
	schedule: ScheduleFilter;
	planId: string;
	activityTypeId: string;
};

export const emptyDraft: FilterDraft = {
	from: "",
	to: "",
	status: "",
	schedule: "all",
	planId: "",
	activityTypeId: "",
};

export function validateDraft(draft: FilterDraft) {
	if (
		draft.schedule !== "unscheduled" &&
		draft.from !== "" &&
		draft.to !== "" &&
		draft.from > draft.to
	) {
		return "The from date must not be after the to date.";
	}

	return null;
}

export function toApiFilters(draft: FilterDraft): SessionFilters {
	const filters: SessionFilters = {};

	if (draft.schedule === "unscheduled") {
		filters.unscheduled = true;
	} else {
		if (draft.schedule === "dated") {
			filters.unscheduled = false;
		}
		if (draft.from !== "") {
			filters.from = new Date(`${draft.from}T00:00:00`).toISOString();
		}
		if (draft.to !== "") {
			filters.to = new Date(`${draft.to}T23:59:59.999`).toISOString();
		}
	}

	if (draft.status !== "") {
		filters.status = draft.status;
	}
	if (draft.planId !== "") {
		filters.planId = Number(draft.planId);
	}
	if (draft.activityTypeId !== "") {
		filters.activityTypeId = Number(draft.activityTypeId);
	}

	return filters;
}

export function hasActiveFilters(filters: SessionFilters) {
	return Object.keys(filters).length > 0;
}
