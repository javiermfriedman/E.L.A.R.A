import { useState } from "react";
import { ElaraProvider } from "./context/ElaraContext";
import { isAuthenticated, removeToken } from "./services/api";
import Login from "./pages/login/Login";
import AccessGranted from "./components/layout/AccessGranted";
import Dashboard from "./components/layout/Dashboard";

export default function App() {
  const [phase, setPhase] = useState(isAuthenticated() ? "dashboard" : "login");

  function handleLogout() {
    removeToken();
    setPhase("login");
  }

  return (
    <ElaraProvider>
      {phase === "login" && <Login onLogin={() => setPhase("access")} />}
      {phase === "access" && (
        <AccessGranted onComplete={() => setPhase("dashboard")} />
      )}
      {phase === "dashboard" && <Dashboard onLogout={handleLogout} />}
    </ElaraProvider>
  );
}
