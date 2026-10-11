import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router";
import {
	ApiError,
	cloneSession,
	getCalendar,
	listPlans,
	type CalendarSession,
} from "../api/client";
import { queryKeys } from "../api/queryKeys";
import {
	dayKey,
	parseDayKey,
	rangeBounds,
	rangeTitle,
	shiftCursor,
	startOfDay,
	visibleDays,
	withDateKeepTime,
	type CalendarView,
} from "../calendar/range";
import { statusLabel } from "../sessions/display";
import "./CalendarPage.css";

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function errorMessage(error: unknown, fallback: string) {
	return error instanceof ApiError ? error.detail : fallback;
}

export default function CalendarPage() {
	const queryClient = useQueryClient();
	const [view, setView] = useState<CalendarView>("month");
	const [cursor, setCursor] = useState(() => startOfDay(new Date()));
	const [planId, setPlanId] = useState<number | null>(null);

	const [cloneSource, setCloneSource] = useState<CalendarSession | null>(null);
	const [cloneName, setCloneName] = useState("");
	const [cloneDate, setCloneDate] = useState("");
	const [cloneError, setCloneError] = useState<string | null>(null);
	const [cloned, setCloned] = useState<{ id: number; name: string } | null>(null);

	const days = visibleDays(view, cursor);
	const { from, to } = rangeBounds(days);
	const todayKey = dayKey(new Date());

	const plans = useQuery({ queryKey: queryKeys.plans, queryFn: listPlans });
	const calendar = useQuery({
		queryKey: queryKeys.calendar(from, to, planId),
		queryFn: () => getCalendar(from, to, planId),
	});

	const cloneMutation = useMutation({
		mutationFn: (args: { source: CalendarSession; name: string; date: string }) =>
			cloneSession(args.source.id, {
				name: args.name || undefined,
				session_at: withDateKeepTime(args.source.session_at, args.date),
			}),
		onSuccess: (result, args) => {
			setCursor(parseDayKey(args.date));
			setCloned({ id: result.id, name: result.name });
			setCloneSource(null);
			void queryClient.invalidateQueries({ queryKey: ["calendar"] });
			void queryClient.invalidateQueries({ queryKey: ["sessions"] });
		},
		onError: (error) => setCloneError(errorMessage(error, "Could not clone session.")),
	});

	const byDay = new Map<string, CalendarSession[]>();
	for (const session of calendar.data ?? []) {
		const key = dayKey(new Date(session.session_at));
		byDay.set(key, [...(byDay.get(key) ?? []), session]);
	}

	function openClone(session: CalendarSession) {
		setCloneSource(session);
		setCloneName(`${session.name} (copy)`);
		setCloneDate("");
		setCloneError(null);
		setCloned(null);
	}

	function confirmClone() {
		if (!cloneSource) return;
		if (!cloneDate) {
			setCloneError("Choose a date.");
			return;
		}
		setCloneError(null);
		cloneMutation.mutate({
			source: cloneSource,
			name: cloneName.trim(),
			date: cloneDate,
		});
	}

	const selectedPlan = plans.data?.find((plan) => plan.id === planId);

	return (
		<main className="calendar-page">
			<h1>Calendar</h1>

			<div className="calendar-toolbar">
				<div className="calendar-nav">
					<button type="button" onClick={() => setCursor(shiftCursor(view, cursor, -1))}>
						Previous
					</button>
					<button type="button" onClick={() => setCursor(startOfDay(new Date()))}>
						Today
					</button>
					<button type="button" onClick={() => setCursor(shiftCursor(view, cursor, 1))}>
						Next
					</button>
				</div>
				<strong className="calendar-title">{rangeTitle(view, cursor, days)}</strong>
				<div className="calendar-toggle" role="group" aria-label="View">
					{(["month", "week"] as const).map((option) => (
						<button
							key={option}
							type="button"
							aria-pressed={view === option}
							className={view === option ? "active" : ""}
							onClick={() => setView(option)}
						>
							{option === "month" ? "Month" : "Week"}
						</button>
					))}
				</div>
				<label className="calendar-plan">
					Plan{" "}
					<select
						value={planId ?? ""}
						onChange={(event) =>
							setPlanId(event.target.value ? Number(event.target.value) : null)
						}
					>
						<option value="">All plans</option>
						{plans.data?.map((plan) => (
							<option key={plan.id} value={plan.id}>
								{plan.name}
							</option>
						))}
					</select>
				</label>
			</div>

			{cloned && (
				<p className="calendar-message" role="status">
					Cloned as <Link to={`/sessions/${cloned.id}`}>{cloned.name}</Link>.
				</p>
			)}

			{calendar.isPending && <p className="calendar-message">Loading calendar…</p>}
			{calendar.isError && (
				<p className="calendar-error" role="alert">
					{errorMessage(calendar.error, "Could not load calendar.")}
				</p>
			)}
			{calendar.isSuccess && calendar.data.length === 0 && (
				<p className="calendar-message">
					No sessions in this range
					{selectedPlan ? ` for plan "${selectedPlan.name}"` : ""}.
				</p>
			)}

			<div className={`calendar-grid calendar-grid-${view}`}>
				{WEEKDAYS.map((weekday) => (
					<div key={weekday} className="calendar-weekday">
						{weekday}
					</div>
				))}
				{days.map((day) => {
					const key = dayKey(day);
					const classes = ["calendar-day"];
					if (key === todayKey) classes.push("today");
					if (view === "month" && day.getMonth() !== cursor.getMonth()) {
						classes.push("outside");
					}
					return (
						<div key={key} className={classes.join(" ")}>
							<div className="calendar-day-number">
								{day.getDate()}
								{key === todayKey && <span className="calendar-today-mark"> Today</span>}
							</div>
							{(byDay.get(key) ?? []).map((session) => (
								<div key={session.id} className={`calendar-chip status-${session.status}`}>
									<Link to={`/sessions/${session.id}`}>{session.name}</Link>
									<span className="calendar-chip-meta">
										{new Date(session.session_at).toLocaleTimeString(undefined, {
											timeStyle: "short",
										})}{" "}
										· {statusLabel(session.status)}
									</span>
									<button type="button" onClick={() => openClone(session)}>
										Clone
									</button>
									{cloneSource?.id === session.id && (
										<div className="calendar-clone-panel">
											<label>
												Name
												<input
													value={cloneName}
													onChange={(event) => setCloneName(event.target.value)}
												/>
											</label>
											<label>
												Date
												<input
													type="date"
													value={cloneDate}
													required
													onChange={(event) => setCloneDate(event.target.value)}
												/>
											</label>
											{cloneError && (
												<p className="calendar-error" role="alert">
													{cloneError}
												</p>
											)}
											<button
												type="button"
												disabled={cloneMutation.isPending}
												onClick={confirmClone}
											>
												Confirm
											</button>
											<button type="button" onClick={() => setCloneSource(null)}>
												Cancel
											</button>
										</div>
									)}
								</div>
							))}
						</div>
					);
				})}
			</div>
		</main>
	);
}
