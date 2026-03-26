import { useState } from "react";
import { ElaraProvider } from "./context/ElaraContext";
import { isAuthenticated } from "./services/api";
import Login from "./pages/Login/Login";
import AccessGranted from "./components/layout/AccessGranted";

export default function App() {
  // If token already exists, skip straight to dashboard
  const [phase, setPhase] = useState(isAuthenticated() ? "dashboard" : "login");

  return (
    <ElaraProvider>
      {phase === "login" && <Login onLogin={() => setPhase("access")} />}
      {phase === "access" && (
        <AccessGranted onComplete={() => setPhase("dashboard")} />
      )}
      {phase === "dashboard" && (
        <div style={{ color: "var(--color-primary)", padding: "2rem" }}>
          DASHBOARD COMING SOON
        </div>
      )}
    </ElaraProvider>
  );
}
