import React from 'react';
import { HelpCircle } from 'lucide-react';

export default function FeatureImportance({ data, isOpen, onToggle }) {
  if (!data) return null;

  // Sort importance from highest to lowest
  const sortedData = Object.entries(data)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5); // Show top 5

  return (
    <div className="bg-zinc-900/40 border border-white/5 rounded-[2rem] p-6 backdrop-blur-md">
      <div className="flex items-center gap-2 mb-6 border-b border-white/5 pb-4">
        <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse" />
        <h3 className="text-[10px] font-mono uppercase tracking-[0.2em] text-zinc-400">Signal Strength (Weights)</h3>
        <div className="group relative ml-auto">
          <HelpCircle size={14} className="text-zinc-600 hover:text-cyan-400 cursor-help transition-colors" />
          <div className="absolute right-0 hidden group-hover:block bg-zinc-950 border border-cyan-500/50 rounded-lg p-2 w-48 text-[10px] text-zinc-300 shadow-lg backdrop-blur z-50">
            Feature importance scores showing which columns have the most influence on model predictions
          </div>
        </div>
      </div>

      <div className="space-y-5">
        {sortedData.map(([label, value]) => (
          <div key={label} className="space-y-2 group relative">
            <div className="flex justify-between items-center text-[10px] font-mono uppercase">
              <span className="text-zinc-300 font-bold cursor-help">{label}</span>
              <span className="text-cyan-500">{(value * 100).toFixed(1)}%</span>
            </div>
            <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-cyan-600 to-blue-400 rounded-full transition-all duration-1000"
                style={{ width: `${value * 100}%` }}
              />
            </div>
            <div className="hidden group-hover:block absolute left-0 top-full mt-1 bg-zinc-950 border border-cyan-500/50 rounded-lg p-2 w-40 text-[10px] text-zinc-300 shadow-lg backdrop-blur z-50">
              {label} has {(value * 100).toFixed(1)}% influence on predictions
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}