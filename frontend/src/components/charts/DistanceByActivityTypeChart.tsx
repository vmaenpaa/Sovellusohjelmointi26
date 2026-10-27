import {
	Bar,
	BarChart,
	CartesianGrid,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

export type DistanceByActivityTypePoint = {
	activity: string;
	distance: number;
};

type Props = {
	data: DistanceByActivityTypePoint[];
};

export default function DistanceByActivityTypeChart({ data }: Props) {
	return (
		<ResponsiveContainer width="100%" height={Math.max(240, data.length * 44)}>
			<BarChart
				data={data}
				layout="vertical"
				margin={{ top: 8, right: 24, bottom: 8, left: 8 }}
			>
				<CartesianGrid strokeDasharray="3 3" />
				<XAxis type="number" unit=" km" />
				<YAxis type="category" dataKey="activity" width={120} />
				<Tooltip />
				<Bar dataKey="distance" fill="#15803d" />
			</BarChart>
		</ResponsiveContainer>
	);
}