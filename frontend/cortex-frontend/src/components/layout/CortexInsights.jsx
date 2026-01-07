import React from 'react';
import { Terminal, Cpu, TrendingUp, TrendingDown, Minus, HelpCircle } from 'lucide-react';

export default function CortexInsights({ logs }) {
  const getTrendTooltip = (trend) => {
    const tooltips = {
      OPTIMIZED: "Model performance improved with current feature selection",
      DEGRADED: "Model performance declined after feature changes",
      STABLE: "Model performance remained consistent"
    };
    return tooltips[trend] || "";
  };

  return (
    <div className="bg-zinc-900/40 border border-white/5 rounded-[2rem] p-6 backdrop-blur-md overflow-hidden flex flex-col h-[300px]">
      <div className="flex items-center gap-2 mb-4 border-b border-white/5 pb-4">
        <Terminal size={16} className="text-cyan-500" />
        <h3 className="text-xs font-mono uppercase tracking-[0.2em] text-zinc-400">Intelligence Log</h3>
        <div className="group relative ml-auto">
          <HelpCircle size={14} className="text-zinc-600 hover:text-cyan-400 cursor-help transition-colors" />
          <div className="absolute right-0 hidden group-hover:block bg-zinc-950 border border-cyan-500/50 rounded-lg p-2 w-48 text-[10px] text-zinc-300 shadow-lg backdrop-blur z-50">
            Real-time system logs showing model calibration results and performance metrics
          </div>
        </div>
      </div>

      <div className="space-y-4 overflow-y-auto custom-scrollbar flex-1 pr-2">
        {logs.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-zinc-600">
            <Cpu size={32} className="mb-2 opacity-20" />
            <p className="text-xs font-mono italic">Waiting for calibration...</p>
          </div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="border-l-2 border-white/10 pl-4 py-1 animate-in slide-in-from-left duration-500">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2 group relative">
                  {log.trend === "OPTIMIZED" && <TrendingUp size={12} className="text-emerald-400" />}
                  {log.trend === "DEGRADED" && <TrendingDown size={12} className="text-red-400" />}
                  {log.trend === "STABLE" && <Minus size={12} className="text-zinc-500" />}
                  <span className={`text-sm font-bold font-mono cursor-help ${
                    log.trend === "OPTIMIZED" ? "text-emerald-400" : 
                    log.trend === "DEGRADED" ? "text-red-400" : "text-zinc-400"
                  }`}>
                    {log.trend} {log.diff}
                  </span>
                  <div className="hidden group-hover:block absolute left-0 top-full mt-1 bg-zinc-950 border border-cyan-500/50 rounded-lg p-2 w-40 text-[10px] text-zinc-300 shadow-lg backdrop-blur z-50">
                    {getTrendTooltip(log.trend)}
                  </div>
                </div>
                <span className="text-xs font-mono text-zinc-600">{log.timestamp}</span>
              </div>
              <p className="text-sm text-zinc-400 leading-relaxed font-mono">
                {log.message}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}