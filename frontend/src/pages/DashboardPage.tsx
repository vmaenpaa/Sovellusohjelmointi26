import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";
import {
	apiRequest,
	listActivityTypes,
	listSessions,
} from "../api/client";
import { queryKeys } from "../api/queryKeys";
import {
	formatSessionDate,
	statusLabel,
	summarizeExercises,
} from "../sessions/display";
import "./DashboardPage.css";
import "./SessionsPage.css";

const RECENT_LIMIT = 8;

export default function DashboardPage() {
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

			<section>
				<h2>Recent sessions</h2>

				{sessions.isPending && (
					<p className="sessions-message">Loading sessions...</p>
				)}

				{sessions.isError && (
					<p className="sessions-error" role="alert">
						Could not load sessions: {sessions.error.message}
					</p>
				)}

				{sessions.isSuccess && recent.length === 0 && (
					<p className="sessions-message">
						No dated sessions yet.{" "}
						<Link to="/sessions/new">Create your first session</Link>
					</p>
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
