"use client";

import Image from "next/image";

import React, { useState } from "react";
import UploadPhoto from "./UploadPhoto";
import Gallery from "./Gallery";
import DisclosureUpload from "./DisclosureUpload";

export default function Home() {
  const [galleryKey, setGalleryKey] = useState(0);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
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
