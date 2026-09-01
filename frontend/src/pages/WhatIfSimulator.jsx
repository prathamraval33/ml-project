import React, { useEffect, useState } from 'react';
import { SlidersHorizontal, Sparkles, TrendingUp, DollarSign, Calendar, Film, ArrowRight, RotateCcw } from 'lucide-react';
import { TierBadge } from '../components/ui/TierBadge';
import { predictMovie, runWhatIfSimulation } from '../api/client';
import { useUiStore } from '../store/useUiStore';

const ALL_GENRES = [
  'Action',
  'Adventure',
  'Animation',
  'Comedy',
  'Crime',
  'Drama',
  'Family',
  'Fantasy',
  'History',
  'Horror',
  'Music',
  'Mystery',
  'Romance',
  'Science Fiction',
  'Thriller',
  'War',
  'Western',
];

export const WhatIfSimulator = () => {
  const { whatIfBaseMovie, setWhatIfBaseMovie } = useUiStore();

  // Baseline movie parameters
  const [baseParams, setBaseParams] = useState({
    title: 'Project Nebula',
    budget: 65_000_000,
    runtime: 118,
    genres: ['Science Fiction', 'Action'],
    release_date: '2026-07-15',
    director: 'Christopher Nolan',
    director_prior_avg_revenue: 350_000_000,
    primary_production_company_prior_avg_revenue: 200_000_000,
    is_franchise: 0,
  });

  // Simulated adjusted parameters
  const [modifiedParams, setModifiedParams] = useState({ ...baseParams });

  // Results
  const [simulationResult, setSimulationResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // If a movie was sent from Explorer, populate
  useEffect(() => {
    if (whatIfBaseMovie) {
      let parsedGenres = ['Drama'];
      try {
        parsedGenres = typeof whatIfBaseMovie.genres === 'string' && whatIfBaseMovie.genres.startsWith('[')
          ? JSON.parse(whatIfBaseMovie.genres)
          : [whatIfBaseMovie.primary_genre || 'Drama'];
      } catch {
        parsedGenres = [whatIfBaseMovie.primary_genre || 'Drama'];
      }

      const initial = {
        title: whatIfBaseMovie.title,
        budget: whatIfBaseMovie.budget > 0 ? whatIfBaseMovie.budget : 50_000_000,
        runtime: whatIfBaseMovie.runtime || 110,
        genres: parsedGenres,
        release_date: whatIfBaseMovie.release_date || '2026-07-15',
        director: whatIfBaseMovie.director || 'Unknown',
        director_prior_avg_revenue: 100_000_000,
        primary_production_company_prior_avg_revenue: 100_000_000,
        is_franchise: whatIfBaseMovie.is_franchise || 0,
      };
      setBaseParams(initial);
      setModifiedParams(initial);
      setWhatIfBaseMovie(null); // Clear store
    }
  }, [whatIfBaseMovie]);

  // Run simulation whenever modifiedParams changes
  useEffect(() => {
    const executeSimulation = async () => {
      try {
        setLoading(true);
        const res = await runWhatIfSimulation({
          base_params: baseParams,
          adjustments: modifiedParams,
        });
        setSimulationResult(res);
      } catch (err) {
        console.error('Simulation error:', err);
      } finally {
        setLoading(false);
      }
    };

    const timer = setTimeout(executeSimulation, 250);
    return () => clearTimeout(timer);
  }, [baseParams, modifiedParams]);

  const handleGenreToggle = (g) => {
    const current = modifiedParams.genres || [];
    const exists = current.includes(g);
    const updated = exists ? current.filter((item) => item !== g) : [...current, g];
    setModifiedParams({ ...modifiedParams, genres: updated.length > 0 ? updated : ['Drama'] });
  };

  const formatCurrency = (val) => {
    if (!val && val !== 0) return '$0';
    if (Math.abs(val) >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
    if (Math.abs(val) >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
    return `$${val.toLocaleString()}`;
  };

  const handleReset = () => {
    setModifiedParams({ ...baseParams });
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#8052ff]/10 border border-[#8052ff]/20 text-[#8052ff] text-xs font-mono mb-3">
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Scenario Sensitivity Analysis</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white">What-If Box Office Studio</h1>
          <p className="text-zinc-400 text-sm mt-1 max-w-2xl">
            Adjust pre-release variables in real time to simulate impact on predicted worldwide revenue, ROI, and success tiers.
          </p>
        </div>

        <button
          onClick={handleReset}
          className="btn-ghost px-4 py-2 text-xs flex items-center gap-2 self-start md:self-auto"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset to Baseline</span>
        </button>
      </div>

      {/* Main Grid: Left Controls, Right Live Forecast Outcomes */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Interactive Parameter Controls (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="void-card p-6 space-y-6">
            <h3 className="text-base font-semibold text-white">Pre-Release Variables</h3>

            {/* Title & Franchise Toggle */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="sm:col-span-2">
                <label className="text-xs font-medium text-zinc-400 block mb-1.5">Film Title</label>
                <input
                  type="text"
                  value={modifiedParams.title}
                  onChange={(e) => setModifiedParams({ ...modifiedParams, title: e.target.value })}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-[#8052ff]"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-zinc-400 block mb-1.5">Franchise Property</label>
                <button
                  type="button"
                  onClick={() =>
                    setModifiedParams({ ...modifiedParams, is_franchise: modifiedParams.is_franchise ? 0 : 1 })
                  }
                  className={`w-full py-2 px-3 rounded-xl border text-xs font-medium transition-all ${
                    modifiedParams.is_franchise
                      ? 'bg-[#8052ff]/20 text-[#8052ff] border-[#8052ff]/40'
                      : 'bg-zinc-950 text-zinc-400 border-zinc-800 hover:text-white'
                  }`}
                >
                  {modifiedParams.is_franchise ? '★ Franchise Sequel' : 'Standalone Film'}
                </button>
              </div>
            </div>

            {/* Budget Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-zinc-300 font-medium">Production Budget</span>
                <span className="text-[#8052ff] font-mono font-bold text-sm">
                  {formatCurrency(modifiedParams.budget)}
                </span>
              </div>
              <input
                type="range"
                min="1000000"
                max="300000000"
                step="2500000"
                value={modifiedParams.budget}
                onChange={(e) => setModifiedParams({ ...modifiedParams, budget: Number(e.target.value) })}
                className="w-full accent-[#8052ff] cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-zinc-500 font-mono">
                <span>$1M (Indie)</span>
                <span>$100M (Mid-Budget)</span>
                <span>$300M (Tentpole)</span>
              </div>
            </div>

            {/* Runtime Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-zinc-300 font-medium">Runtime (Minutes)</span>
                <span className="text-zinc-200 font-mono font-bold">{modifiedParams.runtime} mins</span>
              </div>
              <input
                type="range"
                min="60"
                max="210"
                step="5"
                value={modifiedParams.runtime}
                onChange={(e) => setModifiedParams({ ...modifiedParams, runtime: Number(e.target.value) })}
                className="w-full accent-[#8052ff] cursor-pointer"
              />
            </div>

            {/* Release Date Window */}
            <div>
              <label className="text-xs font-medium text-zinc-400 block mb-1.5">Release Date Calendar Window</label>
              <input
                type="date"
                value={modifiedParams.release_date}
                onChange={(e) => setModifiedParams({ ...modifiedParams, release_date: e.target.value })}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-[#8052ff]"
              />
              <p className="text-[11px] text-zinc-500 font-mono mt-1">
                Summer (June/July) & Holiday (Nov/Dec) dates automatically activate peak seasonality multipliers.
              </p>
            </div>

            {/* Director & Studio Prior Revenue Averages */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-400">Director Historical Avg</span>
                  <span className="text-zinc-200 font-mono font-medium">
                    {formatCurrency(modifiedParams.director_prior_avg_revenue)}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="600000000"
                  step="10000000"
                  value={modifiedParams.director_prior_avg_revenue}
                  onChange={(e) =>
                    setModifiedParams({ ...modifiedParams, director_prior_avg_revenue: Number(e.target.value) })
                  }
                  className="w-full accent-[#8052ff] cursor-pointer"
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-400">Studio Historical Avg</span>
                  <span className="text-zinc-200 font-mono font-medium">
                    {formatCurrency(modifiedParams.primary_production_company_prior_avg_revenue)}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="600000000"
                  step="10000000"
                  value={modifiedParams.primary_production_company_prior_avg_revenue}
                  onChange={(e) =>
                    setModifiedParams({
                      ...modifiedParams,
                      primary_production_company_prior_avg_revenue: Number(e.target.value),
                    })
                  }
                  className="w-full accent-[#8052ff] cursor-pointer"
                />
              </div>
            </div>

            {/* Multi-Genre Selector */}
            <div>
              <label className="text-xs font-medium text-zinc-400 block mb-2">
                Genres ({modifiedParams.genres?.length || 0} selected)
              </label>
              <div className="flex flex-wrap gap-2">
                {ALL_GENRES.map((g) => {
                  const isSelected = modifiedParams.genres?.includes(g);
                  return (
                    <button
                      key={g}
                      type="button"
                      onClick={() => handleGenreToggle(g)}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                        isSelected
                          ? 'bg-[#8052ff] text-white shadow-md shadow-[#8052ff]/30'
                          : 'bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white'
                      }`}
                    >
                      {g}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Right Live Simulated Forecast Dashboard (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Simulated Box Office Revenue Card */}
          <div className="void-card p-6 border-[#8052ff]/40 shadow-2xl relative overflow-hidden">
            <div className="absolute -right-12 -top-12 w-48 h-48 bg-[#8052ff]/10 rounded-full blur-3xl pointer-events-none" />

            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono uppercase tracking-wider text-[#8052ff] font-semibold">
                Simulated Outcome
              </span>
              <TierBadge tier={simulationResult?.modified_predicted_tier || 'Hit'} />
            </div>

            <div className="space-y-1">
              <span className="text-xs text-zinc-400 font-mono">Predicted Worldwide Revenue</span>
              <div className="text-4xl font-extrabold text-white font-mono tracking-tight">
                {formatCurrency(simulationResult?.modified_predicted_revenue)}
              </div>
            </div>

            {/* Delta Highlights */}
            {simulationResult && (
              <div className="mt-6 pt-6 border-t border-zinc-900 grid grid-cols-2 gap-4">
                <div className="p-3 rounded-xl bg-black border border-zinc-800">
                  <span className="text-zinc-500 text-[10px] font-mono block">Revenue Delta</span>
                  <div
                    className={`text-sm font-bold font-mono mt-0.5 ${
                      simulationResult.revenue_delta >= 0 ? 'text-emerald-400' : 'text-[#ff5c7a]'
                    }`}
                  >
                    {simulationResult.revenue_delta >= 0 ? '+' : ''}
                    {formatCurrency(simulationResult.revenue_delta)}
                    <span className="text-[10px] ml-1 font-normal text-zinc-400">
                      ({simulationResult.revenue_delta_percent >= 0 ? '+' : ''}
                      {simulationResult.revenue_delta_percent}%)
                    </span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-black border border-zinc-800">
                  <span className="text-zinc-500 text-[10px] font-mono block">Predicted ROI</span>
                  <div
                    className={`text-sm font-bold font-mono mt-0.5 ${
                      simulationResult.modified_predicted_roi >= 0 ? 'text-[#ffb829]' : 'text-[#ff5c7a]'
                    }`}
                  >
                    {(simulationResult.modified_predicted_roi * 100).toFixed(1)}%
                    <span className="text-[10px] ml-1 font-normal text-zinc-400">
                      ({simulationResult.roi_delta >= 0 ? '+' : ''}
                      {(simulationResult.roi_delta * 100).toFixed(1)}%)
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Top Positive/Negative Drivers for Simulation */}
          <div className="void-card p-6 space-y-4">
            <h4 className="text-sm font-semibold text-white">Scenario Drivers</h4>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[11px] font-mono text-[#ffb829] uppercase tracking-wider block mb-1.5">
                  Top Positive Contributors
                </span>
                <div className="space-y-1.5">
                  {simulationResult?.modified_top_positive_factors?.slice(0, 3).map((f, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between p-2 rounded-lg bg-zinc-950 border border-zinc-900"
                    >
                      <span className="text-zinc-300 capitalize">{f.feature.replace(/_/g, ' ')}</span>
                      <span className="text-[#ffb829] font-mono font-bold">+{f.shap_value.toFixed(3)}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-[11px] font-mono text-[#ff5c7a] uppercase tracking-wider block mb-1.5">
                  Drag / Downward Pressures
                </span>
                <div className="space-y-1.5">
                  {simulationResult?.modified_top_negative_factors?.slice(0, 3).map((f, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between p-2 rounded-lg bg-zinc-950 border border-zinc-900"
                    >
                      <span className="text-zinc-300 capitalize">{f.feature.replace(/_/g, ' ')}</span>
                      <span className="text-[#ff5c7a] font-mono font-bold">{f.shap_value.toFixed(3)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
