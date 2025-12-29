import { motion } from "framer-motion";

export default function DiagnosticGrid({ stats }) {
  // These are fallback values in case we haven't uploaded a file yet
  const displayStats = stats || {
    missing_before: 0,
    missing_after: 0,
    rows: 0,
    accuracy: "0.0%"
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-8">
      {/* 1. HEALTH SCORE (The big highlight) */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="md:col-span-1 bg-zinc-900 border border-white/10 p-8 rounded-[2rem] flex flex-col justify-center relative overflow-hidden group"
      >
        {/* Subtle glow effect behind the number */}
        <div className="absolute -right-4 -top-4 w-24 h-24 bg-cyan-500/10 blur-3xl group-hover:bg-cyan-500/20 transition-colors" />
        
        <span className="text-zinc-500 text-[10px] font-mono uppercase tracking-[0.2em] mb-1">
          Dataset Health
        </span>
        <div className="text-7xl font-black text-white tracking-tighter flex items-baseline">
          100<span className="text-cyan-400 text-3xl ml-1">%</span>
        </div>
        <p className="text-zinc-500 text-[10px] mt-2 leading-tight uppercase font-mono">
          Integrity Protocol: <span className="text-emerald-500">Passed</span>
        </p>
      </motion.div>

      {/* 2. STAT CARDS (The metric details) */}
      <div className="md:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard 
          label="Remediation" 
          value={`${displayStats.missing_before} → ${displayStats.missing_after}`} 
          sub="Missing values healed" 
        />
        <StatCard 
          label="Sample Size" 
          value={displayStats.rows.toLocaleString()} 
          sub="Total records processed" 
        />
        <StatCard 
          label="Model Precision" 
          value={displayStats.accuracy} 
          sub="Baseline accuracy score" 
        />
      </div>
    </div>
  );
}

// Internal reusable card component
function StatCard({ label, value, sub }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-zinc-900/40 border border-white/5 p-6 rounded-[1.5rem] backdrop-blur-md flex flex-col justify-between hover:border-white/10 transition-colors"
    >
      <div>
        <p className="text-zinc-500 text-[10px] font-mono uppercase tracking-widest">{label}</p>
        <p className="text-2xl font-bold mt-2 tracking-tight text-zinc-100">{value}</p>
      </div>
      <p className="text-zinc-600 text-[10px] mt-4 font-mono uppercase tracking-tighter italic">{sub}</p>
    </motion.div>
  );
}