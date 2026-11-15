import React, { createContext, useState, useEffect, useContext } from "react";
import { api } from "../services/api";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const cached = localStorage.getItem("user");
    return cached ? JSON.parse(cached) : null;  // null = not logged in
  });
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState("dark");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const login = async (email, password) => {
    const data = await api.login(email, password);
    localStorage.setItem("token", data.accessToken || "demo-token");
    localStorage.setItem("user", JSON.stringify(data.user));
    setToken(data.accessToken);
    setUser(data.user);
    return data.user;
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);  // null = login screen dikhao
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  // Quick Enterprise Demo Role Switchers
  const switchRole = (role) => {
    let mockUser;
    if (role === "SUPER_ADMIN") {
      mockUser = {
        id: "6732a1000000000000000001",
        fullName: "Victoria Vance (Super Admin)",
        email: "superadmin@enterprise.ai",
        role: "SUPER_ADMIN",
        organizationId: "6732a1000000000000000002",
        department: "Executive Governance",
        isActive: true
      };
    } else if (role === "ORG_ADMIN") {
      mockUser = {
        id: "6732a1000000000000000002",
        fullName: "Sarah Jenkins (Org Admin)",
        email: "admin@acme.com",
        role: "ORG_ADMIN",
        organizationId: "6732a1000000000000000001",
        department: "Executive Operations",
        isActive: true
      };
    } else if (role === "MANAGER") {
      mockUser = {
        id: "6732a1000000000000000003",
        fullName: "David Sterling (HR Manager)",
        email: "hr.manager@acme.com",
        role: "MANAGER",
        organizationId: "6732a1000000000000000001",
        department: "Human Resources & Talent",
        isActive: true
      };
    } else {
      mockUser = {
        id: "6732a1000000000000000004",
        fullName: "Alex Rivera (Staff Engineer)",
        email: "alex.rivera@acme.com",
        role: "EMPLOYEE",
        organizationId: "6732a1000000000000000001",
        department: "Engineering & Architecture",
        isActive: true
      };
    }
    localStorage.setItem("user", JSON.stringify(mockUser));
    setUser(mockUser);
  };

  const loginAsAdmin = () => switchRole("ORG_ADMIN");
  const loginAsUser = () => switchRole("EMPLOYEE");
  const register = async (userData) => {
    return switchRole("EMPLOYEE");
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
        logout,
        register,
        loginAsAdmin,
        loginAsUser,
        switchRole,
        isSuperAdmin: user?.role === "SUPER_ADMIN",
        isOrgAdmin: user?.role === "ORG_ADMIN",
        isManager: user?.role === "MANAGER" || user?.role === "ORG_ADMIN" || user?.role === "SUPER_ADMIN",
        isEmployee: user?.role === "EMPLOYEE",
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
