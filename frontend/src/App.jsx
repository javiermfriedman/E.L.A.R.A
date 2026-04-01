import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ElaraProvider } from "./context/ElaraContext";
import { isAuthenticated } from "./services/api";
import Login from "./pages/login/Login";
import AccessGranted from "./components/layout/AccessGranted";
import Dashboard from "./components/layout/Dashboard";

function ProtectedRoute({ children }) {
  return isAuthenticated() ? children : <Navigate to="/login" replace />;
}

function GuestRoute({ children }) {
  return isAuthenticated() ? <Navigate to="/dashboard" replace /> : children;
}

export default function App() {
  return (
    <BrowserRouter>
      <ElaraProvider>
        <Routes>
          <Route
            path="/login"
            element={
              <GuestRoute>
                <Login />
              </GuestRoute>
            }
          />
          <Route
            path="/access"
            element={
              <ProtectedRoute>
                <AccessGranted />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="*"
            element={
              <Navigate
                to={isAuthenticated() ? "/dashboard" : "/login"}
                replace
              />
            }
          />
        </Routes>
      </ElaraProvider>
    </BrowserRouter>
  );
}
