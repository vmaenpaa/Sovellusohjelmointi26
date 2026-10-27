import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
	ApiError,
	getProgress,
	getStatsSummary,
} from "../api/client";
import { queryKeys } from "../api/queryKeys";
import { addDays, dayKey, startOfWeek } from "../calendar/range";
import { EmptyState, ErrorBanner } from "../components/StatusMessage";
import DistanceByActivityTypeChart from "../components/charts/DistanceByActivityTypeChart";
import SessionsOverTimeChart from "../components/charts/SessionsOverTimeChart";
import "./ProgressPage.css";
import "./SessionsPage.css";

type Granularity = "week" | "month";

function dateBound(date: string, endOfDay: boolean) {
	return new Date(`${date}T${endOfDay ? "23:59:59.999" : "00:00:00"}`).toISOString();
}

function errorMessage(error: unknown, fallback: string) {
	return error instanceof ApiError ? error.detail : fallback;
}

export default function ProgressPage() {

	const [dateRange, setDateRange] = useState(() => {
		const today = new Date();
		return {
			from: dayKey(addDays(startOfWeek(today), -35)),
			to: dayKey(today),
		};
	});

	const [granularity, setGranularity] = useState<Granularity>("week");

	const isDateRangeValid =
		dateRange.from !== "" &&
		dateRange.to !== "" &&
		dateRange.from <= dateRange.to;

	const rangeError =
		dateRange.from === "" || dateRange.to === ""
			? "Choose both dates to load stats."
			: dateRange.from > dateRange.to
				? "The start date must not be after the end date."
				: null;
		const dateFilters = {
			from: dateRange.from ? dateBound(dateRange.from, false) : undefined,
			to: dateRange.to ? dateBound(dateRange.to, true) : undefined,
		};

	const progressFilters = {
		metric: "session_count",
		granularity,
		...dateFilters,
	} as const;
	
	const summaryFilters = dateFilters;

	const progress = useQuery({
		queryKey: queryKeys.statsProgress(progressFilters),
		queryFn: () => getProgress(progressFilters),
		enabled: isDateRangeValid,
	});

	const summary = useQuery({
		queryKey: queryKeys.statsSummary(summaryFilters),
		queryFn: () => getStatsSummary(summaryFilters),
		enabled: isDateRangeValid,
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
			<div className="progress-controls">
				<div className="progress-date-range">
					<label>
						From
						<input
							type="date"
							required
							value={dateRange.from}
							onChange={(event) =>
								setDateRange((current) => ({
									...current,
									from: event.target.value,
								}))
							}
						/>
					</label>
					<label>
						To
						<input
							type="date"
							required
							value={dateRange.to}
							onChange={(event) =>
								setDateRange((current) => ({
									...current,
									to: event.target.value,
								}))
							}
						/>
					</label>
				</div>
				<fieldset className="progress-granularity">
					<legend>Group by</legend>
					<div className="progress-granularity-options">
						{(["week", "month"] as const).map((option) => (
							<label
								key={option}
								className={granularity === option ? "active" : ""}
							>
								<input
									type="radio"
									name="progress-granularity"
									value={option}
									checked={granularity === option}
									onChange={() => setGranularity(option)}
								/>
								{option === "week" ? "Week" : "Month"}
							</label>
						))}
					</div>
				</fieldset>
			</div>
			{rangeError && (
				<p className="progress-range-error" role="alert">
					{rangeError}
				</p>
			)}

			<section>
				<h2>Sessions over time</h2>
				{isDateRangeValid && progress.isPending && <p>Loading progress...</p>}
				{isDateRangeValid && progress.isError && (
					<ErrorBanner
						message={errorMessage(progress.error, "Could not load session progress.")}
					/>
				)}
				{isDateRangeValid && progress.isSuccess && sessionPoints.length === 0 && (
					<EmptyState
						title="No session history yet"
						description="Scheduled sessions will appear here over time."
					/>
				)}
				{isDateRangeValid && sessionPoints.length > 0 && (
					<SessionsOverTimeChart data={sessionPoints} />
				)}
			</section>

			<section>
				<h2>Distance by activity type</h2>
				{isDateRangeValid && summary.isPending && <p>Loading activity measurements...</p>}
				{isDateRangeValid && summary.isError && (
					<ErrorBanner
						message={errorMessage(summary.error, "Could not load activity measurements.")}
					/>
				)}
				{isDateRangeValid && summary.isSuccess && distancePoints.length === 0 && (
					<EmptyState
						title="No distance measurements yet"
						description="Recorded distance measurements will appear here by activity type."
					/>
				)}
				{isDateRangeValid && distancePoints.length > 0 && (
					<DistanceByActivityTypeChart data={distancePoints} />
				)}
			</section>
		</main>
	);
}
