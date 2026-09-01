import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts';

export const ShapWaterfall = ({ contributions = [], baseValue = 0, predictedValue = 0 }) => {
  // Take top 8 contributors
  const displayContributions = contributions.slice(0, 8);

  const data = displayContributions.map((c) => ({
    feature: c.feature
      .replace(/_/g, ' ')
      .replace(/genre /g, '')
      .replace(/\b\w/g, (l) => l.toUpperCase()),
    value: c.value,
    shapValue: c.shap_value,
    isPositive: c.shap_value >= 0,
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="bg-zinc-950 border border-zinc-800 p-3 rounded-xl shadow-xl text-xs font-mono">
          <p className="font-semibold text-white mb-1">{d.feature}</p>
          <p className="text-zinc-400">Feature Value: <span className="text-zinc-200">{d.value}</span></p>
          <p className="text-zinc-400">
            SHAP Contribution:{' '}
            <span className={d.isPositive ? 'text-[#ffb829] font-bold' : 'text-[#ff5c7a] font-bold'}>
              {d.isPositive ? '+' : ''}{d.shapValue.toFixed(4)}
            </span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <div className="flex items-center justify-between text-xs font-mono text-zinc-400 mb-3 px-2">
        <div>
          Baseline Value: <span className="text-zinc-200 font-semibold">${(baseValue / 1_000_000).toFixed(1)}M</span>
        </div>
        <div>
          Final Prediction: <span className="text-[#8052ff] font-semibold">${(predictedValue / 1_000_000).toFixed(1)}M</span>
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={data}
            margin={{ top: 5, right: 20, left: 90, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1f1f1f" horizontal={false} />
            <XAxis
              type="number"
              stroke="#9a9a9a"
              tick={{ fill: '#9a9a9a', fontSize: 10 }}
              label={{ value: 'Feature Impact on Prediction', position: 'insideBottom', offset: -5, fill: '#9a9a9a', fontSize: 10 }}
            />
            <YAxis
              type="category"
              dataKey="feature"
              stroke="#9a9a9a"
              tick={{ fill: '#ffffff', fontSize: 11 }}
              width={110}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255, 255, 255, 0.02)' }} />
            <ReferenceLine x={0} stroke="#3f3f46" strokeWidth={1} />
            <Bar dataKey="shapValue" radius={[3, 3, 3, 3]}>
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.isPositive ? '#ffb829' : '#ff5c7a'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="flex items-center justify-center gap-6 mt-2 text-[11px] font-mono">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-[#ffb829]" />
          <span className="text-zinc-400">Positive Impact (Pushes Revenue Up)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-[#ff5c7a]" />
          <span className="text-zinc-400">Negative Impact (Pulls Revenue Down)</span>
        </div>
      </div>
    </div>
  );
};
