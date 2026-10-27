import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";
import {
	apiRequest,
	listActivityTypes,
	listSessions,
} from "../api/client";
import { queryKeys } from "../api/queryKeys";
import StatWidgets from "../components/StatWidgets";
import { EmptyState, ErrorBanner } from "../components/StatusMessage";
import {
	formatSessionDate,
	statusLabel,
	summarizeExercises,
} from "../sessions/display";
import "./DashboardPage.css";
import "./SessionsPage.css";

const RECENT_LIMIT = 8;
const PERIOD_OPTIONS = [7, 30, 90];

function periodBounds(days: number) {
	const start = new Date();
	start.setDate(start.getDate() - (days - 1));
	start.setHours(0, 0, 0, 0);
	const end = new Date();
	end.setHours(23, 59, 59, 999);
	return { from: start.toISOString(), to: end.toISOString() };
}

export default function DashboardPage() {
	const [periodDays, setPeriodDays] = useState(30);
	const [period, setPeriod] = useState(() => periodBounds(30));
	const sessions = useQuery({
		queryKey: queryKeys.sessions({ unscheduled: false }),
		queryFn: () => listSessions({ unscheduled: false }),
	});
	const activityTypes = useQuery({
		queryKey: queryKeys.activityTypes,
		queryFn: listActivityTypes,
	});
	const health = useQuery({
		queryKey: ["health"],
		queryFn: () => apiRequest<{ status: string }>("/health"),
		enabled: false,
	});

	const activityNames = new Map(
		(activityTypes.data ?? []).map((activity) => [activity.id, activity.name]),
	);

	const recent = (sessions.data ?? [])
		.filter((session) => session.session_at !== null)
		.sort(
			(a, b) =>
				new Date(b.session_at as string).getTime() -
				new Date(a.session_at as string).getTime(),
		)
		.slice(0, RECENT_LIMIT);

	const healthLabel = health.isError
		? "NOT OK"
		: health.data
			? health.data.status === "ok"
				? "OK"
				: "NOT OK"
			: "Not checked";
	const healthClass = health.isError
		? "not-ok"
		: health.data
			? health.data.status === "ok"
				? "ok"
				: "not-ok"
			: "loading";

	return (
		<main className="sessions-page">
			<h1>Dashboard</h1>

			<div className="dashboard-grid">
			<section>
				<h2>Recent sessions</h2>

				{sessions.isPending && (
					<p className="sessions-message">Loading sessions...</p>
				)}

				{sessions.isError && (
					<ErrorBanner message={`Could not load sessions: ${sessions.error.message}`} />
				)}

				{sessions.isSuccess && recent.length === 0 && (
					<EmptyState
						title="No dated sessions yet"
						action={{ to: "/sessions/new", label: "Create your first session" }}
					/>
				)}

				{recent.length > 0 && (
					<ul className="sessions-list">
						{recent.map((session) => (
							<li key={session.id}>
								<Link className="sessions-row" to={`/sessions/${session.id}`}>
									<span className="sessions-name">{session.name}</span>
									<span className="sessions-date">
										{formatSessionDate(session.session_at)}
									</span>
									<span
										className={`sessions-status sessions-status-${session.status}`}
									>
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
			</section>

			<section>
				<h2>Stats</h2>
				<label className="dashboard-period">
					Period
					<select
						value={periodDays}
						onChange={(event) => {
							const days = Number(event.target.value);
							setPeriodDays(days);
							setPeriod(periodBounds(days));
						}}
					>
						{PERIOD_OPTIONS.map((days) => (
							<option key={days} value={days}>
								Last {days} days
							</option>
						))}
					</select>
				</label>
				<StatWidgets from={period.from} to={period.to} />
			</section>
			</div>

			<section className="dashboard-health">
				<span>API status</span>
				<button
					type="button"
					className="dashboard-health-button"
					onClick={() => void health.refetch()}
				>
					Check
				</button>
				<span className={`dashboard-health-status ${healthClass}`}>
					{healthLabel}
				</span>
			</section>
		</main>
	);
}
