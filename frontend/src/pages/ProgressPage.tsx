import { useQuery } from "@tanstack/react-query";
import {
	ApiError,
	getProgress,
	getStatsSummary,
} from "../api/client";
import { queryKeys } from "../api/queryKeys";
import { EmptyState, ErrorBanner } from "../components/StatusMessage";
import DistanceByActivityTypeChart from "../components/charts/DistanceByActivityTypeChart";
import SessionsOverTimeChart from "../components/charts/SessionsOverTimeChart";
import "./SessionsPage.css";

const progressFilters = { metric: "session_count", granularity: "week" } as const;
const summaryFilters = {};

function errorMessage(error: unknown, fallback: string) {
	return error instanceof ApiError ? error.detail : fallback;
}

export default function ProgressPage() {
	const progress = useQuery({
		queryKey: queryKeys.statsProgress(progressFilters),
		queryFn: () => getProgress(progressFilters),
	});
	const summary = useQuery({
		queryKey: queryKeys.statsSummary(summaryFilters),
		queryFn: () => getStatsSummary(summaryFilters),
	});

	const sessionPoints = (progress.data?.points ?? []).map((point) => ({
		date: point.period_label,
		sessions: point.value,
	}));
	const distancePoints = (summary.data?.by_activity_type ?? [])
		.filter((activity) => activity.total_distance_km > 0)
		.map((activity) => ({
			activity: activity.activity_type_slug
				.split("_")
				.map((part) => part.charAt(0).toUpperCase() + part.slice(1))
				.join(" "),
			distance: activity.total_distance_km,
		}));

	return (
		<main className="sessions-page">
			<h1>Progress</h1>

			<section>
				<h2>Sessions over time</h2>
				{progress.isPending && <p>Loading progress...</p>}
				{progress.isError && (
					<ErrorBanner
						message={errorMessage(progress.error, "Could not load session progress.")}
					/>
				)}
				{progress.isSuccess && sessionPoints.length === 0 && (
					<EmptyState
						title="No session history yet"
						description="Scheduled sessions will appear here over time."
					/>
				)}
				{sessionPoints.length > 0 && <SessionsOverTimeChart data={sessionPoints} />}
			</section>

			<section>
				<h2>Distance by activity type</h2>
				{summary.isPending && <p>Loading activity measurements...</p>}
				{summary.isError && (
					<ErrorBanner
						message={errorMessage(summary.error, "Could not load activity measurements.")}
					/>
				)}
				{summary.isSuccess && distancePoints.length === 0 && (
					<EmptyState
						title="No distance measurements yet"
						description="Recorded distance measurements will appear here by activity type."
					/>
				)}
				{distancePoints.length > 0 && (
					<DistanceByActivityTypeChart data={distancePoints} />
				)}
			</section>
		</main>
	);
}
