export type CalendarView = "month" | "week";

export function startOfDay(date: Date) {
	return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

export function addDays(date: Date, days: number) {
	return new Date(date.getFullYear(), date.getMonth(), date.getDate() + days);
}

export function addMonths(date: Date, months: number) {
	const target = new Date(date.getFullYear(), date.getMonth() + months, 1);
	const lastDay = new Date(
		target.getFullYear(),
		target.getMonth() + 1,
		0,
	).getDate();
	target.setDate(Math.min(date.getDate(), lastDay));
	return target;
}

export function startOfWeek(date: Date) {
	const offset = (date.getDay() + 6) % 7;
	return addDays(startOfDay(date), -offset);
}

export function visibleDays(view: CalendarView, cursor: Date) {
	const first =
		view === "month"
			? startOfWeek(new Date(cursor.getFullYear(), cursor.getMonth(), 1))
			: startOfWeek(cursor);
	const count = view === "month" ? 42 : 7;
	return Array.from({ length: count }, (_, i) => addDays(first, i));
}

export function rangeBounds(days: Date[]) {
	const last = days[days.length - 1];
	const end = new Date(
		last.getFullYear(),
		last.getMonth(),
		last.getDate(),
		23,
		59,
		59,
		999,
	);
	return { from: days[0].toISOString(), to: end.toISOString() };
}

export function shiftCursor(view: CalendarView, cursor: Date, direction: -1 | 1) {
	return view === "month"
		? addMonths(cursor, direction)
		: addDays(cursor, 7 * direction);
}

export function dayKey(date: Date) {
	const month = String(date.getMonth() + 1).padStart(2, "0");
	const day = String(date.getDate()).padStart(2, "0");
	return `${date.getFullYear()}-${month}-${day}`;
}

export function parseDayKey(key: string) {
	const [year, month, day] = key.split("-").map(Number);
	return new Date(year, month - 1, day);
}

export function withDateKeepTime(originalIso: string, key: string) {
	const original = new Date(originalIso);
	const target = parseDayKey(key);
	target.setHours(
		original.getHours(),
		original.getMinutes(),
		original.getSeconds(),
		original.getMilliseconds(),
	);
	return target.toISOString();
}

export function rangeTitle(view: CalendarView, cursor: Date, days: Date[]) {
	if (view === "month") {
		return cursor.toLocaleDateString(undefined, {
			month: "long",
			year: "numeric",
		});
	}
	const options: Intl.DateTimeFormatOptions = { dateStyle: "medium" };
	return `${days[0].toLocaleDateString(undefined, options)} – ${days[6].toLocaleDateString(undefined, options)}`;
}
