import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router";
import { ApiError, createPlan, listPlans } from "../api/client";
import { queryKeys } from "../api/queryKeys";
import PlanForm from "../components/PlanForm";
import { EmptyState, ErrorBanner } from "../components/StatusMessage";
import "./PlansPage.css";

export default function PlansPage() {
	const navigate = useNavigate();
	const queryClient = useQueryClient();
	const plans = useQuery({ queryKey: queryKeys.plans, queryFn: listPlans });

	const create = useMutation({
		mutationFn: createPlan,
		onSuccess: async (plan) => {
			await queryClient.invalidateQueries({ queryKey: queryKeys.plans });
			navigate(`/plans/${plan.id}`);
		},
	});

	return (
		<main className="plans-page">
			<h1>Plans</h1>

			<section>
				{plans.isPending && <p>Loading plans...</p>}
				{plans.isError && <ErrorBanner message="Could not load plans." />}
				{plans.data && plans.data.length === 0 && (
					<EmptyState
						title="No plans yet"
						description="Create your first plan with the form below."
					/>
				)}
				{plans.data && plans.data.length > 0 && (
					<ul>
						{plans.data.map((plan) => (
							<li key={plan.id}>
								<Link to={`/plans/${plan.id}`}>{plan.name}</Link>
								<span className="plan-meta">
									{plan.start_date ?? "No start date"}
									{plan.length_weeks !== null && ` · ${plan.length_weeks} wk`}
								</span>
							</li>
						))}
					</ul>
				)}
			</section>

			<section>
				<h2>New plan</h2>
				{create.isError && (
					<ErrorBanner
						message={
							create.error instanceof ApiError
								? create.error.detail
								: "Could not create plan."
						}
					/>
				)}
				<PlanForm
					submitLabel="Create plan"
					pending={create.isPending}
					error={null}
					onSubmit={(body) => create.mutate(body)}
				/>
			</section>
		</main>
	);
}
