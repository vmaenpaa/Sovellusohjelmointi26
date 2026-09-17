import { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router";
import { apiFetch } from "../api/client";
import { clearToken, getToken } from "./token";

export default function ProtectedRoute() {
	const token = getToken();
	const [authenticated, setAuthenticated] = useState<boolean | null>(null);

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
					setAuthenticated(false);
					return;
				}

				if (response.ok) {
					setAuthenticated(true);
				}
			})
			.catch(() => undefined);

		return () => {
			cancelled = true;
		};
	}, [token]);

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

	return <Outlet />;
}
