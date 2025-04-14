"use client";
import React from "react";

export default function LogoutButton({ onLogout }: { onLogout: () => void }) {
  const handleLogout = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("authenticated");
    }
    onLogout();
  };
  return (
    <button
      onClick={handleLogout}
      className="absolute top-6 right-6 px-4 py-2 rounded-lg bg-zinc-200 text-zinc-700 font-semibold hover:bg-zinc-300 shadow transition z-20"
      aria-label="Logout"
    >
      Logout
    </button>
  );
}
