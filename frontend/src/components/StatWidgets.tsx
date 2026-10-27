import { useQuery } from "@tanstack/react-query";
import { ApiError, getStatsSummary } from "../api/client";
import { queryKeys } from "../api/queryKeys";
import { ErrorBanner } from "./StatusMessage";

type Props = {
	from: string;
	to: string;
};

function formatDuration(totalMinutes: number) {
	const minutes = Math.round(totalMinutes);
	const hours = Math.floor(minutes / 60);
	const rest = minutes % 60;
	if (hours === 0) return `${rest}m`;
	return rest === 0 ? `${hours}h` : `${hours}h ${rest}m`;
}

export default function StatWidgets({ from, to }: Props) {
	const filters = { from, to };
	const summary = useQuery({
		queryKey: queryKeys.statsSummary(filters),
		queryFn: () => getStatsSummary(filters),
	});

	if (summary.isPending) {
		return <p className="sessions-message">Loading stats...</p>;
	}

	if (summary.isError) {
		const detail =
			summary.error instanceof ApiError ? summary.error.detail : "Unknown error";
		return <ErrorBanner message={`Could not load stats: ${detail}`} />;
	}

	const data = summary.data;
	const widgets = [
		{ label: "Sessions", value: String(data.session_count) },
		{ label: "Total duration", value: formatDuration(data.total_duration_min) },
		{
			label: "Total distance",
			value: `${data.total_distance_km.toFixed(1)} km`,
		},
		{
			label: "Average intensity",
            
			// The API returns 0 when no session has an intensity.
			value: data.average_intensity > 0 ? data.average_intensity.toFixed(1) : "–",
		},
	];

	return (
		<div className="stat-widgets">
			{widgets.map((widget) => (
				<div className="stat-widget" key={widget.label}>
					<span className="stat-widget-label">{widget.label}</span>
					<span className="stat-widget-value">{widget.value}</span>
				</div>
			))}
		</div>
	);
}
