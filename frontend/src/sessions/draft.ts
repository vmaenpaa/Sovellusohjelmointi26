import type {
	ActivityType,
	SessionDetail,
	SessionWrite,
} from "../api/client";

export type ValuePair = { planned: string; actual: string };

export type UnitDraft = {
	unitTypeId: number;
	label: string;
	perSet: boolean;
	values: ValuePair[];
};

export type ExerciseDraft = {
	key: string;
	activityTypeId: number;
	notes: string;
	units: UnitDraft[];
};

export type SessionDraft = {
	name: string;
	sessionAt: string;
	status: string;
	planId: string;
	intensity: string;
	notes: string;
	exercises: ExerciseDraft[];
};

export function emptyPair(): ValuePair {
	return { planned: "", actual: "" };
}

export function emptyDraft(): SessionDraft {
	return {
		name: "",
		sessionAt: "",
		status: "planned",
		planId: "",
		intensity: "",
		notes: "",
		exercises: [],
	};
}

export function buildUnits(activity: ActivityType | undefined): UnitDraft[] {
	if (!activity) {
		return [];
	}

	return [...activity.unit_links]
		.sort((a, b) => a.sort_order - b.sort_order)
		.map((link) => ({
			unitTypeId: link.unit_type_id,
			label: link.unit_type.label ?? link.unit_type.name,
			perSet: link.per_set,
			values: [emptyPair()],
		}));
}

export function newExercise(activity: ActivityType): ExerciseDraft {
	return {
		key: crypto.randomUUID(),
		activityTypeId: activity.id,
		notes: "",
		units: buildUnits(activity),
	};
}

function formatValue(value: string | null) {
	return value === null ? "" : String(Number(value));
}

export function toLocalInput(iso: string | null) {
	if (iso === null) {
		return "";
	}

	const date = new Date(iso);
	const pad = (value: number) => String(value).padStart(2, "0");

	return (
		`${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
		`T${pad(date.getHours())}:${pad(date.getMinutes())}`
	);
}

export function draftFromSession(
	session: SessionDetail,
	activityTypes: ActivityType[],
): SessionDraft {
	const exercises = [...session.items]
		.sort((a, b) => a.sort_order - b.sort_order)
		.map((item): ExerciseDraft => {
			const activity = activityTypes.find((a) => a.id === item.activity_type_id);
			const units = buildUnits(activity).map((unit) => {
				const rows = item.measurements
					.filter((m) => m.unit_type_id === unit.unitTypeId)
					.sort((a, b) => (a.set_index ?? 0) - (b.set_index ?? 0))
					.map((m) => ({
						planned: formatValue(m.planned_value),
						actual: formatValue(m.actual_value),
					}));

				if (rows.length === 0) {
					return unit;
				}
				return { ...unit, values: unit.perSet ? rows : [rows[0]] };
			});

			return {
				key: crypto.randomUUID(),
				activityTypeId: item.activity_type_id,
				notes: item.notes ?? "",
				units,
			};
		});

	return {
		name: session.name,
		sessionAt: toLocalInput(session.session_at),
		status: session.status,
		planId: session.plan_id === null ? "" : String(session.plan_id),
		intensity: session.intensity === null ? "" : String(session.intensity),
		notes: session.notes ?? "",
		exercises,
	};
}

function isBlank(value: string) {
	return value.trim() === "";
}

export function validateDraft(draft: SessionDraft): string | null {
	if (isBlank(draft.name)) {
		return "Name is required.";
	}
	if (draft.name.trim().length > 200) {
		return "Name must be 200 characters or fewer.";
	}

	if (!isBlank(draft.intensity)) {
		const intensity = Number(draft.intensity);
		if (!Number.isInteger(intensity) || intensity < 1 || intensity > 10) {
			return "Intensity must be a whole number from 1 to 10.";
		}
	}

	for (const exercise of draft.exercises) {
		for (const unit of exercise.units) {
			for (const pair of unit.values) {
				for (const value of [pair.planned, pair.actual]) {
					if (!isBlank(value) && !Number.isFinite(Number(value))) {
						return `"${value}" is not a valid number for ${unit.label}.`;
					}
				}
			}
		}
	}

	return null;
}

function toNumber(value: string) {
	return isBlank(value) ? null : Number(value);
}

export function toSessionWrite(draft: SessionDraft): SessionWrite {
	return {
		name: draft.name.trim(),
		session_at: isBlank(draft.sessionAt)
			? null
			: new Date(draft.sessionAt).toISOString(),
		status: draft.status,
		notes: isBlank(draft.notes) ? null : draft.notes,
		intensity: isBlank(draft.intensity) ? null : Number(draft.intensity),
		plan_id: isBlank(draft.planId) ? null : Number(draft.planId),
		items: draft.exercises.map((exercise, index) => ({
			activity_type_id: exercise.activityTypeId,
			sort_order: index,
			notes: isBlank(exercise.notes) ? null : exercise.notes,
			measurements: exercise.units.flatMap((unit) =>
				unit.values.flatMap((pair, setIndex) =>
					isBlank(pair.planned) && isBlank(pair.actual)
						? []
						: [
								{
									unit_type_id: unit.unitTypeId,
									planned_value: toNumber(pair.planned),
									actual_value: toNumber(pair.actual),
									set_index: unit.perSet ? setIndex : null,
								},
							],
				),
			),
		})),
	};
}
