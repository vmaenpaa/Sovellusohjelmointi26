import { useState } from "react";
import { apiFetch } from "../api/client";
import "./HomePage.css";

export default function HomePage() {
  const [status, setStatus] = useState<"loading" | "ok" | "not-ok">("loading");

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
          Test
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
