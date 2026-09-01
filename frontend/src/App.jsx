import React from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { Overview } from './pages/Overview';
import { FeatureImportance } from './pages/FeatureImportance';
import { MovieExplorer } from './pages/MovieExplorer';
import { WhatIfSimulator } from './pages/WhatIfSimulator';
import { Trends } from './pages/Trends';
import { useUiStore } from './store/useUiStore';

export function App() {
  const { activeTab } = useUiStore();

  const getPageHeader = () => {
    switch (activeTab) {
      case 'overview':
        return { title: 'Executive Overview', subtitle: 'Macro performance & predictive intelligence' };
      case 'features':
        return { title: 'Feature Attribution & SHAP', subtitle: 'Global variable weights and leakage ablation' };
      case 'explorer':
        return { title: 'Catalog Explorer', subtitle: 'Inspect 3,931 verified historical films & SHAP waterfalls' };
      case 'whatif':
        return { title: 'What-If Studio', subtitle: 'Real-time pre-release sensitivity analysis' };
      case 'trends':
        return { title: 'Macro Trends', subtitle: 'Industry-wide genre, budget, and seasonality analytics' };
      default:
        return { title: 'CineForecast', subtitle: 'Film revenue forecasting platform' };
    }
  };

  const headerInfo = getPageHeader();

  return (
    <div className="flex min-h-screen bg-black text-white font-sans selection:bg-[#8052ff]/30 selection:text-white">
      {/* Fixed Left Navigation Sidebar */}
      <Sidebar />

      {/* Main Content Viewport */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header title={headerInfo.title} subtitle={headerInfo.subtitle} />

        <main className="flex-1 pb-16">
          {activeTab === 'overview' && <Overview />}
          {activeTab === 'features' && <FeatureImportance />}
          {activeTab === 'explorer' && <MovieExplorer />}
          {activeTab === 'whatif' && <WhatIfSimulator />}
          {activeTab === 'trends' && <Trends />}
        </main>
      </div>
    </div>
  );
}

export default App;
