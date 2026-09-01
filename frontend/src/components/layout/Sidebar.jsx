import React from 'react';
import { LayoutDashboard, Sparkles, Film, SlidersHorizontal, TrendingUp, Github } from 'lucide-react';
import { useUiStore } from '../../store/useUiStore';

const navigationItems = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'features', label: 'Feature Drivers', icon: Sparkles },
  { id: 'explorer', label: 'Movie Explorer', icon: Film },
  { id: 'whatif', label: 'What-If Simulator', icon: SlidersHorizontal },
  { id: 'trends', label: 'Industry Trends', icon: TrendingUp },
];

export const Sidebar = () => {
  const { activeTab, setActiveTab } = useUiStore();

  return (
    <aside className="w-64 min-h-screen bg-black hairline-right flex flex-col justify-between py-6 px-4 select-none shrink-0 z-20">
      <div>
        {/* Brand Logo & Tagline */}
        <div className="flex items-center gap-3 px-3 py-2 mb-8">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#8052ff] to-[#ffb829] flex items-center justify-center shadow-lg shadow-[#8052ff]/20">
            <span className="text-white text-xs font-bold tracking-wider">CF</span>
          </div>
          <div>
            <h1 className="text-sm font-semibold tracking-tight text-white leading-none">CineForecast</h1>
            <p className="text-[10px] text-zinc-500 font-mono mt-1">v1.0 • ML Platform</p>
          </div>
        </div>

        {/* Navigation Section */}
        <div className="space-y-1">
          <p className="text-[10px] font-mono tracking-widest text-zinc-600 uppercase px-3 mb-2">Analytics Modules</p>
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-[#8052ff]/15 text-[#8052ff] font-semibold hairline-border shadow-sm'
                    : 'text-zinc-400 hover:text-white hover:bg-zinc-900/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-[#8052ff]' : 'text-zinc-500'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Model Spec Footer Badge */}
      <div className="p-3 rounded-2xl bg-zinc-950 hairline-border text-xs">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-zinc-400 text-[11px] font-medium">Champion Model</span>
          <span className="px-1.5 py-0.5 rounded-full text-[9px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Active
          </span>
        </div>
        <p className="text-zinc-200 font-medium text-xs">XGBoost Regressor + SHAP</p>
        <p className="text-zinc-500 text-[10px] mt-0.5 font-mono">34 Pre-Release Features</p>
      </div>
    </aside>
  );
};
