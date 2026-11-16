import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation } from "@tanstack/react-query";
import {
	ApiError,
	createInsight,
	type InsightRequest,
	type InsightResponse,
} from "../api/client";
import { ErrorBanner } from "../components/StatusMessage";
import "./InsightsPage.css";

type InsightSectionProps = {
	title: string;
	items: string[];
	className: string;
};

function InsightSection({ title, items, className }: InsightSectionProps) {
	return (
		<section className={`insight-section ${className}`}>
			<h3>{title}</h3>
			{items.length > 0 ? (
				<ul>
					{items.map((item, index) => (
						<li key={`${title}-${index}`}>{item}</li>
					))}
				</ul>
			) : (
				<p className="insight-empty">No items were returned for this section.</p>
			)}
		</section>
	);
}

function InsightResult({ result }: { result: InsightResponse }) {
	return (
		<section className="insights-result">
			<h2>Your coaching insight</h2>
			<div className="insight-summary">
				<h3>Summary</h3>
				<p>{result.summary || "No summary was returned."}</p>
			</div>
			<div className="insight-sections">
				<InsightSection
					title="Strengths"
					items={result.strengths}
					className="insight-strengths"
				/>
				<InsightSection
					title="Recommendations"
					items={result.recommendations}
					className="insight-recommendations"
				/>
				<InsightSection
					title="Caveats"
					items={result.caveats}
					className="insight-caveats"
				/>
			</div>
		</section>
	);
}

export default function InsightsPage() {
	const [period, setPeriod] = useState<InsightRequest["period"]>("week");
	const [focus, setFocus] = useState("");
	const insight = useMutation({ mutationFn: createInsight });

	const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		const trimmedFocus = focus.trim();
		insight.mutate({
			period,
			...(trimmedFocus ? { focus: trimmedFocus } : {}),
		});
	};

	return (
		<main className="insights-page">
			<h1>Insights</h1>
			<p>Get coaching insights from your training data.</p>

			<form className="insights-form" onSubmit={handleSubmit}>
				<fieldset disabled={insight.isPending}>
					<label>
						Period
						<select
							value={period}
							onChange={(event) =>
								setPeriod(event.target.value as InsightRequest["period"])
							}
						>
							<option value="week">This week</option>
							<option value="month">This month</option>
						</select>
					</label>
					<label>
						Focus (optional)
						<input
							type="text"
							maxLength={200}
							value={focus}
							onChange={(event) => setFocus(event.target.value)}
							placeholder="For example, recovery or running volume"
						/>
					</label>
					<button type="submit">
						{insight.isPending ? "Generating..." : "Generate insights"}
					</button>
				</fieldset>
			</form>

			{insight.isError && (
				<ErrorBanner
					message={
						insight.error instanceof ApiError
							? insight.error.detail
							: "Could not generate insights."
					}
				/>
			)}
			{insight.data && (
				<InsightResult result={insight.data} />
			)}
		</main>
	);
}