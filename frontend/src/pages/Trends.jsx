import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  BarChart2,
  Calendar,
  Layers,
  Sparkles,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Legend,
} from 'recharts';
import { fetchTrends } from '../api/client';

export const Trends = () => {
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadTrends = async () => {
      try {
        setLoading(true);
        const data = await fetchTrends();
        setTrends(data);
      } catch (err) {
        console.error('Error fetching trends:', err);
      } finally {
        setLoading(false);
      }
    };
    loadTrends();
  }, []);

  const formatCurrencyM = (val) => `$${(val / 1_000_000).toFixed(0)}M`;

  const genreData = (trends?.genre_trends || []).map((g) => ({
    name: g.genre,
    avgRevenueM: +(g.avg_revenue / 1_000_000).toFixed(1),
    avgBudgetM: +(g.avg_budget / 1_000_000).toFixed(1),
    avgRoi: +g.avg_roi.toFixed(2),
    hitRate: g.hit_rate_percent,
  }));

  const yearlyData = (trends?.yearly_trends || []).map((y) => ({
    year: y.release_year,
    avgRevenueM: +(y.avg_revenue / 1_000_000).toFixed(1),
    avgBudgetM: +(y.avg_budget / 1_000_000).toFixed(1),
    totalMovies: y.movie_count,
  }));

  const seasonData = (trends?.seasonality_trends || []).map((s) => ({
    month: s.month_name,
    avgRevenueM: +(s.avg_revenue / 1_000_000).toFixed(1),
    avgRoi: +s.avg_roi.toFixed(2),
    count: s.movie_count,
  }));

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Film Industry Analytics & Macro Trends</h1>
        <p className="text-zinc-400 text-sm mt-1">
          Historical analysis across genres, release year inflation, and calendar seasonality across 3,931 films.
        </p>
      </div>

      {/* Grid: Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Genre Revenue vs Budget Chart */}
        <div className="void-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-white">Average Revenue vs Budget by Genre</h3>
              <p className="text-xs text-zinc-400">USD Millions ($M)</p>
            </div>
          </div>

          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={genreData.slice(0, 10)} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f1f1f" />
                <XAxis
                  dataKey="name"
                  stroke="#9a9a9a"
                  tick={{ fill: '#9a9a9a', fontSize: 10 }}
                  angle={-35}
                  textAnchor="end"
                />
                <YAxis stroke="#9a9a9a" tick={{ fill: '#9a9a9a', fontSize: 10 }} unit="M" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#09090b', borderColor: '#27272a', borderRadius: '12px', fontSize: '11px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="avgRevenueM" name="Avg Revenue" fill="#8052ff" radius={[4, 4, 0, 0]} />
                <Bar dataKey="avgBudgetM" name="Avg Budget" fill="#ffb829" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Release Month Seasonality Chart */}
        <div className="void-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-white">Monthly Release Seasonality</h3>
              <p className="text-xs text-zinc-400">Peak box office returns in Summer & Holiday windows</p>
            </div>
          </div>

          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={seasonData} margin={{ top: 10, right: 10, left: -10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f1f1f" />
                <XAxis dataKey="month" stroke="#9a9a9a" tick={{ fill: '#9a9a9a', fontSize: 11 }} />
                <YAxis stroke="#9a9a9a" tick={{ fill: '#9a9a9a', fontSize: 10 }} unit="M" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#09090b', borderColor: '#27272a', borderRadius: '12px', fontSize: '11px' }}
                />
                <Bar dataKey="avgRevenueM" name="Avg Box Office ($M)" radius={[4, 4, 0, 0]}>
                  {seasonData.map((entry, index) => {
                    const isPeak = ['Jun', 'Jul', 'Nov', 'Dec'].includes(entry.month);
                    return <Cell key={`cell-${index}`} fill={isPeak ? '#ffb829' : '#8052ff'} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Historical Evolution Timeline (1990 - Present) */}
        <div className="void-card p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-white">Historical Box Office Evolution (1990 – 2025)</h3>
              <p className="text-xs text-zinc-400">Average production budget vs revenue growth over 35 years</p>
            </div>
          </div>

          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={yearlyData} margin={{ top: 10, right: 20, left: -10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f1f1f" />
                <XAxis dataKey="year" stroke="#9a9a9a" tick={{ fill: '#9a9a9a', fontSize: 11 }} />
                <YAxis stroke="#9a9a9a" tick={{ fill: '#9a9a9a', fontSize: 10 }} unit="M" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#09090b', borderColor: '#27272a', borderRadius: '12px', fontSize: '11px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line
                  type="monotone"
                  dataKey="avgRevenueM"
                  name="Avg Revenue ($M)"
                  stroke="#8052ff"
                  strokeWidth={2.5}
                  dot={{ fill: '#8052ff', r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="avgBudgetM"
                  name="Avg Budget ($M)"
                  stroke="#ffb829"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={{ fill: '#ffb829', r: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
