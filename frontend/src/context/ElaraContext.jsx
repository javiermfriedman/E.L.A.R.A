import { createContext, useContext, useState, useEffect } from "react";
import { getToken, removeToken, isAuthenticated } from "../services/api";

const ElaraContext = createContext(null);

export function ElaraProvider({ children }) {
  const [token, setTokenState] = useState(getToken);
  const [user, setUser] = useState(null);

  // Sync token state with localStorage
  function saveToken(newToken) {
    setTokenState(newToken);
  }

  function logout() {
    removeToken();
    setTokenState(null);
    setUser(null);
  }

  const value = {
    token,
    user,
    setUser,
    saveToken,
    logout,
    isLoggedIn: !!token,
  };

  return (
    <ElaraContext.Provider value={value}>{children}</ElaraContext.Provider>
  );
}

export function useElara() {
  const ctx = useContext(ElaraContext);
  if (!ctx) throw new Error("useElara must be used inside ElaraProvider");
  return ctx;
}
