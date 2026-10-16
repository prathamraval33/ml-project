import React from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

export const PredictedVsActualScatter = ({ movies = [] }) => {
  const safeMovies = Array.isArray(movies) ? movies : [];
  // Format data for chart (convert USD to Millions for clean readable axes)
  const data = safeMovies
    .filter((m) => m && m.revenue > 0 && m.predicted_revenue > 0)
    .map((m) => ({
      title: m.title || 'Untitled',
      actualM: +(m.revenue / 1_000_000).toFixed(2),
      predictedM: +(m.predicted_revenue / 1_000_000).toFixed(2),
      tier: m.success_tier || 'Hit',
      budgetM: +(m.budget / 1_000_000).toFixed(2),
    }));

  const maxVal = data.length > 0
    ? Math.max(...data.map((d) => Math.max(d.actualM, d.predictedM)), 100)
    : 100;

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="bg-zinc-950 border border-zinc-800 p-3 rounded-xl shadow-xl text-xs">
          <p className="font-semibold text-white mb-1.5">{d.title}</p>
          <div className="space-y-1 font-mono">
            <p className="text-zinc-400">
              Actual Box Office: <span className="text-emerald-400 font-bold">${d.actualM}M</span>
            </p>
            <p className="text-zinc-400">
              Predicted: <span className="text-[#8052ff] font-bold">${d.predictedM}M</span>
            </p>
            <p className="text-zinc-400">
              Budget: <span className="text-zinc-300">${d.budgetM}M</span>
            </p>
            <p className="text-zinc-400">
              Success Tier: <span className="text-[#ffb829]">{d.tier}</span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f1f1f" />
          <XAxis
            type="number"
            dataKey="actualM"
            name="Actual Revenue"
            unit="M"
            stroke="#9a9a9a"
            tick={{ fill: '#9a9a9a', fontSize: 11 }}
            label={{ value: 'Actual Box Office Revenue ($M)', position: 'insideBottom', offset: -10, fill: '#9a9a9a', fontSize: 12 }}
          />
          <YAxis
            type="number"
            dataKey="predictedM"
            name="Predicted Revenue"
            unit="M"
            stroke="#9a9a9a"
            tick={{ fill: '#9a9a9a', fontSize: 11 }}
            label={{ value: 'Predicted Revenue ($M)', angle: -90, position: 'insideLeft', offset: 0, fill: '#9a9a9a', fontSize: 12 }}
          />
          <ZAxis range={[25, 25]} />
          <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3', stroke: '#3f3f46' }} />
          {/* Identity Line y = x representing ideal predictions */}
          <ReferenceLine
            segment={[
              { x: 0, y: 0 },
              { x: maxVal, y: maxVal },
            ]}
            stroke="#ffb829"
            strokeDasharray="4 4"
            strokeWidth={1.5}
          />
          <Scatter name="Films" data={data} fill="#8052ff" fillOpacity={0.75} />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};
