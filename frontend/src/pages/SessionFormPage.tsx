import { useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useLocation, useNavigate, useParams } from "react-router";
import {
	ApiError,
	cloneSession,
	createSession,
	deleteSession,
	getSession,
	listActivityTypes,
	listPlans,
	updateSession,
	type ActivityType,
	type Plan,
	type SessionDetail,
} from "../api/client";
import { queryKeys } from "../api/queryKeys";
import MeasurementEditor from "../components/MeasurementEditor";
import {
	buildUnits,
	draftFromSession,
	emptyDraft,
	newExercise,
	toSessionWrite,
	validateDraft,
	type SessionDraft,
} from "../sessions/draft";
import "./SessionFormPage.css";

function errorMessage(error: unknown, fallback: string) {
	if (error instanceof ApiError) {
		if (error.status === 404) {
			return error.detail && error.detail !== "Not Found"
				? error.detail
				: "Session not found.";
		}
		if (error.status === 403) {
			return "You cannot change this session.";
		}
		return error.detail;
	}
	return fallback;
}

export default function SessionFormPage() {
	const { sessionId } = useParams();
	const isNew = sessionId === undefined;
	const id = isNew ? null : Number(sessionId);
	const validId = id !== null && Number.isInteger(id) && id > 0;

	const session = useQuery({
		queryKey: queryKeys.session(id ?? "new"),
		queryFn: () => getSession(id as number),
		enabled: validId,
	});
	const plans = useQuery({ queryKey: queryKeys.plans, queryFn: listPlans });
	const activityTypes = useQuery({
		queryKey: queryKeys.activityTypes,
		queryFn: listActivityTypes,
	});

	if (!isNew && !validId) {
		return <main className="designer-page">Session not found.</main>;
	}
	if (session.isError) {
		return (
			<main className="designer-page">
				{session.error instanceof ApiError && session.error.status === 404
					? "Session not found."
					: `Could not load session: ${session.error.message}`}
			</main>
		);
	}
	if (plans.isError || activityTypes.isError) {
		return <main className="designer-page">Could not load plans or activities.</main>;
	}
	if (
		(!isNew && !session.data) ||
		!plans.data ||
		!activityTypes.data
	) {
		return <main className="designer-page">Loading...</main>;
	}

	return (
		<DesignerForm
			key={id ?? "new"}
			sessionId={id}
			session={session.data ?? null}
			plans={plans.data}
			activityTypes={activityTypes.data}
		/>
	);
}

type DesignerFormProps = {
	sessionId: number | null;
	session: SessionDetail | null;
	plans: Plan[];
	activityTypes: ActivityType[];
};

function DesignerForm({
	sessionId,
	session,
	plans,
	activityTypes,
}: DesignerFormProps) {
	const navigate = useNavigate();
	const queryClient = useQueryClient();
	const [draft, setDraftState] = useState<SessionDraft>(() =>
		session ? draftFromSession(session, activityTypes) : emptyDraft(),
	);
	const [validationError, setValidationError] = useState<string | null>(null);
	const [saved, setSaved] = useState(false);
	const [confirmingDelete, setConfirmingDelete] = useState(false);
	const [cloneName, setCloneName] = useState(session?.name ?? "");
	const [cloneAt, setCloneAt] = useState("");
	const cloned =
		(useLocation().state as { cloned?: boolean } | null)?.cloned === true;

	const invalidateSessions = () =>
		Promise.all([
			queryClient.invalidateQueries({ queryKey: ["sessions"] }),
			queryClient.invalidateQueries({ queryKey: ["calendar"] }),
		]);

	const remove = useMutation({
		mutationFn: () => deleteSession(sessionId as number),
		onSuccess: async () => {
			await invalidateSessions();
			navigate("/sessions");
		},
	});

	const clone = useMutation({
		mutationFn: () =>
			cloneSession(sessionId as number, {
				name: cloneName.trim(),
				session_at: cloneAt ? new Date(cloneAt).toISOString() : null,
			}),
		onSuccess: async (result) => {
			await invalidateSessions();
			navigate(`/sessions/${result.id}`, { state: { cloned: true } });
		},
	});

	const setDraft = (next: SessionDraft) => {
		setSaved(false);
		setDraftState(next);
	};

	const save = useMutation({
		mutationFn: (body: ReturnType<typeof toSessionWrite>) =>
			sessionId === null ? createSession(body) : updateSession(sessionId, body),
		onSuccess: async (result) => {
			await Promise.all([
				queryClient.invalidateQueries({ queryKey: ["sessions"] }),
				queryClient.invalidateQueries({ queryKey: ["calendar"] }),
			]);

			if (sessionId === null) {
				navigate(`/sessions/${result.id}`);
			} else {
				setSaved(true);
			}
		},
	});

	const updateField = <K extends keyof SessionDraft>(
		key: K,
		value: SessionDraft[K],
	) => setDraft({ ...draft, [key]: value });

	const updateExercise = (index: number, patch: Partial<SessionDraft["exercises"][number]>) =>
		updateField(
			"exercises",
			draft.exercises.map((exercise, i) =>
				i === index ? { ...exercise, ...patch } : exercise,
			),
		);

	const moveExercise = (index: number, delta: number) => {
		const target = index + delta;
		if (target < 0 || target >= draft.exercises.length) {
			return;
		}

		const exercises = [...draft.exercises];
		[exercises[index], exercises[target]] = [exercises[target], exercises[index]];
		updateField("exercises", exercises);
	};

	const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		setSaved(false);

		const error = validateDraft(draft);
		setValidationError(error);
		if (error === null) {
			save.mutate(toSessionWrite(draft));
		}
	};

	return (
		<main className="designer-page">
			<h1>{sessionId === null ? "New session" : "Edit session"}</h1>

			{cloned && (
				<p className="designer-banner">
					Cloned!
				</p>
			)}

			<form className="designer-form" onSubmit={handleSubmit} noValidate>
				<section className="designer-card">
					<label>
						Name
						<input
							type="text"
							value={draft.name}
							maxLength={200}
							onChange={(event) => updateField("name", event.target.value)}
						/>
					</label>
					<label>
						Date and time
						<input
							type="datetime-local"
							value={draft.sessionAt}
							onChange={(event) => updateField("sessionAt", event.target.value)}
						/>
					</label>
					<label>
						Status
						<select
							value={draft.status}
							onChange={(event) => updateField("status", event.target.value)}
						>
							<option value="planned">Planned</option>
							<option value="in_progress">In progress</option>
							<option value="completed">Completed</option>
						</select>
					</label>
					<label>
						Plan
						<select
							value={draft.planId}
							onChange={(event) => updateField("planId", event.target.value)}
						>
							<option value="">No plan</option>
							{plans.map((plan) => (
								<option key={plan.id} value={plan.id}>
									{plan.name}
								</option>
							))}
						</select>
					</label>
					<label>
						Intensity (1-10)
						<input
							type="number"
							min={1}
							max={10}
							step={1}
							value={draft.intensity}
							onChange={(event) => updateField("intensity", event.target.value)}
						/>
					</label>
					<label className="designer-wide">
						Notes
						<textarea
							rows={3}
							value={draft.notes}
							onChange={(event) => updateField("notes", event.target.value)}
						/>
					</label>
				</section>

				<section className="designer-exercises">
					<h2>Exercises</h2>

					{draft.exercises.length === 0 && (
						<p className="designer-muted">No exercises yet.</p>
					)}

					{draft.exercises.map((exercise, index) => (
						<div key={exercise.key} className="designer-card designer-exercise">
							<div className="designer-exercise-header">
								<select
									aria-label="Activity"
									value={exercise.activityTypeId}
									onChange={(event) => {
										const activity = activityTypes.find(
											(a) => a.id === Number(event.target.value),
										);
										if (activity) {
											updateExercise(index, {
												activityTypeId: activity.id,
												units: buildUnits(activity),
											});
										}
									}}
								>
									{activityTypes.map((activity) => (
										<option key={activity.id} value={activity.id}>
											{activity.name}
										</option>
									))}
								</select>
								<div className="designer-exercise-actions">
									<button
										type="button"
										disabled={index === 0}
										onClick={() => moveExercise(index, -1)}
									>
										Up
									</button>
									<button
										type="button"
										disabled={index === draft.exercises.length - 1}
										onClick={() => moveExercise(index, 1)}
									>
										Down
									</button>
									<button
										type="button"
										onClick={() =>
											updateField(
												"exercises",
												draft.exercises.filter((_, i) => i !== index),
											)
										}
									>
										Remove
									</button>
								</div>
							</div>

							<MeasurementEditor
								units={exercise.units}
								onChange={(units) => updateExercise(index, { units })}
							/>

							<label>
								Exercise notes
								<textarea
									rows={2}
									value={exercise.notes}
									onChange={(event) =>
										updateExercise(index, { notes: event.target.value })
									}
								/>
							</label>
						</div>
					))}

					<select
						aria-label="Add exercise"
						value=""
						onChange={(event) => {
							const activity = activityTypes.find(
								(a) => a.id === Number(event.target.value),
							);
							if (activity) {
								updateField("exercises", [...draft.exercises, newExercise(activity)]);
							}
						}}
					>
						<option value="">Add exercise...</option>
						{activityTypes.map((activity) => (
							<option key={activity.id} value={activity.id}>
								{activity.name}
							</option>
						))}
					</select>
				</section>

				{validationError && (
					<p className="designer-error" role="alert">
						{validationError}
					</p>
				)}
				{save.isError && (
					<p className="designer-error" role="alert">
						{errorMessage(save.error, "Could not save the session.")}
					</p>
				)}
				{saved && <p className="designer-saved">Saved.</p>}

				<div className="designer-footer">
					<button type="submit" className="designer-save" disabled={save.isPending}>
						{save.isPending ? "Saving..." : "Save"}
					</button>
					<div className="designer-extras">
						{sessionId !== null &&
							(confirmingDelete ? (
								<span className="designer-confirm">
									Delete this session? This cannot be undone.
									<button
										type="button"
										disabled={remove.isPending}
										onClick={() => remove.mutate()}
									>
										{remove.isPending ? "Deleting..." : "Confirm delete"}
									</button>
									<button
										type="button"
										onClick={() => setConfirmingDelete(false)}
									>
										Cancel
									</button>
								</span>
							) : (
								<button type="button" onClick={() => setConfirmingDelete(true)}>
									Delete
								</button>
							))}
					</div>
				</div>
				{remove.isError && (
					<p className="designer-error" role="alert">
						{errorMessage(remove.error, "Could not delete the session.")}
					</p>
				)}
			</form>

			{sessionId !== null && (
				<section className="designer-card designer-clone">
					<h2>Clone</h2>
					<p className="designer-muted designer-wide">
						Clones the saved version. Planned values are kept, actuals are
						cleared, status is set to planned. The plan is not copied, so the
						copy is off the plan. Later edits to either session do not affect
						the other.
					</p>
					<label>
						Copy name
						<input
							type="text"
							value={cloneName}
							maxLength={200}
							onChange={(event) => setCloneName(event.target.value)}
						/>
					</label>
					<label>
						Copy date and time (optional, empty = unscheduled)
						<input
							type="datetime-local"
							value={cloneAt}
							onChange={(event) => setCloneAt(event.target.value)}
						/>
					</label>
					{clone.isError && (
						<p className="designer-error designer-wide" role="alert">
							{errorMessage(clone.error, "Could not clone the session.")}
						</p>
					)}
					<div className="designer-wide">
						<button
							type="button"
							disabled={clone.isPending || cloneName.trim() === ""}
							onClick={() => clone.mutate()}
						>
							{clone.isPending ? "Cloning..." : "Clone"}
						</button>
					</div>
				</section>
			)}
		</main>
	);
}
