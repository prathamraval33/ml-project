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
} from 'recharts';

export const ShapSummaryBar = ({ featureImportances = [], topN = 12 }) => {
  const data = featureImportances
    .slice(0, topN)
    .map((item) => ({
      feature: item.feature
        .replace(/_/g, ' ')
        .replace(/genre /g, '')
        .replace(/\b\w/g, (l) => l.toUpperCase()),
      rawFeature: item.feature,
      importance: item.mean_abs_shap,
    }))
    .reverse(); // Reverse so highest importance appears at the top

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="bg-zinc-950 border border-zinc-800 p-3 rounded-xl shadow-xl text-xs font-mono">
          <p className="font-semibold text-white mb-1">{d.feature}</p>
          <p className="text-zinc-400">
            Mean |SHAP| Impact:{' '}
            <span className="text-[#8052ff] font-bold">{d.importance.toFixed(4)}</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-96">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 10, right: 30, left: 100, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#1f1f1f" horizontal={false} />
          <XAxis
            type="number"
            stroke="#9a9a9a"
            tick={{ fill: '#9a9a9a', fontSize: 11 }}
            label={{ value: 'Mean |SHAP Value| (Impact on log revenue)', position: 'insideBottom', offset: -5, fill: '#9a9a9a', fontSize: 11 }}
          />
          <YAxis
            type="category"
            dataKey="feature"
            stroke="#9a9a9a"
            tick={{ fill: '#ffffff', fontSize: 11, fontWeight: 500 }}
            width={120}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255, 255, 255, 0.02)' }} />
          <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={index >= data.length - 3 ? '#ffb829' : '#8052ff'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
