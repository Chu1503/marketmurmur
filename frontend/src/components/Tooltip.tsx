"use client";
import { useState } from "react";
import { Info } from "lucide-react";

interface Props {
  text: string;
}

export default function Tooltip({ text }: Props) {
  const [show, setShow] = useState(false);

  return (
    <span className="relative inline-flex items-center">
      <button
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        onFocus={() => setShow(true)}
        onBlur={() => setShow(false)}
        className="text-gray-600 hover:text-gray-400 transition-colors ml-1 cursor-help"
        type="button"
        aria-label="More info"
      >
        <Info className="w-3.5 h-3.5" />
      </button>

      {show && (
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50
                         w-56 bg-gray-800 border border-gray-700 rounded-lg
                         px-3 py-2 text-xs text-gray-300 leading-relaxed shadow-xl
                         pointer-events-none">
          {text}
          <span className="absolute top-full left-1/2 -translate-x-1/2
                           border-4 border-transparent border-t-gray-700" />
        </span>
      )}
    </span>
  );
}