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
	if (items.length === 0) {
		return null;
	}

	return (
		<section className={`insight-section ${className}`}>
			<h3>{title}</h3>
			<ul>
				{items.map((item, index) => (
					<li key={`${title}-${index}`}>{item}</li>
				))}
			</ul>
		</section>
	);
}

function InsightResult({ result }: { result: InsightResponse }) {
	return (
		<section className="insights-result">
			<h2>Your coaching insight</h2>
			<section className="insight-summary">
				<h3>Summary</h3>
				<p>{result.summary || "No summary was returned."}</p>
			</section>
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

function getInsightErrorMessage(error: unknown) {
	const detail = error instanceof ApiError ? error.detail.trim() : "";
	const providerMessage =
		error instanceof ApiError && (error.status === 502 || error.status === 503)
			? "Check that Ollama is running and try again later."
			: "Check your connection and try again later.";

	return detail
		? `${detail} ${providerMessage}`
		: `Could not generate insights. ${providerMessage}`;
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

			<form
				className="insights-form"
				onSubmit={handleSubmit}
				aria-busy={insight.isPending}
			>
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

			{insight.isPending && (
				<p className="insights-loading" role="status" aria-live="polite">
					<span className="insights-spinner" aria-hidden="true" />
					Generating insights from your training data...
				</p>
			)}
			{insight.isError && (
				<ErrorBanner
					message={getInsightErrorMessage(insight.error)}
				/>
			)}
			{insight.data && (
				<InsightResult result={insight.data} />
			)}
		</main>
	);
}