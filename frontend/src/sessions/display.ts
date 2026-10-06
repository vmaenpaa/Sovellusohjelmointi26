import type { SessionItem } from "../api/client";

export function formatSessionDate(sessionAt: string | null) {
	if (sessionAt === null) {
		return "Unscheduled";
	}

	return new Date(sessionAt).toLocaleString(undefined, {
		dateStyle: "medium",
		timeStyle: "short",
	});
}

export function statusLabel(status: string) {
	return status.replace("_", " ");
}

export function summarizeExercises(
	items: SessionItem[],
	nameById: Map<number, string>,
	maxNames = 3,
) {
	const names: string[] = [];

	for (const item of [...items].sort((a, b) => a.sort_order - b.sort_order)) {
		const name = nameById.get(item.activity_type_id) ?? "Unknown activity";
		if (!names.includes(name)) {
			names.push(name);
		}
	}

	if (names.length === 0) {
		return "No exercises";
	}

	const shown = names.slice(0, maxNames).join(", ");
	return names.length > maxNames ? `${shown} +${names.length - maxNames}` : shown;
}
