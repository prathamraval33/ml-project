import React from 'react';

export const StatCard = ({ label, value, subtext, icon: Icon, trend, accent = 'iris' }) => {
  const accentColors = {
    iris: 'text-[#8052ff] bg-[#8052ff]/10 border-[#8052ff]/20',
    saffron: 'text-[#ffb829] bg-[#ffb829]/10 border-[#ffb829]/20',
    rose: 'text-[#ff5c7a] bg-[#ff5c7a]/10 border-[#ff5c7a]/20',
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  };

  return (
    <div className="void-card p-6 flex flex-col justify-between transition-transform duration-200 hover:-translate-y-0.5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-zinc-400 tracking-wide uppercase font-mono">{label}</span>
        {Icon && (
          <div className={`p-2 rounded-xl border ${accentColors[accent] || accentColors.iris}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div>
        <div className="text-stat-value tracking-tight font-bold text-white mb-1">{value}</div>
        {subtext && <div className="text-xs text-zinc-400 font-mono">{subtext}</div>}
      </div>
    </div>
  );
};
