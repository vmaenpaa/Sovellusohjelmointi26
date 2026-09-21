import { useEffect, useState } from "react";
import { Navigate, Outlet, useNavigate } from "react-router";
import { apiFetch } from "../api/client";
import Header from "../components/Header";
import { clearToken, getToken } from "./token";

export type AuthenticatedUser = {
	id: number;
	email: string;
	display_name: string;
};

export default function ProtectedRoute() {
	const token = getToken();
	const navigate = useNavigate();
	const [authenticated, setAuthenticated] = useState<boolean | null>(null);
	const [user, setUser] = useState<AuthenticatedUser | null>(null);

	const handleLogout = () => {
		clearToken();
		setUser(null);
		setAuthenticated(false);
		navigate("/login", { replace: true });
	};

	useEffect(() => {
		if (!token) {
			return;
		}

		let cancelled = false;

		apiFetch("/auth/me")
			.then((response) => {
				if (cancelled) {
					return;
				}

				if (response.status === 401) {
					clearToken();
					setUser(null);
					setAuthenticated(false);
					navigate("/login", { replace: true });
					return;
				}

				if (response.ok) {
					response.json().then((data: AuthenticatedUser) => {
						if (cancelled) {
							return;
						}

						setUser(data);
						setAuthenticated(true);
					});
				}
			})
			.catch(() => undefined);

		return () => {
			cancelled = true;
		};
	}, [navigate, token]);

	if (!token) {
		clearToken();
		return <Navigate to="/login" replace />;
	}

	if (authenticated === false) {
		return <Navigate to="/login" replace />;
	}

	if (authenticated !== true) {
		return null;
	}

	return (
		<>
			<Header user={user} onLogout={handleLogout} />
			<Outlet />
		</>
	);
}
