import React, { useState } from 'react';
import axios from 'axios';
import { Download, Zap, Activity, ShieldCheck, Database, FileUp, RefreshCw } from 'lucide-react';
import DataTable from './components/layout/DataTable';
import DataHealthChart from './components/charts/DataHealthChart';
import ColumnSelector from './components/layout/ColumnSelector';
import TargetSelector from './components/layout/TargetSelector';
import CortexInsights from './components/layout/CortexInsights';
import FeatureImportance from './components/charts/FeatureImportance';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [file, setFile] = useState(null); 
  const [selectedCols, setSelectedCols] = useState([]);
  const [selectedTarget, setSelectedTarget] = useState(null);
  const [insights, setInsights] = useState([]);
  const [openDropdown, setOpenDropdown] = useState(null); // NEW: Track which dropdown is open

  // INITIAL FILE UPLOAD
  const processFile = async (uploadedFile) => {
    if (!uploadedFile) return;
    setFile(uploadedFile);
    setLoading(true);

    const formData = new FormData();
    formData.append('file', uploadedFile);
    formData.append('selected_columns', JSON.stringify([])); 

    try {
      const res = await axios.post('http://localhost:8000/heal', formData);
      setReport(res.data);
      // Default: All columns selected except target
      const allCols = res.data.analysis.column_diagnostics
        .map(c => c.value)
        .filter(c => c !== res.data.stats.target_used);
      setSelectedCols(allCols);
      setSelectedTarget(res.data.stats.target_used);
      
      // Initial System Log
      setInsights([{
        id: Date.now(),
        trend: "STABLE",
        diff: "INIT",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        message: "Neural baseline established. Data vectors initialized and healed."
      }]);
    } catch (err) {
      alert("Analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  // RE-CALIBRATION WITH DYNAMIC REASONING
  const handleRefine = async () => {
    if (!file || !selectedTarget) return;
    setLoading(true);

    const prevAccuracy = parseFloat(report?.stats?.accuracy || 0);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('selected_columns', JSON.stringify(selectedCols));
    formData.append('target_column', selectedTarget);

    try {
      const res = await axios.post('http://localhost:8000/heal', formData);
      const newAccuracy = parseFloat(res.data.stats.accuracy);
      
      // Calculate changes for reasoning
      const diff = (newAccuracy - prevAccuracy).toFixed(1);
      const trend = diff > 0 ? "OPTIMIZED" : diff < 0 ? "DEGRADED" : "STABLE";
      
      const totalColsCount = report.analysis.column_diagnostics.length;
      const activeColsCount = selectedCols.length;
      const prunedCount = totalColsCount - activeColsCount;

      // Dynamic Reasoning Logic
      let dynamicMessage = "";
      if (diff > 0) {
        dynamicMessage = `Optimization successful. Pruning ${prunedCount} noisy vectors enhanced the focus on primary predictors.`;
      } else if (diff < 0) {
        dynamicMessage = `Intelligence degradation detected. Removing features has limited the model's ability to map patterns in the data space.`;
      } else {
        dynamicMessage = "Model weights recalculated. System remains stable with the current feature set.";
      }

      const newEntry = {
        id: Date.now(),
        trend: trend,
        diff: diff > 0 ? `+${diff}%` : `${diff}%`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        message: dynamicMessage
      };

      setInsights(prev => [newEntry, ...prev].slice(0, 5)); 
      setReport(res.data);
    } catch (err) {
      alert("Refining failed.");
    } finally {
      setLoading(false);
    }
  };

  const toggleColumn = (colValue) => {
    setSelectedCols(prev => {
      if (prev.includes(colValue)) {
        return prev.filter(c => c !== colValue);
      } else {
        return [...prev, colValue];
      }
    });
  };

  const handleTargetChange = (newTarget) => {
    setSelectedTarget(newTarget);
    // Remove target from selected columns if it's there
    setSelectedCols(prev => prev.filter(c => c !== newTarget));
    setOpenDropdown(null); // Close dropdown after selection
  };

  // Helper to toggle dropdown state
  const toggleDropdown = (name) => {
    setOpenDropdown(openDropdown === name ? null : name);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white p-8 relative overflow-hidden">
      {/* Background Grid Layer */}
      <div className="absolute inset-0 z-0 opacity-[0.25]" 
           style={{ backgroundImage: 'linear-gradient(#3f3f46 1px, transparent 1px), linear-gradient(90deg, #3f3f46 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header Area */}
        <header className="flex justify-between items-center mb-12">
          <h1 className="text-4xl font-black italic">CORTEX <span className="text-cyan-500">AI</span></h1>
          <button 
            onClick={() => window.open('http://localhost:8000/download')} 
            disabled={!report}
            className="flex items-center gap-2 border border-white/10 px-6 py-3 rounded-full font-bold disabled:opacity-20 hover:bg-white hover:text-black transition-all"
          >
            <Download size={18} /> DOWNLOAD
          </button>
        </header>

        {/* Global Statistics Cards */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          <StatCard label="Model Precision" value={report?.stats?.accuracy || "N/A"} icon={<Zap className="text-cyan-500"/>} active={!!report} />
          <StatCard label="Anomalies Healed" value={report?.stats?.missing_before || "0"} icon={<ShieldCheck className="text-emerald-500"/>} active={!!report} />
          <StatCard label="Integrity Score" value={report ? "100%" : "—"} icon={<Activity className="text-blue-500"/>} active={!!report} />
          <StatCard label="Total Records" value={report?.stats?.rows || "0"} icon={<Database className="text-purple-500"/>} active={!!report} />
        </div>

        {/* Workspace Grid */}
        <div className="grid grid-cols-3 gap-8">
          
          {/* Left Sidebar: Controls & Analytics */}
          <div className="space-y-6 z-50">
            {report && (
              <div className="relative z-[100] flex flex-col gap-3 p-1 bg-zinc-900/30 rounded-[2rem] border border-white/5 shadow-2xl backdrop-blur-md">
                <div onClick={() => toggleDropdown('target')}>
                  <TargetSelector
                    diagnostics={report.analysis.column_diagnostics}
                    selectedTarget={selectedTarget}
                    onTargetChange={handleTargetChange}
                    isOpen={openDropdown === 'target'}
                    onToggle={() => toggleDropdown('target')}
                  />
                </div>
                <div onClick={() => toggleDropdown('features')}>
                  <ColumnSelector 
                    diagnostics={report.analysis.column_diagnostics} 
                    selectedColumns={selectedCols}
                    onSelectionChange={toggleColumn}
                    isOpen={openDropdown === 'features'}
                    onToggle={() => toggleDropdown('features')}
                  />
                </div>
                <button 
                  onClick={handleRefine}
                  className="w-full h-14 bg-cyan-500 hover:bg-cyan-400 text-black font-black rounded-2xl transition-all flex items-center justify-center gap-2 uppercase tracking-widest text-xs"
                >
                  <RefreshCw size={16} /> Re-Calibrate Intelligence
                </button>
                <div onClick={() => toggleDropdown('importance')}>
                  <FeatureImportance 
                    data={report?.analysis?.feature_importance}
                    isOpen={openDropdown === 'importance'}
                    onToggle={() => toggleDropdown('importance')}
                  />
                </div>
              </div>
            )}
            
            <DataHealthChart data={report?.analysis} />
            
            {/* Intelligence Log Panel */}
            <CortexInsights logs={insights} />
          </div>

          {/* Right Main Panel: Data Viewer */}
          <div className="col-span-2">
            {loading ? (
              <div className="h-[600px] bg-zinc-900/40 rounded-[2rem] flex flex-col items-center justify-center animate-pulse border border-cyan-500/20 shadow-[0_0_50px_rgba(6,182,212,0.1)]">
                <div className="w-12 h-12 border-4 border-white/5 border-t-cyan-500 rounded-full animate-spin mb-4" />
                <p className="font-mono text-xs text-cyan-500 tracking-[0.3em]">SYNCHRONIZING VECTORS...</p>
              </div>
            ) : report ? (
              <DataTable rows={report.preview_data} />
            ) : (
              <label 
                onDragOver={(e)=>{e.preventDefault()}} 
                onDrop={(e)=>{e.preventDefault(); processFile(e.dataTransfer.files[0])}}
                className="h-[600px] border-2 border-dashed border-white/10 rounded-[2.5rem] flex flex-col items-center justify-center cursor-pointer hover:bg-zinc-900/20 hover:border-cyan-500/40 transition-all group"
              >
                <div className="p-8 rounded-full bg-white/5 mb-4 group-hover:scale-110 transition-transform">
                  <FileUp size={40} className="text-zinc-500 group-hover:text-cyan-500 transition-colors" />
                </div>
                <p className="font-mono text-xs uppercase tracking-[0.2em] text-zinc-500">Drop CSV to Initialize Cortex</p>
                <input type="file" className="hidden" onChange={(e)=>processFile(e.target.files[0])} />
              </label>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}

// Sub-component for individual stat cards
function StatCard({ label, value, icon, active }) {
  return (
    <div className={`bg-zinc-900/50 border border-white/5 p-6 rounded-[2rem] transition-all duration-700 ${active ? 'opacity-100 translate-y-0' : 'opacity-30 translate-y-4'}`}>
      <div className="flex justify-between items-start mb-2">
        <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">{label}</span>
        <div className={`${active ? 'animate-pulse' : ''}`}>{icon}</div>
      </div>
      <div className="text-3xl font-bold tracking-tighter">
        {typeof value === 'number' && value <= 1 ? `${(value * 100).toFixed(1)}%` : value}
      </div>
    </div>
  );
}