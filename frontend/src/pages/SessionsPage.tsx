import { useState, type FormEvent } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";
import { listActivityTypes, listPlans, listSessions } from "../api/client";
import { queryKeys, type SessionFilters } from "../api/queryKeys";
import ActivityTypeSelect from "../components/ActivityTypeSelect";
import {
	formatSessionDate,
	statusLabel,
	summarizeExercises,
} from "../sessions/display";
import {
	emptyDraft,
	hasActiveFilters,
	toApiFilters,
	validateDraft,
	type FilterDraft,
	type ScheduleFilter,
} from "../sessions/filters";
import "./SessionsPage.css";

export default function SessionsPage() {
	const [draft, setDraft] = useState<FilterDraft>(emptyDraft);
	const [applied, setApplied] = useState<SessionFilters>({});
	const [validationError, setValidationError] = useState<string | null>(null);

	const sessions = useQuery({
		queryKey: queryKeys.sessions(applied),
		queryFn: () => listSessions(applied),
	});
	const plans = useQuery({ queryKey: queryKeys.plans, queryFn: listPlans });
	const activityTypes = useQuery({
		queryKey: queryKeys.activityTypes,
		queryFn: listActivityTypes,
	});

	const activityNames = new Map(
		(activityTypes.data ?? []).map((activity) => [activity.id, activity.name]),
	);
	const datesDisabled = draft.schedule === "unscheduled";

	const update = <K extends keyof FilterDraft>(key: K, value: FilterDraft[K]) => {
		setDraft((current) => ({ ...current, [key]: value }));
	};

	const handleApply = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();

		const error = validateDraft(draft);
		setValidationError(error);
		if (error === null) {
			setApplied(toApiFilters(draft));
		}
	};

	const handleClear = () => {
		setDraft(emptyDraft);
		setApplied({});
		setValidationError(null);
	};

	return (
		<main className="sessions-page">
			<h1>Sessions</h1>

			<form className="sessions-filters" onSubmit={handleApply} noValidate>
				<label>
					From
					<input
						type="date"
						value={draft.from}
						disabled={datesDisabled}
						onChange={(event) => update("from", event.target.value)}
					/>
				</label>
				<label>
					To
					<input
						type="date"
						value={draft.to}
						disabled={datesDisabled}
						onChange={(event) => update("to", event.target.value)}
					/>
				</label>
				<label>
					Status
					<select
						value={draft.status}
						onChange={(event) => update("status", event.target.value)}
					>
						<option value="">All</option>
						<option value="planned">Planned</option>
						<option value="in_progress">In progress</option>
						<option value="completed">Completed</option>
					</select>
				</label>
				<label>
					Schedule
					<select
						value={draft.schedule}
						onChange={(event) =>
							update("schedule", event.target.value as ScheduleFilter)
						}
					>
						<option value="all">All</option>
						<option value="dated">Dated</option>
						<option value="unscheduled">Unscheduled</option>
					</select>
				</label>
				<label>
					Plan
					<select
						value={draft.planId}
						onChange={(event) => update("planId", event.target.value)}
					>
						<option value="">All plans</option>
						{(plans.data ?? []).map((plan) => (
							<option key={plan.id} value={plan.id}>
								{plan.name}
							</option>
						))}
					</select>
				</label>
				<label>
					Activity
					<ActivityTypeSelect
						activityTypes={activityTypes.data ?? []}
						value={draft.activityTypeId === "" ? "" : Number(draft.activityTypeId)}
						onChange={(id) => update("activityTypeId", id === "" ? "" : String(id))}
						allowEmpty
						emptyLabel="All activities"
					/>
				</label>

				<div className="sessions-actions">
					<button type="submit" className="sessions-apply">
						Apply
					</button>
					<button type="button" className="sessions-clear" onClick={handleClear}>
						Clear
					</button>
				</div>
			</form>

			{validationError && (
				<p className="sessions-error" role="alert">
					{validationError}
				</p>
			)}

			{sessions.isPending && <p className="sessions-message">Loading sessions...</p>}

			{sessions.isError && (
				<p className="sessions-error" role="alert">
					Could not load sessions: {sessions.error.message}
				</p>
			)}

			{sessions.isSuccess && sessions.data.length === 0 && (
				<p className="sessions-message">
					{hasActiveFilters(applied)
						? "No sessions match these filters."
						: "No sessions yet. Create your first session to get started."}
				</p>
			)}

			{sessions.isSuccess && sessions.data.length > 0 && (
				<ul className="sessions-list">
					{sessions.data.map((session) => (
						<li key={session.id}>
							<Link className="sessions-row" to={`/sessions/${session.id}`}>
								<span className="sessions-name">{session.name}</span>
								<span className="sessions-date">
									{formatSessionDate(session.session_at)}
								</span>
								<span className={`sessions-status sessions-status-${session.status}`}>
									{statusLabel(session.status)}
								</span>
								<span className="sessions-summary">
									{summarizeExercises(session.items, activityNames)}
								</span>
							</Link>
						</li>
					))}
				</ul>
			)}
		</main>
	);
}
