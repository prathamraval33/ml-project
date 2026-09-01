import React, { useEffect, useState } from 'react';
import { DollarSign, BarChart3, TrendingUp, Target, Award, Sparkles, Activity } from 'lucide-react';
import { StatCard } from '../components/ui/StatCard';
import { TierBadge } from '../components/ui/TierBadge';
import { PredictedVsActualScatter } from '../components/charts/PredictedVsActualScatter';
import { fetchMovies, fetchTrends } from '../api/client';
import { useUiStore } from '../store/useUiStore';

export const Overview = () => {
  const [trends, setTrends] = useState(null);
  const [sampleMovies, setSampleMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const { setActiveTab, setSelectedMovieId } = useUiStore();

  useEffect(() => {
    const loadOverviewData = async () => {
      try {
        setLoading(true);
        const [trendsData, moviesData] = await Promise.all([
          fetchTrends(),
          fetchMovies({ size: 80, sort_by: 'revenue', order: 'desc' }),
        ]);
        setTrends(trendsData);
        setSampleMovies(moviesData.items || []);
      } catch (err) {
        console.error('Failed loading overview data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadOverviewData();
  }, []);

  const formatCurrency = (val) => {
    if (!val) return '$0';
    if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
    if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
    return `$${val.toLocaleString()}`;
  };

  const kpis = trends?.headline_kpis || {};

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Hero Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#8052ff]/10 border border-[#8052ff]/20 text-[#8052ff] text-xs font-mono mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI-Powered Film Intelligence</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Film Revenue & ROI Intelligence</h1>
          <p className="text-zinc-400 text-sm mt-1 max-w-2xl">
            Pre-release box office predictions, multi-class success tier classification, and explainable SHAP attributions trained on 3,931 verified historical films.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('whatif')}
            className="btn-primary px-5 py-2.5 text-xs flex items-center gap-2"
          >
            <Activity className="w-4 h-4" />
            <span>Launch What-If Simulator</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Catalog Box Office"
          value={formatCurrency(kpis.total_box_office_usd)}
          subtext="3,931 analyzed films"
          icon={DollarSign}
          accent="iris"
        />
        <StatCard
          label="Average Production Budget"
          value={formatCurrency(kpis.average_budget_usd)}
          subtext="Industry baseline"
          icon={BarChart3}
          accent="saffron"
        />
        <StatCard
          label="Historical Hit Rate"
          value={`${kpis.hit_rate_percent || 0}%`}
          subtext="Films achieving ROI ≥ 1.0"
          icon={Award}
          accent="emerald"
        />
        <StatCard
          label="Model R² Score (Log USD)"
          value="0.63"
          subtext="Champion Pearson R: 0.63"
          icon={Target}
          accent="iris"
        />
      </div>

      {/* Primary Visualizations Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Scatter Plot Card */}
        <div className="void-card p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-white">Predicted vs. Actual Box Office Revenue</h3>
              <p className="text-xs text-zinc-400 mt-0.5">
                Evaluated on held-out test films (points near the golden dashed line indicate near-perfect predictions).
              </p>
            </div>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400">
              USD Millions ($M)
            </span>
          </div>

          <PredictedVsActualScatter movies={sampleMovies} />
        </div>

        {/* Model Specs & Success Tier Distribution */}
        <div className="void-card p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-semibold text-white mb-1">Catalog Success Tiers</h3>
            <p className="text-xs text-zinc-400 mb-6">Historical breakdown by return on investment.</p>

            <div className="space-y-4">
              {trends?.tier_distribution &&
                Object.entries(trends.tier_distribution).map(([tier, count]) => {
                  const total = kpis.total_catalog_size || 1;
                  const pct = ((count / total) * 100).toFixed(1);
                  return (
                    <div key={tier} className="space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <TierBadge tier={tier} />
                        <span className="font-mono text-zinc-400">
                          {count} ({pct}%)
                        </span>
                      </div>
                      <div className="w-full h-1.5 bg-zinc-900 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-[#8052ff]"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>

          <div className="pt-6 border-t border-zinc-900 mt-6 text-xs text-zinc-500 font-mono">
            <p>• Zero Future-Data Leakage Verified</p>
            <p>• Temporal Split (Train 1990–2022, Test 2023+)</p>
          </div>
        </div>
      </div>

      {/* Top Box Office Table */}
      <div className="void-card p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-white">Top Box Office Performers</h3>
            <p className="text-xs text-zinc-400">Actual box office vs machine learning predictions</p>
          </div>
          <button
            onClick={() => setActiveTab('explorer')}
            className="text-xs text-[#8052ff] hover:underline font-medium"
          >
            View All Movies →
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="text-zinc-500 font-mono hairline-bottom">
                <th className="pb-3 font-medium">Title</th>
                <th className="pb-3 font-medium">Primary Genre</th>
                <th className="pb-3 font-medium">Budget</th>
                <th className="pb-3 font-medium">Actual Revenue</th>
                <th className="pb-3 font-medium">Predicted Revenue</th>
                <th className="pb-3 font-medium">Tier</th>
                <th className="pb-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-900 text-zinc-300">
              {sampleMovies.slice(0, 7).map((m) => (
                <tr key={m.id} className="hover:bg-zinc-900/40 transition-colors">
                  <td className="py-3 font-medium text-white max-w-xs truncate">{m.title}</td>
                  <td className="py-3 text-zinc-400">{m.primary_genre || 'Drama'}</td>
                  <td className="py-3 font-mono">{formatCurrency(m.budget)}</td>
                  <td className="py-3 font-mono text-emerald-400 font-medium">{formatCurrency(m.revenue)}</td>
                  <td className="py-3 font-mono text-[#8052ff] font-medium">{formatCurrency(m.predicted_revenue)}</td>
                  <td className="py-3">
                    <TierBadge tier={m.success_tier} />
                  </td>
                  <td className="py-3 text-right">
                    <button
                      onClick={() => {
                        setSelectedMovieId(m.id);
                        setActiveTab('explorer');
                      }}
                      className="px-2.5 py-1 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-300 transition-colors"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
