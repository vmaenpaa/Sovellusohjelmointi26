import type { ActivityType } from "../api/client";

type Props = {
	activityTypes: ActivityType[];
	value: number | "";
	onChange: (id: number | "") => void;
	allowEmpty?: boolean;
	emptyLabel?: string;
	ariaLabel?: string;
};

function unitSummary(activity: ActivityType) {
	return [...activity.unit_links]
		.sort((a, b) => a.sort_order - b.sort_order)
		.map((link) => link.unit_type.label ?? link.unit_type.name)
		.join(", ");
}

function optionLabel(activity: ActivityType) {
	const units = unitSummary(activity);
	return units ? `${activity.name} — ${units}` : activity.name;
}

export default function ActivityTypeSelect({
	activityTypes,
	value,
	onChange,
	allowEmpty = false,
	emptyLabel = "Any activity",
	ariaLabel = "Activity",
}: Props) {
	const system = activityTypes.filter((a) => a.is_system);
	const custom = activityTypes.filter((a) => !a.is_system);
	const selected = activityTypes.find((a) => a.id === value);

	let helper: string | null = null;
	if (value !== "") {
		helper = selected ? `Units: ${unitSummary(selected) || "none"}` : "Unknown exercise";
	}

	return (
		<div className="activity-select">
			<select
				aria-label={ariaLabel}
				value={value}
				onChange={(event) =>
					onChange(event.target.value === "" ? "" : Number(event.target.value))
				}
			>
				{(allowEmpty || value === "") && <option value="">{emptyLabel}</option>}
				{value !== "" && !selected && (
					<option value={value}>Unknown exercise</option>
				)}
				{system.length > 0 && (
					<optgroup label="System exercises">
						{system.map((a) => (
							<option key={a.id} value={a.id}>
								{optionLabel(a)}
							</option>
						))}
					</optgroup>
				)}
				{custom.length > 0 && (
					<optgroup label="My exercises">
						{custom.map((a) => (
							<option key={a.id} value={a.id}>
								{optionLabel(a)}
							</option>
						))}
					</optgroup>
				)}
			</select>
			{helper && <small className="activity-select-helper">{helper}</small>}
		</div>
	);
}
