import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "../api/client";
import "./HomePage.css";

export default function HomePage() {
  const health = useQuery({
    queryKey: ["health"],
    queryFn: () => apiRequest<{ status: string }>("/health"),
    enabled: false,
  });

  const status: "loading" | "ok" | "not-ok" = health.isError
    ? "not-ok"
    : health.data
      ? health.data.status === "ok"
        ? "ok"
        : "not-ok"
      : "loading";

  const handleTest = () => {
    health.refetch();
  };

  return (
    <div className="homepage">
      <div className="homepage-card">

        <button className="homepage-button" onClick={handleTest}>
          Check health
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
