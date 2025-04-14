"use client";
import React, { useState } from "react";

export default function DisclosureUpload({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="w-full max-w-md mt-8">
      <button
        type="button"
        className="flex items-center w-full px-4 py-3 bg-zinc-800 text-blue-200 rounded-t-lg focus:outline-none focus:ring-2 focus:ring-blue-400 hover:bg-zinc-700 transition-all font-semibold text-lg shadow"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls="upload-form-panel"
      >
        <span className={`mr-2 transform transition-transform duration-200 ${open ? "rotate-90" : "rotate-0"}`}>
          ▶
        </span>
        Upload a Photo
      </button>
      {open && (
        <div
          id="upload-form-panel"
          className="border border-zinc-700 rounded-b-lg bg-zinc-900 p-4 shadow-inner animate-fade-in"
        >
          {children}
        </div>
      )}
    </div>
  );
}

// Add a simple fade-in animation for extra polish
// Tailwind users can add this to globals.css:
// @keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
// .animate-fade-in { animation: fade-in 0.3s ease; }
