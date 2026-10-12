import { queryClient } from "../api/queryClient";

const TOKEN_KEY = "access_token";

export function setToken(token: string) {
	localStorage.setItem(TOKEN_KEY, token);
}

export function getToken() {
	return localStorage.getItem(TOKEN_KEY);
}

export function clearToken() {
	localStorage.removeItem(TOKEN_KEY);
	// Cached rows belong to the previous account.
	queryClient.clear();
}
