import type { AuthenticatedUser } from "../auth/ProtectedRoute";
import "./Header.css";

type HeaderProps = {
	user: AuthenticatedUser | null;
	onLogout: () => void;
};

export default function Header({ user, onLogout }: HeaderProps) {
	return (
		<header className="app-header">
			<div className="app-header-user">
				<span className="app-header-label">Signed in as</span>
				<strong>{user?.display_name}</strong>
			</div>
			<button className="app-header-logout" type="button" onClick={onLogout}>
				Log out
			</button>
		</header>
	);
}
