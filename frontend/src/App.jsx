// src/App.jsx
import React, { useState, useEffect } from 'react';
import { Routes, Route } from "react-router-dom";

import { useFullScreenContext } from './context/FullScreenContext';

function RootLayout() {
  const { fsRootRef } = useFullScreenContext();

  return (
    <div
      ref={fsRootRef}
      className="min-h-dvh bg-[url('/bg.png')] bg-cover bg-center bg-fixed relative"
    >
      <div className="min-h-dvh bg-white/50 backdrop-blur-[1px]">
        <h1>DOMIFILE</h1>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>

      {/* Main application */}
      <Route path="/*" element={<RootLayout />} />

    </Routes>
  );
}
