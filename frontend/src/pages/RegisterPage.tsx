import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router";
import { apiFetch } from "../api/client";
import "./RegisterPage.css";

type FormValues = {
	username: string;
	email: string;
	password: string;
};

type FormErrors = Partial<Record<keyof FormValues, string>>;

export default function RegisterPage() {
	const navigate = useNavigate();
	const [values, setValues] = useState<FormValues>({
		username: "",
		email: "",
		password: "",
	});
	const [errors, setErrors] = useState<FormErrors>({});
	const [apiError, setApiError] = useState("");
	const [isSubmitting, setIsSubmitting] = useState(false);

	const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		const { name, value } = event.target;
		setValues((currentValues) => ({
			...currentValues,
			[name]: value,
		}));
		setErrors((currentErrors) => ({
			...currentErrors,
			[name]: undefined,
		}));
		setApiError("");
	};

	const validate = (): FormErrors => {
		const nextErrors: FormErrors = {};

		if (!values.username.trim()) {
			nextErrors.username = "Username is required.";
		}

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
			const response = await apiFetch("/auth/register", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					email: values.email.trim(),
					password: values.password,
					display_name: values.username.trim(),
				}),
			});

			const data = await response.json().catch(() => ({}));

			if (!response.ok) {
				const detail =
					typeof data.detail === "string"
						? data.detail
						: "Registration failed. Please check your details and try again.";

				setApiError(detail);
				return;
			}

			navigate("/login");
		} catch {
			setApiError("Unable to connect to the server. Please try again.");
		} finally {
			setIsSubmitting(false);
		}
	};

	return (
		<main className="register-page">
			<section className="register-card" aria-labelledby="register-title">
				<h1 id="register-title">Create your account</h1>
			
				<form className="register-form" onSubmit={handleSubmit} noValidate>
					<div className="register-field">
						<label htmlFor="username">Username</label>
						<input
							id="username"
							name="username"
							type="text"
							value={values.username}
							onChange={handleChange}
							  required
							autoComplete="username"
						/>
						{errors.username && (
							<p className="register-field-error" id="username-error">
								{errors.username}
							</p>
						)}
					</div>

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
						{errors.email && (
							<p className="register-field-error" id="email-error">
								{errors.email}
							</p>
						)}
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
							autoComplete="new-password"
						/>
						{errors.password && (
							<p className="register-field-error" id="password-error">
								{errors.password}
							</p>
						)}
					</div>

					{apiError && (
						<p className="register-api-error" role="alert">
							{apiError}
						</p>
					)}

					<button className="register-button" type="submit" disabled={isSubmitting}>
						{isSubmitting ? "Creating account..." : "Create account"}
					</button>
				</form>
			</section>
		</main>
	);
}
