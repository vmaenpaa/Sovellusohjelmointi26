import { useState } from "react";
import { useNavigate } from "react-router";
import { apiFetch } from "../api/client";
import { clearToken } from "../auth/token";
import "./HomePage.css";

export default function HomePage() {
  const navigate = useNavigate();
  const [status, setStatus] = useState<"loading" | "ok" | "not-ok">("loading");

  const handleLogout = () => {
    clearToken();
    navigate("/login");
  };

  const handleTest = async () => {
    setStatus("loading");

    try {
      const response = await apiFetch("/health");
      const data = await response.json();

      setStatus(data.status === "ok" ? "ok" : "not-ok");
    } catch {
      setStatus("not-ok");
    }
  };

  return (
    <div className="homepage">
      <div className="homepage-card">

        <button className="homepage-button" onClick={handleTest}>
          Check health
        </button>

        <button className="homepage-button homepage-logout-button" onClick={handleLogout}>
          Log out
        </button>

        <div
          className={`homepage-status ${
            status === "ok"
              ? "ok"
              : status === "not-ok"
                ? "not-ok"
                : "loading"
          }`}
        >
          {status === "loading" ? "Press button to test" : status === "ok" ? "OK" : "NOT OK"}
        </div>
      </div>
    </div>
  );
}
