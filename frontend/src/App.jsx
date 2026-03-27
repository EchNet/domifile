// src/App.jsx
import React, { useState } from 'react';

import { useFullScreenContext } from './context/FullScreenContext';


export default function App() {
  const { fsRootRef } = useFullScreenContext();
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const ask = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setResult(null);

    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await res.json();
    setResult(data);
    setLoading(false);
  };

  function renderAnswer(answer, sources) {
    const parts = answer.split(/(\[[\d,\s]+\])/g);

    return parts.map((part, i) => {
      const match = part.match(/\[([\d,\s]+)\]/);

      if (!match) return <span key={i}>{part}</span>;

      const ids = match[1]
        .split(",")
        .map((s) => parseInt(s.trim(), 10))
        .filter(Boolean);

      return (
        <sup key={i} className="ml-1 space-x-1">
          {ids.map((id, n) => {
            const source = sources.find((s) => s.id === id);
            if (!source) return null;

            return (
              <>
                {n > 0 ? ", " : ""}
                <a
                  key={id}
                  href={source.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-teal-600 hover:underline"
                >
                  {id}
                </a>
              </>
            );
          })}
        </sup>
      );
    });
  }

  return (
    <div ref={fsRootRef} className="min-h-screen bg-gray-50 text-gray-900 flex flex-col items-center px-4">

      {/* Logo */}
      <div className="mt-16 mb-8 text-2xl font-semibold tracking-wide">
        <span className="text-blue-900">DOMI</span>
        <span className="text-gray-500">FILE</span>
      </div>

      {/* Input */}
      <div className="w-full max-w-2xl">
        <div className="flex gap-2">
          <input
            className="flex-1 rounded-xl border border-gray-300 px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            placeholder="Ask about your documents..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && ask()}
          />
          <button
            onClick={ask}
            className="bg-blue-900 text-white px-5 py-3 rounded-xl hover:bg-blue-800 transition"
          >
            Ask
          </button>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="mt-8 text-gray-500">
          Analyzing documents…
        </div>
      )}

      {/* Answer */}
      {result && (
        <div className="w-full max-w-2xl mt-8 space-y-4">

          <div className="text-sm text-gray-500">
            Answer based on {result.sources?.length || 0} documents
          </div>

          <div className="bg-white rounded-2xl shadow p-6 whitespace-pre-wrap">
            {renderAnswer(result.answer, result.sources)}
          </div>

          {/* Sources */}
          <div className="text-sm text-gray-600 space-y-1">
            {result.sources?.map((s, i) => (
              <div key={i}>
                <a
                  href={s.url}
                  target="_blank"
                  rel="noreferrer"
                  className="hover:underline text-teal-600"
                >
                  {s.label}
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
