import React from 'react';
import { Terminal, Cpu, TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function CortexInsights({ logs }) {
  return (
    <div className="bg-zinc-900/40 border border-white/5 rounded-[2rem] p-6 backdrop-blur-md overflow-hidden flex flex-col h-[300px]">
      <div className="flex items-center gap-2 mb-4 border-b border-white/5 pb-4">
        <Terminal size={16} className="text-cyan-500" />
        <h3 className="text-[10px] font-mono uppercase tracking-[0.2em] text-zinc-400">Intelligence Log</h3>
      </div>

      <div className="space-y-4 overflow-y-auto custom-scrollbar flex-1 pr-2">
        {logs.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-zinc-600">
            <Cpu size={32} className="mb-2 opacity-20" />
            <p className="text-[10px] font-mono italic">Waiting for calibration...</p>
          </div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="border-l-2 border-white/10 pl-4 py-1 animate-in slide-in-from-left duration-500">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  {log.trend === "OPTIMIZED" && <TrendingUp size={12} className="text-emerald-400" />}
                  {log.trend === "DEGRADED" && <TrendingDown size={12} className="text-red-400" />}
                  {log.trend === "STABLE" && <Minus size={12} className="text-zinc-500" />}
                  <span className={`text-[10px] font-bold font-mono ${
                    log.trend === "OPTIMIZED" ? "text-emerald-400" : 
                    log.trend === "DEGRADED" ? "text-red-400" : "text-zinc-400"
                  }`}>
                    {log.trend} {log.diff}
                  </span>
                </div>
                <span className="text-[12px] font-mono text-zinc-600">{log.timestamp}</span>
              </div>
              <p className="text-[0.85rem] text-zinc-400 leading-relaxed font-mono">
                {log.message}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}