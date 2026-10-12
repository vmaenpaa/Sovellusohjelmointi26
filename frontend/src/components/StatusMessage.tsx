import type { ReactNode } from "react";
import { Link } from "react-router";
import "./StatusMessage.css";

type EmptyStateProps = {
	title: string;
	description?: ReactNode;
	action?: { to: string; label: string };
};

export function EmptyState({ title, description, action }: EmptyStateProps) {
	return (
		<div className="empty-state">
			<p className="empty-state-title">{title}</p>
			{description && <p className="empty-state-description">{description}</p>}
			{action && (
				<Link className="empty-state-action" to={action.to}>
					{action.label}
				</Link>
			)}
		</div>
	);
}

export function ErrorBanner({ message }: { message: string }) {
	return (
		<div className="error-banner" role="alert">
			{message}
		</div>
	);
}
