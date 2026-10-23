import {
	CartesianGrid,
	Line,
	LineChart,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

export type SessionsOverTimePoint = {
	date: string;
	sessions: number;
};

type Props = {
	data: SessionsOverTimePoint[];
};

export default function SessionsOverTimeChart({ data }: Props) {
	return (
		<ResponsiveContainer width="100%" height={300}>
			<LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
				<CartesianGrid strokeDasharray="3 3" />
				<XAxis dataKey="date" />
				<YAxis allowDecimals={false} />
				<Tooltip />
				<Line type="monotone" dataKey="sessions" stroke="#2563eb" strokeWidth={2} />
			</LineChart>
		</ResponsiveContainer>
	);
}
