import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router";
import { ApiError, createPlan, listPlans } from "../api/client";
import { queryKeys } from "../api/queryKeys";
import PlanForm from "../components/PlanForm";
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
				{plans.isError && <p className="plan-error">Could not load plans.</p>}
				{plans.data && plans.data.length === 0 && <p>No plans yet.</p>}
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
				<PlanForm
					submitLabel="Create plan"
					pending={create.isPending}
					error={
						create.error instanceof ApiError
							? create.error.detail
							: create.isError
								? "Could not create plan."
								: null
					}
					onSubmit={(body) => create.mutate(body)}
				/>
			</section>
		</main>
	);
}
