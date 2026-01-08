import React, { useState } from 'react';
import {
  Trophy, Activity, Trees, Cpu, Target, Network,
  Info
} from 'lucide-react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, ResponsiveContainer, Tooltip } from 'recharts';
import { cn } from '../../lib/utils';

// Mapping string names from Python to Lucide components
const iconMap = {
  Activity: Activity,
  Trees: Trees,
  Cpu: Cpu,
  Target: Target,
  Network: Network
};

// Custom Tooltip for Radar Chart
const CustomRadarTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-zinc-950 border border-cyan-500/50 rounded-lg p-3 shadow-lg backdrop-blur">
        <p className="text-cyan-400 font-bold text-sm">{data.name}</p>
        <p className="text-white font-black text-lg">{data.accuracy.toFixed(1)}%</p>
      </div>
    );
  }
  return null;
};

export default function NeuralArena({ data }) {
  const [expandedModel, setExpandedModel] = useState(null);

  if (!data || !data.arena_results) {
    return null;
  }

  const results = Object.entries(data.arena_results);
  const champion = data.champion;

  // Prepare data for radar chart
  const radarData = results.map(([modelName, stats]) => ({
    name: modelName,
    accuracy: parseFloat((stats.accuracy * 100).toFixed(1)),
    fullMark: 100
  }));

  const containerColors = {
    emerald: 'bg-emerald-950/30 border-emerald-500/30',
    green: 'bg-green-950/30 border-green-500/30',
    amber: 'bg-amber-950/30 border-amber-500/30',
    orange: 'bg-orange-950/30 border-orange-500/30',
    cyan: 'bg-cyan-950/30 border-cyan-500/30'
  };

  const accentColors = {
    emerald: 'text-emerald-400',
    green: 'text-green-400',
    amber: 'text-amber-400',
    orange: 'text-orange-400',
    cyan: 'text-cyan-400'
  };

  const barColors = {
    emerald: 'bg-emerald-500',
    green: 'bg-green-500',
    amber: 'bg-amber-500',
    orange: 'bg-orange-500',
    cyan: 'bg-cyan-500'
  };

  return (
    <div className="space-y-4 w-full text-left">
      {/* Champion Banner */}
      <div className="bg-gradient-to-r from-cyan-900/30 to-purple-900/30 border border-cyan-500/50 rounded-2xl p-4 backdrop-blur">
        <div className="flex items-center gap-3 mb-2">
          <Trophy className="text-cyan-400" size={20} />
          <h3 className="text-sm font-black uppercase tracking-widest text-cyan-400">Arena Champion</h3>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <div className="text-lg font-bold text-white leading-tight">{champion.name}</div>
            <div className="text-[10px] text-zinc-400 uppercase tracking-wider">{champion.title}</div>
          </div>
          <div className="text-2xl font-black text-cyan-400 px-2">
            {champion.accuracy}
          </div>
        </div>
      </div>

      {/* Radar Chart */}
      <div className="bg-zinc-900/40 border border-white/5 rounded-2xl p-4">
        <p className="text-zinc-500 uppercase tracking-[0.2em] font-bold text-[10px] mb-4">Performance Overview</p>
        <div className="flex justify-center items-center w-full" style={{ height: '300px', minHeight: '300px' }}>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
              <PolarGrid stroke="#27272a" strokeDasharray="3 3" />
              <PolarAngleAxis
                dataKey="name"
                stroke="#a1a1aa"
                tick={{ fill: '#a1a1aa', fontSize: 11 }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                stroke="#52525b"
                tick={{ fill: '#71717a', fontSize: 10 }}
              />
              <Radar
                name="Accuracy %"
                dataKey="accuracy"
                stroke="#06b6d4"
                fill="#06b6d4"
                fillOpacity={0.3}
                dot={{ fill: '#06b6d4', r: 4 }}
                activeDot={{ r: 6, fill: '#06b6d4' }}
              />
              <Tooltip content={<CustomRadarTooltip />} />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                labelStyle={{ color: '#a1a1aa', fontSize: 12 }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Competitors Leaderboard */}
      <div className="space-y-2">
        {results.map(([modelName, stats]) => {
          const color = stats.color || 'cyan';
          const isExpanded = expandedModel === modelName;
          const accuracyPercent = (stats.accuracy * 100);
          const IconComponent = iconMap[stats.icon] || Info;

          return (
            <div key={modelName} className="space-y-2">
              <button
                onClick={() => setExpandedModel(isExpanded ? null : modelName)}
                className={cn(
                  'w-full p-3 rounded-xl border transition-all text-left block',
                  isExpanded
                    ? `${containerColors[color]} border-2`
                    : 'bg-zinc-900/40 border-white/10 hover:border-white/20'
                )}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={accentColors[color]}>
                      <IconComponent size={18} />
                    </span>
                    <div>
                      <div className="font-bold text-sm text-white leading-none mb-1">{modelName}</div>
                      <div className={cn('text-[10px] uppercase tracking-widest font-medium', accentColors[color])}>
                        {stats.title}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={cn('font-black text-lg leading-none', accentColors[color])}>
                      {stats.accuracy_pct}
                    </div>
                    <div className="text-[9px] text-zinc-500 mt-1">±{(stats.std_dev * 100).toFixed(1)}%</div>
                  </div>
                </div>

                <div className="bg-black/30 rounded-full h-2 overflow-hidden w-full">
                  <div
                    className={cn('h-full transition-all duration-500', barColors[color])}
                    style={{ width: `${accuracyPercent}%` }}
                  />
                </div>
              </button>

              {isExpanded && (
                <div className={cn(
                  'p-3 rounded-xl border text-sm space-y-3 animate-in fade-in slide-in-from-top-1 duration-200',
                  containerColors[color]
                )}>
                  <div>
                    <p className="text-[10px] uppercase tracking-widest text-zinc-400 mb-1 font-bold">Description</p>
                    <p className="text-zinc-300 text-xs leading-relaxed">{stats.description}</p>
                  </div>

                  {stats.cv_scores && stats.cv_scores.length > 0 && (
                    <div>
                      <p className="text-[10px] uppercase tracking-widest text-zinc-400 mb-2 font-bold">
                        5-Fold Cross-Validation Scores
                      </p>
                      <div className="grid grid-cols-5 gap-2">
                        {stats.cv_scores.map((score, i) => (
                          <div key={i} className="bg-black/30 rounded-lg p-2 text-center border border-white/10">
                            <div className={cn('font-bold text-[10px]', accentColors[color])}>
                              {(score * 100).toFixed(1)}%
                            </div>
                            <div className="text-[8px] text-zinc-500 uppercase mt-0.5">Fold {i + 1}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex gap-2 pt-2 border-t border-white/10">
                    <div className="flex-1">
                      <p className="text-[10px] uppercase tracking-widest text-zinc-400 mb-1 font-bold">Mean Accuracy</p>
                      <p className={cn('font-black text-sm', accentColors[color])}>
                        {stats.accuracy_pct}
                      </p>
                    </div>
                    <div className="flex-1 border-l border-white/10 pl-3">
                      <p className="text-[10px] uppercase tracking-widest text-zinc-400 mb-1 font-bold">Std Deviation</p>
                      <p className="font-bold text-sm text-zinc-300">±{(stats.std_dev * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Legend with Info Icons */}
      <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
        <p className="text-zinc-500 uppercase tracking-[0.2em] font-bold text-[9px] mb-3">Arena Methodology</p>
        <div className="space-y-3 text-zinc-400 text-[11px] leading-relaxed">
          <div className="flex gap-3">
            <Info size={14} className="text-cyan-500 shrink-0 mt-0.5" />
            <p><span className="font-bold text-zinc-200">Stratified 5-Fold Cross-Validation:</span> Dataset split into 5 balanced segments to ensure performance stability.</p>
          </div>
          <div className="flex gap-3">
            <Info size={14} className="text-cyan-500 shrink-0 mt-0.5" />
            <p><span className="font-bold text-zinc-200">5 Competitors:</span> Each architecture undergoes rigorous parallel testing cycles.</p>
          </div>
          <div className="flex gap-3">
            <Info size={14} className="text-cyan-500 shrink-0 mt-0.5" />
            <p><span className="font-bold text-zinc-200">Champion:</span> Architecture with highest mean accuracy across all validation folds is crowned.</p>
          </div>
        </div>
      </div>
    </div>
  );
}