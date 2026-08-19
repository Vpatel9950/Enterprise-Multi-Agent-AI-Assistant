import React, { createContext, useState, useEffect, useContext } from "react";
import { api } from "../services/api";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [loading, setLoading] = useState(true);
  const [theme, setTheme] = useState("dark");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const userData = await api.getMe();
          setUser(userData);
        } catch (err) {
          console.error("Token verification failed:", err);
          logout();
        }
      }
      setLoading(false);
    };
    initAuth();
  }, [token]);

  const login = async (email, password) => {
    const data = await api.login(email, password);
    localStorage.setItem("token", data.access_token);
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  };

  const register = async (userData) => {
    const data = await api.register(userData);
    localStorage.setItem("token", data.access_token);
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  const loginAsAdmin = async () => {
    return login("admin@enterprise.ai", "AdminPassword123!");
  };

  const loginAsUser = async () => {
    return login("user@enterprise.ai", "UserPassword123!");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        theme,
        toggleTheme,
        login,
        register,
        logout,
        loginAsAdmin,
        loginAsUser,
        isAdmin: user?.role === "admin",
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
