import { useState } from "react";
import type { FormEvent } from "react";
import { NavLink, useNavigate } from "react-router";
import { apiFetch } from "../api/client";
import { setToken } from "../auth/token";
import "./RegisterPage.css";

type FormValues = {
	email: string;
	password: string;
};

type FormErrors = Partial<Record<keyof FormValues, string>>;

export default function LoginPage() {
	const navigate = useNavigate();
	const [values, setValues] = useState<FormValues>({ email: "", password: "" });
	const [errors, setErrors] = useState<FormErrors>({});
	const [apiError, setApiError] = useState("");
	const [isSubmitting, setIsSubmitting] = useState(false);

	const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		const { name, value } = event.target;
		setValues((currentValues) => ({ ...currentValues, [name]: value }));
		setErrors((currentErrors) => ({ ...currentErrors, [name]: undefined }));
		setApiError("");
	};

	const validate = (): FormErrors => {
		const nextErrors: FormErrors = {};

		if (!values.email.trim()) {
			nextErrors.email = "Email is required.";
		}

		if (!values.password) {
			nextErrors.password = "Password is required.";
		}

		return nextErrors;
	};

	const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		setApiError("");

		const nextErrors = validate();
		setErrors(nextErrors);

		if (Object.keys(nextErrors).length > 0) {
			return;
		}

		setIsSubmitting(true);

		try {
			const response = await apiFetch("/auth/login", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					email: values.email.trim(),
					password: values.password,
				}),
			});
			const data = await response.json().catch(() => ({}));

			if (!response.ok) {
				setApiError(
					typeof data.detail === "string"
						? data.detail
						: "Login failed. Please check your details and try again.",
				);
				return;
			}

			if (typeof data.access_token !== "string") {
				setApiError("Login failed. The server did not return a token.");
				return;
			}

			setToken(data.access_token);
			navigate("/");
		} catch {
			setApiError("Unable to connect to the server. Please try again.");
		} finally {
			setIsSubmitting(false);
		}
	};

	return (
		<main className="register-page">
			<section className="register-card" aria-labelledby="login-title">
				<h1 id="login-title">Welcome</h1>

				<form className="register-form" onSubmit={handleSubmit} noValidate>
					<div className="register-field">
						<label htmlFor="email">Email</label>
						<input
							id="email"
							name="email"
							type="email"
							value={values.email}
							onChange={handleChange}
							required
							autoComplete="email"
						/>
						{errors.email && <p className="register-field-error">{errors.email}</p>}
					</div>

					<div className="register-field">
						<label htmlFor="password">Password</label>
						<input
							id="password"
							name="password"
							type="password"
							value={values.password}
							onChange={handleChange}
							required
							autoComplete="current-password"
						/>
						{errors.password && <p className="register-field-error">{errors.password}</p>}
					</div>

					{apiError && <p className="register-api-error" role="alert">{apiError}</p>}

					<button className="register-button" type="submit" disabled={isSubmitting}>
						{isSubmitting ? "Logging in..." : "Log in"}
					</button>
				</form>

				<p className="register-login-link">
					Need an account? <NavLink to="/register">Create one</NavLink>
				</p>
			</section>
		</main>
	);
}
