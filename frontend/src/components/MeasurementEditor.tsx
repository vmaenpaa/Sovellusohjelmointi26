import { emptyPair, type UnitDraft, type ValuePair } from "../sessions/draft";

type MeasurementEditorProps = {
	units: UnitDraft[];
	onChange: (units: UnitDraft[]) => void;
};

export default function MeasurementEditor({
	units,
	onChange,
}: MeasurementEditorProps) {
	const replaceValues = (unitIndex: number, values: ValuePair[]) => {
		onChange(
			units.map((unit, index) =>
				index === unitIndex ? { ...unit, values } : unit,
			),
		);
	};

	const setField = (
		unitIndex: number,
		valueIndex: number,
		field: keyof ValuePair,
		value: string,
	) => {
		replaceValues(
			unitIndex,
			units[unitIndex].values.map((pair, index) =>
				index === valueIndex ? { ...pair, [field]: value } : pair,
			),
		);
	};

	if (units.length === 0) {
		return <p className="measurement-empty">This activity has no units.</p>;
	}

	return (
		<div className="measurement-editor">
			{units.map((unit, unitIndex) => (
				<fieldset key={unit.unitTypeId} className="measurement-unit">
					<legend>{unit.label}</legend>

					{unit.values.map((pair, valueIndex) => (
						<div key={valueIndex} className="measurement-row">
							{unit.perSet && (
								<span className="measurement-set">Set {valueIndex + 1}</span>
							)}
							<label>
								Planned
								<input
									type="number"
									step="any"
									value={pair.planned}
									onChange={(event) =>
										setField(unitIndex, valueIndex, "planned", event.target.value)
									}
								/>
							</label>
							<label>
								Actual
								<input
									type="number"
									step="any"
									value={pair.actual}
									onChange={(event) =>
										setField(unitIndex, valueIndex, "actual", event.target.value)
									}
								/>
							</label>
						</div>
					))}

					{unit.perSet && (
						<div className="measurement-set-actions">
							<button
								type="button"
								onClick={() =>
									replaceValues(unitIndex, [...unit.values, emptyPair()])
								}
							>
								Add set
							</button>
							<button
								type="button"
								disabled={unit.values.length <= 1}
								onClick={() =>
									replaceValues(unitIndex, unit.values.slice(0, -1))
								}
							>
								Remove set
							</button>
						</div>
					)}
				</fieldset>
			))}
		</div>
	);
}
