import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router";
import HomePage from "./pages/HomePage.tsx";

const root = document.getElementById("root") as HTMLElement;

ReactDOM.createRoot(root).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<HomePage />} />
    </Routes>
  </BrowserRouter>,
);