import ReactDOM from "react-dom/client";
import { QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router";
import { queryClient } from "./api/queryClient.ts";
import ProtectedRoute from "./auth/ProtectedRoute.tsx";
import HomePage from "./pages/HomePage.tsx";
import LoginPage from "./pages/LoginPage.tsx";
import PlanDetailPage from "./pages/PlanDetailPage.tsx";
import PlansPage from "./pages/PlansPage.tsx";
import RegisterPage from "./pages/RegisterPage.tsx";
import SessionFormPage from "./pages/SessionFormPage.tsx";
import SessionsPage from "./pages/SessionsPage.tsx";

const root = document.getElementById("root") as HTMLElement;

ReactDOM.createRoot(root).render(
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route index element={<HomePage />} />
          <Route path="/sessions" element={<SessionsPage />} />
          <Route path="/sessions/new" element={<SessionFormPage />} />
          <Route path="/sessions/:sessionId" element={<SessionFormPage />} />
          <Route path="/plans" element={<PlansPage />} />
          <Route path="/plans/:planId" element={<PlanDetailPage />} />
        </Route>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Routes>
    </BrowserRouter>
  </QueryClientProvider>,
);