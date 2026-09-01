import React, { useEffect, useState } from 'react';
import { Sparkles, ShieldAlert, Cpu, CheckCircle2, Layers } from 'lucide-react';
import { ShapSummaryBar } from '../components/charts/ShapSummaryBar';
import { fetchGlobalShap, fetchAblationResults } from '../api/client';

export const FeatureImportance = () => {
  const [globalShap, setGlobalShap] = useState(null);
  const [ablationResults, setAblationResults] = useState([]);
  const [activeVariant, setActiveVariant] = useState('prerelease');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadShapData = async () => {
      try {
        setLoading(true);
        const [shapData, ablationData] = await Promise.all([
          fetchGlobalShap(),
          fetchAblationResults(),
        ]);
        setGlobalShap(shapData);
        setAblationResults(ablationData || []);
      } catch (err) {
        console.error('Error loading SHAP data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadShapData();
  }, []);

  const featureImportances = globalShap?.feature_importances || [];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#8052ff]/10 border border-[#8052ff]/20 text-[#8052ff] text-xs font-mono mb-3">
          <Cpu className="w-3.5 h-3.5" />
          <span>Model Interpretability & Ablation</span>
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Global Feature Importance & Drivers</h1>
        <p className="text-zinc-400 text-sm mt-1 max-w-3xl">
          SHAP (SHapley Additive exPlanations) values computed via TreeExplainer on the champion XGBoost model. Discover which pre-release variables drive box office returns.
        </p>
      </div>

      {/* Main SHAP Chart Card */}
      <div className="void-card p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h3 className="text-base font-semibold text-white">Mean Absolute SHAP Values (Global Impact)</h3>
            <p className="text-xs text-zinc-400 mt-0.5">
              Top features ranked by their average absolute magnitude on log revenue predictions.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="w-3 h-3 rounded-sm bg-[#ffb829]" />
            <span className="text-zinc-300">Top 3 Dominant Drivers</span>
            <span className="w-3 h-3 rounded-sm bg-[#8052ff] ml-3" />
            <span className="text-zinc-300">Other Significant Features</span>
          </div>
        </div>

        <ShapSummaryBar featureImportances={featureImportances} topN={12} />
      </div>

      {/* Key Feature Insights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="void-card p-5 space-y-3">
          <div className="flex items-center gap-2 text-[#ffb829] text-xs font-bold font-mono uppercase">
            <CheckCircle2 className="w-4 h-4" />
            <span>#1 Production Budget</span>
          </div>
          <p className="text-sm font-semibold text-white">The Single Strongest Predictor</p>
          <p className="text-xs text-zinc-400 leading-relaxed">
            Budget scale exhibits an overwhelming positive log-linear correlation with worldwide box office. Higher investment unlocks wider distribution, larger marketing campaigns, and higher production values.
          </p>
        </div>

        <div className="void-card p-5 space-y-3">
          <div className="flex items-center gap-2 text-[#8052ff] text-xs font-bold font-mono uppercase">
            <CheckCircle2 className="w-4 h-4" />
            <span>#2 Historical Track Record</span>
          </div>
          <p className="text-sm font-semibold text-white">Director & Studio Prior Averages</p>
          <p className="text-xs text-zinc-400 leading-relaxed">
            Computed strictly using chronological time-ordered cutoffs (zero data leakage). A director's or production studio's past revenue history serves as a heavy confidence multiplier in the model.
          </p>
        </div>

        <div className="void-card p-5 space-y-3">
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold font-mono uppercase">
            <CheckCircle2 className="w-4 h-4" />
            <span>#3 Release Seasonality & Genre</span>
          </div>
          <p className="text-sm font-semibold text-white">Holiday Windows & Blockbuster Genres</p>
          <p className="text-xs text-zinc-400 leading-relaxed">
            Release months in June, July, November, and December provide a significant SHAP uplift. Animation, Adventure, and Action genres demonstrate the highest baseline gross multiplier.
          </p>
        </div>
      </div>

      {/* Leakage Ablation Study Section */}
      <div className="void-card p-6 space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="inline-flex items-center gap-1.5 text-xs font-mono text-[#ffb829] mb-1">
              <ShieldAlert className="w-4 h-4" />
              <span>Rigorous ML Evaluation</span>
            </div>
            <h3 className="text-lg font-semibold text-white">Target Leakage Ablation Study</h3>
            <p className="text-xs text-zinc-400 mt-1 max-w-2xl">
              Comparing pure Pre-Release models (safe for real-world pre-production forecasting) against Early-Signal models (which include post-release TMDB popularity and vote counts).
            </p>
          </div>
        </div>

        {/* Ablation Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="text-zinc-500 font-mono hairline-bottom">
                <th className="pb-3 font-medium">Model Family</th>
                <th className="pb-3 font-medium">Feature Set</th>
                <th className="pb-3 font-medium">Feature Count</th>
                <th className="pb-3 font-medium">Test R² (Log)</th>
                <th className="pb-3 font-medium">Test RMSE</th>
                <th className="pb-3 font-medium">Test MAE</th>
                <th className="pb-3 font-medium">Pearson R</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-900 text-zinc-300">
              {ablationResults.map((row, idx) => {
                const isClean = row.feature_set.includes('Pre-Release');
                return (
                  <tr key={idx} className="hover:bg-zinc-900/40 transition-colors">
                    <td className="py-3 font-semibold text-white">{row.model}</td>
                    <td className="py-3">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono ${
                          isClean
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        }`}
                      >
                        {row.feature_set}
                      </span>
                    </td>
                    <td className="py-3 font-mono text-zinc-400">{row.features_count}</td>
                    <td className="py-3 font-mono font-medium text-white">{row.r2_log.toFixed(4)}</td>
                    <td className="py-3 font-mono text-zinc-400">{row.rmse_log.toFixed(4)}</td>
                    <td className="py-3 font-mono text-zinc-400">{row.mae_log.toFixed(4)}</td>
                    <td className="py-3 font-mono text-[#8052ff] font-bold">{row.pearson_r.toFixed(4)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 text-xs text-zinc-400 space-y-1 font-mono">
          <p className="text-zinc-200 font-semibold">💡 Scientific Finding:</p>
          <p>
            Adding post-release `popularity` and `vote_count` artificially inflates correlation (Pearson R ~0.69 vs 0.64) due to hindsight audience signals. CineForecast's production pipeline intentionally deploys the pure <strong>Pre-Release feature set</strong> to prevent operational leakage in real-world forecasting.
          </p>
        </div>
      </div>
    </div>
  );
};
