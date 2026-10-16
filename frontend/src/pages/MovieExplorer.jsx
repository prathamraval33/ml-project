import React, { useEffect, useState } from 'react';
import { Search, Filter, Film, ArrowUpDown, ChevronLeft, ChevronRight, X, Play, Sparkles } from 'lucide-react';
import { TierBadge } from '../components/ui/TierBadge';
import { ShapWaterfall } from '../components/charts/ShapWaterfall';
import { fetchMovies, fetchMovieShap, fetchMovieDetail } from '../api/client';
import { useUiStore } from '../store/useUiStore';

export const MovieExplorer = () => {
  const [movies, setMovies] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [genre, setGenre] = useState('');
  const [tier, setTier] = useState('');
  const [sortBy, setSortBy] = useState('revenue');
  const [order, setOrder] = useState('desc');
  const [loading, setLoading] = useState(false);

  // Detail Modal / Drawer state
  const { selectedMovieId, setSelectedMovieId, setActiveTab, setWhatIfBaseMovie } = useUiStore();
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [movieShap, setMovieShap] = useState(null);
  const [shapLoading, setShapLoading] = useState(false);

  const loadMovies = async () => {
    try {
      setLoading(true);
      const data = await fetchMovies({
        page,
        size: pageSize,
        search: search || undefined,
        genre: genre || undefined,
        tier: tier || undefined,
        sort_by: sortBy,
        order,
      });
      setMovies(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error('Error fetching movies:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMovies();
  }, [page, search, genre, tier, sortBy, order]);

  // Handle selected movie detail & SHAP explanation
  useEffect(() => {
    if (!selectedMovieId) {
      setSelectedMovie(null);
      setMovieShap(null);
      return;
    }

    const movie = movies.find((m) => m.id === selectedMovieId);
    if (movie) {
      setSelectedMovie(movie);
    } else {
      fetchMovieDetail(selectedMovieId)
        .then((detail) => setSelectedMovie(detail))
        .catch((err) => console.error('Error fetching movie detail:', err));
    }

    const loadShap = async () => {
      try {
        setShapLoading(true);
        const data = await fetchMovieShap(selectedMovieId);
        setMovieShap(data);
      } catch (err) {
        console.error('Error fetching SHAP for movie:', err);
      } finally {
        setShapLoading(false);
      }
    };
    loadShap();
  }, [selectedMovieId]);

  const formatCurrency = (val) => {
    if (!val && val !== 0) return '$0';
    if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
    if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
    return `$${val.toLocaleString()}`;
  };

  const handleSendToWhatIf = (movie) => {
    setWhatIfBaseMovie(movie);
    setActiveTab('whatif');
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Movie Explorer & Per-Film Explanations</h1>
        <p className="text-zinc-400 text-sm mt-1">
          Explore all 3,931 catalog films, compare ground truth with ML predictions, and inspect per-movie SHAP waterfalls.
        </p>
      </div>

      {/* Filters Bar */}
      <div className="void-card p-4 flex flex-wrap items-center justify-between gap-4">
        {/* Search */}
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-zinc-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by title or director..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-[#8052ff]"
          />
        </div>

        {/* Genre Filter */}
        <select
          value={genre}
          onChange={(e) => {
            setGenre(e.target.value);
            setPage(1);
          }}
          className="bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-zinc-300 focus:outline-none focus:border-[#8052ff]"
        >
          <option value="">All Genres</option>
          <option value="Action">Action</option>
          <option value="Adventure">Adventure</option>
          <option value="Animation">Animation</option>
          <option value="Comedy">Comedy</option>
          <option value="Drama">Drama</option>
          <option value="Horror">Horror</option>
          <option value="Science Fiction">Science Fiction</option>
          <option value="Thriller">Thriller</option>
        </select>

        {/* Tier Filter */}
        <select
          value={tier}
          onChange={(e) => {
            setTier(e.target.value);
            setPage(1);
          }}
          className="bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-zinc-300 focus:outline-none focus:border-[#8052ff]"
        >
          <option value="">All Tiers</option>
          <option value="Blockbuster">Blockbuster</option>
          <option value="Hit">Hit</option>
          <option value="Break-even">Break-even</option>
          <option value="Flop">Flop</option>
        </select>

        {/* Sort Field */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-zinc-300 focus:outline-none focus:border-[#8052ff]"
        >
          <option value="revenue">Sort: Revenue</option>
          <option value="budget">Sort: Budget</option>
          <option value="roi">Sort: ROI</option>
          <option value="predicted_revenue">Sort: Predicted Rev</option>
          <option value="release_year">Sort: Release Year</option>
        </select>

        {/* Sort Order */}
        <button
          onClick={() => setOrder(order === 'desc' ? 'asc' : 'desc')}
          className="btn-ghost px-3 py-2 text-xs flex items-center gap-1.5"
        >
          <ArrowUpDown className="w-3.5 h-3.5" />
          <span>{order.toUpperCase()}</span>
        </button>
      </div>

      {/* Main Table Card */}
      <div className="void-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="text-zinc-500 font-mono hairline-bottom bg-zinc-950/60">
                <th className="py-3.5 px-4 font-medium">Title & Director</th>
                <th className="py-3.5 px-4 font-medium">Genre</th>
                <th className="py-3.5 px-4 font-medium">Year</th>
                <th className="py-3.5 px-4 font-medium">Budget</th>
                <th className="py-3.5 px-4 font-medium">Actual Revenue</th>
                <th className="py-3.5 px-4 font-medium">Predicted Revenue</th>
                <th className="py-3.5 px-4 font-medium">Tier</th>
                <th className="py-3.5 px-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-900 text-zinc-300">
              {loading ? (
                <tr>
                  <td colSpan="8" className="py-12 text-center text-zinc-500 font-mono">
                    Loading catalog movies...
                  </td>
                </tr>
              ) : movies.length === 0 ? (
                <tr>
                  <td colSpan="8" className="py-12 text-center text-zinc-500 font-mono">
                    No movies match your filters.
                  </td>
                </tr>
              ) : (
                movies.map((m) => (
                  <tr
                    key={m.id}
                    onClick={() => setSelectedMovieId(m.id)}
                    className="hover:bg-zinc-900/50 cursor-pointer transition-colors"
                  >
                    <td className="py-3.5 px-4">
                      <p className="font-semibold text-white truncate max-w-xs">{m.title}</p>
                      <p className="text-[11px] text-zinc-500 truncate">{m.director || 'Unknown Director'}</p>
                    </td>
                    <td className="py-3.5 px-4 text-zinc-400">{m.primary_genre || 'Drama'}</td>
                    <td className="py-3.5 px-4 font-mono text-zinc-400">{m.release_year || '—'}</td>
                    <td className="py-3.5 px-4 font-mono">{formatCurrency(m.budget)}</td>
                    <td className="py-3.5 px-4 font-mono text-emerald-400 font-medium">{formatCurrency(m.revenue)}</td>
                    <td className="py-3.5 px-4 font-mono text-[#8052ff] font-medium">
                      {formatCurrency(m.predicted_revenue)}
                    </td>
                    <td className="py-3.5 px-4">
                      <TierBadge tier={m.success_tier} />
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedMovieId(m.id);
                        }}
                        className="px-2.5 py-1 rounded-lg bg-[#8052ff]/10 text-[#8052ff] border border-[#8052ff]/20 hover:bg-[#8052ff]/20 transition-colors font-medium text-[11px]"
                      >
                        Inspect SHAP
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 bg-zinc-950/60 hairline-top flex items-center justify-between text-xs text-zinc-400 font-mono">
          <span>
            Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total} films
          </span>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="p-1.5 rounded-lg border border-zinc-800 disabled:opacity-30 hover:bg-zinc-800 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span>
              Page {page} of {totalPages}
            </span>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
              className="p-1.5 rounded-lg border border-zinc-800 disabled:opacity-30 hover:bg-zinc-800 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Slide-out / Modal for Movie Detail & SHAP Waterfall */}
      {selectedMovieId && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex justify-end">
          <div className="w-full max-w-2xl bg-zinc-950 border-l border-zinc-800 h-full overflow-y-auto p-6 space-y-6 shadow-2xl animate-in slide-in-from-right duration-200">
            {/* Modal Header */}
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[11px] font-mono text-[#8052ff] uppercase tracking-wider">Per-Movie SHAP Attribution</span>
                <h2 className="text-xl font-bold text-white mt-0.5">{selectedMovie?.title || movieShap?.title}</h2>
                <p className="text-xs text-zinc-400 mt-0.5">
                  Director: {selectedMovie?.director || 'Unknown'} • Genre: {selectedMovie?.primary_genre || 'Drama'} • Year: {selectedMovie?.release_year || '2026'}
                </p>
              </div>
              <button
                onClick={() => setSelectedMovieId(null)}
                className="p-2 rounded-full hover:bg-zinc-800 text-zinc-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Financial Summary Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-3 rounded-xl bg-black border border-zinc-800">
                <span className="text-zinc-500 text-[10px] block">Production Budget</span>
                <span className="text-white font-bold text-sm">{formatCurrency(selectedMovie?.budget)}</span>
              </div>
              <div className="p-3 rounded-xl bg-black border border-zinc-800">
                <span className="text-zinc-500 text-[10px] block">Actual Box Office</span>
                <span className="text-emerald-400 font-bold text-sm">{formatCurrency(selectedMovie?.revenue)}</span>
              </div>
              <div className="p-3 rounded-xl bg-black border border-zinc-800">
                <span className="text-zinc-500 text-[10px] block">Predicted Revenue</span>
                <span className="text-[#8052ff] font-bold text-sm">{formatCurrency(movieShap?.predicted_revenue_usd || selectedMovie?.predicted_revenue)}</span>
              </div>
              <div className="p-3 rounded-xl bg-black border border-zinc-800">
                <span className="text-zinc-500 text-[10px] block">Success Tier</span>
                <div className="mt-1">
                  <TierBadge tier={selectedMovie?.success_tier || 'Hit'} />
                </div>
              </div>
            </div>

            {/* SHAP Waterfall Chart */}
            <div className="void-card p-5">
              <h3 className="text-sm font-semibold text-white mb-1">Feature Contribution Waterfall</h3>
              <p className="text-xs text-zinc-400 mb-4">
                How each pre-release attribute pushed or pulled the forecast away from the baseline catalog average.
              </p>

              {shapLoading ? (
                <div className="h-64 flex items-center justify-center text-xs font-mono text-zinc-500">
                  Computing SHAP values...
                </div>
              ) : movieShap ? (
                <ShapWaterfall
                  contributions={movieShap.contributions}
                  baseValue={movieShap.base_value_usd}
                  predictedValue={movieShap.predicted_revenue_usd}
                />
              ) : (
                <div className="h-64 flex items-center justify-center text-xs font-mono text-zinc-500">
                  No SHAP data available.
                </div>
              )}
            </div>

            {/* Send to What-If Button */}
            {selectedMovie && (
              <button
                onClick={() => handleSendToWhatIf(selectedMovie)}
                className="w-full btn-primary py-3 text-xs flex items-center justify-center gap-2 font-semibold"
              >
                <Play className="w-4 h-4" />
                <span>Simulate Changes for this Movie in What-If Studio →</span>
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
