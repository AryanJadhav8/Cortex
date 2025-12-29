import React, { useState } from 'react';
import axios from 'axios';
import { Download, Zap, Activity, ShieldCheck, Database, FileUp } from 'lucide-react';
import DataTable from './components/layout/DataTable';
import DataHealthChart from './components/charts/DataHealthChart';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const processFile = async (file) => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await axios.post('http://localhost:8000/heal', formData);
      setReport(res.data);
    } catch (err) {
      alert("Analysis failed.");
    } finally {
      setLoading(false);
      setIsDragging(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white p-8 relative overflow-hidden">
      {/* GRID BACKGROUND */}
      <div className="absolute inset-0 z-0 opacity-[0.25]" 
           style={{ backgroundImage: 'linear-gradient(#3f3f46 1px, transparent 1px), linear-gradient(90deg, #3f3f46 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <div className="relative z-10 max-w-7xl mx-auto">
        <header className="flex justify-between items-center mb-12">
          <h1 className="text-4xl font-black italic">CORTEX <span className="text-cyan-500">AI</span></h1>
          <button onClick={() => window.open('http://localhost:8000/download')} disabled={!report}
                  className="flex items-center gap-2 border border-white/10 px-6 py-3 rounded-full font-bold disabled:opacity-20">
            <Download size={18} /> DOWNLOAD CLEANED
          </button>
        </header>

        <div className="grid grid-cols-4 gap-6 mb-8">
          <StatCard label="Model Precision" value={report?.stats?.accuracy || "N/A"} icon={<Zap className="text-cyan-500"/>} active={!!report} />
          <StatCard label="Anomalies Healed" value={report?.stats?.missing_before || "0"} icon={<ShieldCheck className="text-emerald-500"/>} active={!!report} />
          <StatCard label="Integrity Score" value={report ? "100%" : "—"} icon={<Activity className="text-blue-500"/>} active={!!report} />
          <StatCard label="Total Records" value={report?.stats?.rows || "0"} icon={<Database className="text-purple-500"/>} active={!!report} />
        </div>

        <div className="grid grid-cols-3 gap-8">
          <DataHealthChart data={report?.analysis} />
          <div className="col-span-2">
            {loading ? (
              <div className="h-[500px] bg-zinc-900/40 rounded-[2rem] flex flex-col items-center justify-center animate-pulse border border-cyan-500/20">
                <div className="w-12 h-12 border-4 border-t-cyan-500 rounded-full animate-spin mb-4" />
                <p className="font-mono text-xs text-cyan-500">HEALING DATA VECTORS...</p>
              </div>
            ) : report ? (
              <DataTable rows={report.preview_data} />
            ) : (
              <label onDragOver={(e)=>{e.preventDefault(); setIsDragging(true)}} onDragLeave={()=>setIsDragging(false)} onDrop={(e)=>{e.preventDefault(); processFile(e.dataTransfer.files[0])}}
                     className={`h-[500px] border-2 border-dashed rounded-[2.5rem] flex flex-col items-center justify-center transition-all cursor-pointer ${isDragging ? 'border-cyan-500 bg-cyan-500/10' : 'border-white/10 bg-zinc-900/10'}`}>
                <FileUp size={40} className="mb-4 text-zinc-500" />
                <p className="font-mono text-xs uppercase tracking-widest">Drop CSV to Initialize</p>
                <input type="file" className="hidden" onChange={(e)=>processFile(e.target.files[0])} />
              </label>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, active }) {
  return (
    <div className={`bg-zinc-900/50 border border-white/5 p-6 rounded-[2rem] transition-all ${active ? 'opacity-100' : 'opacity-30'}`}>
      <div className="flex justify-between items-start mb-2">
        <span className="text-[10px] font-mono text-zinc-500 uppercase">{label}</span>
        {icon}
      </div>
      <div className="text-3xl font-bold">{value}</div>
    </div>
  );
}