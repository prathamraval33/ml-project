import React from 'react';
import { Database, ShieldCheck, Activity } from 'lucide-react';

export const Header = ({ title, subtitle }) => {
  return (
    <header className="hairline-bottom px-8 py-5 bg-black/60 backdrop-blur-md sticky top-0 z-10 flex items-center justify-between">
      <div>
        <h2 className="text-xl font-semibold tracking-tight text-white">{title}</h2>
        {subtitle && <p className="text-xs text-zinc-400 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-950 hairline-border text-xs text-zinc-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-mono text-[11px]">API: Online</span>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-950 hairline-border text-xs text-zinc-300">
          <Database className="w-3.5 h-3.5 text-[#8052ff]" />
          <span className="font-mono text-[11px]">3,931 Clean Films</span>
        </div>
      </div>
    </header>
  );
};
