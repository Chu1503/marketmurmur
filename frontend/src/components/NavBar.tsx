"use client";

import { usePathname } from "next/navigation";

export default function NavBar() {
  const pathname = usePathname();
  if (pathname === "/") return null;

  return (
    <nav className="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-center">
        <a href="/" className="flex items-center gap-2">
          <span className="text-xl font-bold text-white">Market</span>
          <span className="text-xl font-bold text-violet-400">Murmur</span>
        </a>
      </div>
    </nav>
  );
}