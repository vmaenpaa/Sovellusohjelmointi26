import { useState, type FormEvent } from "react";
import type { PlanWrite } from "../api/client";

type PlanFormProps = {
	initial?: PlanWrite;
	submitLabel: string;
	pending: boolean;
	error: string | null;
	onSubmit: (body: PlanWrite) => void;
};

export default function PlanForm({
	initial,
	submitLabel,
	pending,
	error,
	onSubmit,
}: PlanFormProps) {
	const [name, setName] = useState(initial?.name ?? "");
	const [startDate, setStartDate] = useState(initial?.start_date ?? "");
	const [weeks, setWeeks] = useState(
		initial?.length_weeks != null ? String(initial.length_weeks) : "",
	);
	const [notes, setNotes] = useState(initial?.notes ?? "");
	const [validation, setValidation] = useState<string | null>(null);

	const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();

		const trimmedName = name.trim();
		if (trimmedName === "") {
			setValidation("Name is required.");
			return;
		}

		const weeksText = weeks.trim();
		let lengthWeeks: number | null = null;
		if (weeksText !== "") {
			lengthWeeks = Number(weeksText);
			if (!Number.isInteger(lengthWeeks) || lengthWeeks < 1) {
				setValidation("Length in weeks must be a whole number of at least 1.");
				return;
			}
		}

		setValidation(null);
		onSubmit({
			name: trimmedName,
			start_date: startDate === "" ? null : startDate,
			length_weeks: lengthWeeks,
			notes: notes.trim() === "" ? null : notes,
		});
	};

	const message = validation ?? error;

	return (
		<form className="plan-form" onSubmit={handleSubmit} noValidate>
			<label>
				Name
				<input value={name} onChange={(e) => setName(e.target.value)} required />
			</label>
			<label>
				Start date
				<input
					type="date"
					value={startDate}
					onChange={(e) => setStartDate(e.target.value)}
				/>
			</label>
			<label>
				Length (weeks)
				<input
					type="number"
					min={1}
					step={1}
					value={weeks}
					onChange={(e) => setWeeks(e.target.value)}
				/>
			</label>
			<label>
				Notes
				<textarea value={notes} onChange={(e) => setNotes(e.target.value)} />
			</label>
			{message && <p className="plan-error" role="alert">{message}</p>}
			<button type="submit" className="plan-primary" disabled={pending}>
				{pending ? "Saving..." : submitLabel}
			</button>
		</form>
	);
}
