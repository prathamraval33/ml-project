import { create } from 'zustand';

export const useUiStore = create((set) => ({
  activeTab: 'overview', // 'overview', 'features', 'explorer', 'whatif', 'trends'
  setActiveTab: (tab) => set({ activeTab: tab }),

  selectedMovieId: null,
  setSelectedMovieId: (id) => set({ selectedMovieId: id }),

  // Explorer Filters
  explorerSearch: '',
  setExplorerSearch: (search) => set({ explorerSearch: search }),
  explorerGenre: '',
  setExplorerGenre: (genre) => set({ explorerGenre: genre }),
  explorerTier: '',
  setExplorerTier: (tier) => set({ explorerTier: tier }),

  // WhatIf Base Movie
  whatIfBaseMovie: null,
  setWhatIfBaseMovie: (movie) => set({ whatIfBaseMovie: movie }),
}));
