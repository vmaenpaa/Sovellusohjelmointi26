import { useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router";
import {
	ApiError,
	attachSession,
	deletePlan,
	detachSession,
	getPlan,
	listPlans,
	listSessions,
	updatePlan,
} from "../api/client";
import { queryKeys } from "../api/queryKeys";
import PlanForm from "../components/PlanForm";
import { formatSessionDate, statusLabel } from "../sessions/display";
import "./PlansPage.css";

function errorText(error: unknown, fallback: string) {
	return error instanceof ApiError ? error.detail : fallback;
}

export default function PlanDetailPage() {
	const planId = Number(useParams().planId);
	const navigate = useNavigate();
	const queryClient = useQueryClient();
	const [selected, setSelected] = useState("");

	const plan = useQuery({
		queryKey: queryKeys.plan(planId),
		queryFn: () => getPlan(planId),
		retry: false,
	});
	const sessions = useQuery({
		queryKey: queryKeys.sessions({}),
		queryFn: () => listSessions(),
	});
	const plans = useQuery({ queryKey: queryKeys.plans, queryFn: listPlans });

	const invalidateAll = () =>
		Promise.all([
			queryClient.invalidateQueries({ queryKey: ["plans"] }),
			queryClient.invalidateQueries({ queryKey: ["sessions"] }),
			queryClient.invalidateQueries({ queryKey: ["calendar"] }),
		]);

	const save = useMutation({
		mutationFn: (body: Parameters<typeof updatePlan>[1]) =>
			updatePlan(planId, body),
		onSuccess: () => queryClient.invalidateQueries({ queryKey: ["plans"] }),
	});
	const remove = useMutation({
		mutationFn: () => deletePlan(planId),
		onSuccess: async () => {
			queryClient.removeQueries({ queryKey: queryKeys.plan(planId) });
			await invalidateAll();
			navigate("/plans");
		},
	});
	const attach = useMutation({
		mutationFn: (sessionId: number) => attachSession(planId, sessionId),
		onSuccess: async () => {
			setSelected("");
			await invalidateAll();
		},
	});
	const detach = useMutation({
		mutationFn: (sessionId: number) => detachSession(planId, sessionId),
		onSuccess: invalidateAll,
	});

	if (!Number.isInteger(planId) || (plan.error instanceof ApiError && plan.error.status === 404)) {
		return (
			<main className="plans-page">
				<p>Plan not found.</p>
				<button type="button" className="plan-secondary" onClick={() => navigate("/plans")}>
					Back to plans
				</button>
			</main>
		);
	}
	if (plan.isPending) {
		return <main className="plans-page"><p>Loading plan...</p></main>;
	}
	if (plan.isError) {
		return (
			<main className="plans-page">
				<p className="plan-error">Could not load plan.</p>
				<button type="button" className="plan-secondary" onClick={() => navigate("/plans")}>
					Back to plans
				</button>
			</main>
		);
	}

	const data = plan.data;
	const dated = data.sessions.filter((s) => s.session_at !== null);
	const unscheduled = data.sessions.filter((s) => s.session_at === null);
	const planNames = new Map((plans.data ?? []).map((p) => [p.id, p.name]));
	const attachable = (sessions.data ?? []).filter((s) => s.plan_id !== planId);

	const handleDelete = () => {
		if (
			window.confirm(
				"Delete this plan? Its sessions stay in your log and are removed from the plan.",
			)
		) {
			remove.mutate();
		}
	};

	const handleAttach = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		if (selected !== "") attach.mutate(Number(selected));
	};

	const renderRows = (rows: typeof data.sessions) => (
		<ul>
			{rows.map((member) => (
				<li key={member.id}>
					<span>
						<Link to={`/sessions/${member.id}`}>{member.name}</Link>{" "}
						<span className="plan-meta">
							{formatSessionDate(member.session_at)} · {statusLabel(member.status)}
						</span>
					</span>
					<button
						type="button"
						className="plan-secondary"
						disabled={detach.isPending}
						onClick={() => detach.mutate(member.id)}
					>
						Detach
					</button>
				</li>
			))}
		</ul>
	);

	return (
		<main className="plans-page">
			<button type="button" className="plan-secondary" onClick={() => navigate("/plans")}>
				Back to plans
			</button>
			<h1>{data.name}</h1>

			<section>
				<h2>Details</h2>
				<PlanForm
					key={data.updated_at}
					initial={data}
					submitLabel="Save changes"
					pending={save.isPending}
					error={save.isError ? errorText(save.error, "Could not save plan.") : null}
					onSubmit={(body) => save.mutate(body)}
				/>
			</section>

			<section>
				<h2>Scheduled sessions</h2>
				{dated.length === 0 ? <p>No scheduled sessions.</p> : renderRows(dated)}
			</section>

			<section>
				<h2>Unscheduled sessions</h2>
				{unscheduled.length === 0 ? <p>No unscheduled sessions.</p> : renderRows(unscheduled)}
				{detach.isError && (
					<p className="plan-error" role="alert">
						{errorText(detach.error, "Could not detach session.")}
					</p>
				)}
			</section>

			<section>
				<h2>Attach a session</h2>
				<form className="plan-attach" onSubmit={handleAttach}>
					<label>
						Session
						<select value={selected} onChange={(e) => setSelected(e.target.value)}>
							<option value="">Select a session</option>
							{attachable.map((s) => (
								<option key={s.id} value={s.id}>
									{s.name}
									{s.plan_id !== null &&
										` (moves from ${planNames.get(s.plan_id) ?? "another plan"})`}
								</option>
							))}
						</select>
					</label>
					<button
						type="submit"
						className="plan-primary"
						disabled={selected === "" || attach.isPending}
					>
						Attach
					</button>
				</form>
				{attach.isError && (
					<p className="plan-error" role="alert">
						{errorText(attach.error, "Could not attach session.")}
					</p>
				)}
			</section>

			<section>
				<h2>Delete plan</h2>
				<button
					type="button"
					className="plan-danger"
					disabled={remove.isPending}
					onClick={handleDelete}
				>
					Delete plan
				</button>
				{remove.isError && (
					<p className="plan-error" role="alert">
						{errorText(remove.error, "Could not delete plan.")}
					</p>
				)}
			</section>
		</main>
	);
}
