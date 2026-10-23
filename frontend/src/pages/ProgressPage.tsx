import SessionsOverTimeChart, {
	type SessionsOverTimePoint,
} from "../components/charts/SessionsOverTimeChart";

// Static placeholder until S4-11 wires /stats/progress.
const SAMPLE_DATA: SessionsOverTimePoint[] = [
	{ date: "Week 1", sessions: 2 },
	{ date: "Week 2", sessions: 3 },
	{ date: "Week 3", sessions: 1 },
	{ date: "Week 4", sessions: 4 },
	{ date: "Week 5", sessions: 3 },
	{ date: "Week 6", sessions: 5 },
	{ date: "Week 7", sessions: 4 },
	{ date: "Week 8", sessions: 6 },
];

export default function ProgressPage() {
	return (
		<main className="progress-page">
			<h1>Progress</h1>
			<section>
				<h2>Sessions over time</h2>
				<p>Sample data.</p>
				<SessionsOverTimeChart data={SAMPLE_DATA} />
			</section>
		</main>
	);
}
