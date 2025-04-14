"use client";

import Image from "next/image";

import React, { useState } from "react";
import UploadPhoto from "./UploadPhoto";
import Gallery from "./Gallery";
import DisclosureUpload from "./DisclosureUpload";
import LogoutButton from "./LogoutButton";

export default function Home() {
  const [galleryKey, setGalleryKey] = useState(0);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [authenticated, setAuthenticated] = useState(false);

  React.useEffect(() => {
    if (typeof window !== "undefined") {
      const authed = localStorage.getItem("authenticated");
      if (authed === "true") setAuthenticated(true);
    }
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      const data = await res.json();
      if (data.success) {
        setAuthenticated(true);
        if (typeof window !== "undefined") {
          localStorage.setItem("authenticated", "true");
        }
      } else {
        setError("Incorrect password");
      }
    } catch (err) {
      setError("Could not connect to backend");
    }
  };


  if (!authenticated) {
    return (
      <main className="fixed inset-0 flex items-center justify-center min-h-screen bg-gradient-to-br from-black via-zinc-900 to-zinc-800 dark:bg-gradient-to-br dark:from-zinc-900 dark:via-black dark:to-zinc-900">
        <div className="absolute inset-0 bg-black/80 dark:bg-black/90 backdrop-blur-sm z-0" />
        <form
          onSubmit={handleLogin}
          className="relative z-10 flex flex-col gap-6 items-center w-full max-w-sm px-8 py-10 bg-white/95 dark:bg-zinc-900/90 rounded-2xl shadow-2xl border border-zinc-200 dark:border-zinc-700"
        >
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="Enter password"
            className="w-full px-4 py-3 rounded-lg border border-zinc-300 dark:border-zinc-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 dark:placeholder-zinc-500 bg-zinc-100 dark:bg-zinc-800 transition"
            autoFocus
          />
          {error && (
            <div className="w-full text-center text-red-600 dark:text-red-400 font-medium animate-pulse">{error}</div>
          )}
          <button
            type="submit"
            className="w-full py-3 mt-2 rounded-lg bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white text-lg font-semibold shadow transition"
          >
            Login
          </button>
        </form>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 relative">
      <LogoutButton onLogout={() => setAuthenticated(false)} />
      <h1 className="text-4xl font-bold mb-4">Welcome to Captioner <span role="img" aria-label="camera">📸</span></h1>
      <p className="text-lg text-gray-600 mb-8">Effortlessly manage your photo captions. Start by uploading your favorite shots!</p>
      <Gallery key={galleryKey} />
      {/* Collapsible upload form */}
      <DisclosureUpload>
        <UploadPhoto onUpload={() => setGalleryKey(k => k + 1)} />
      </DisclosureUpload>
    </main>
  );
}
