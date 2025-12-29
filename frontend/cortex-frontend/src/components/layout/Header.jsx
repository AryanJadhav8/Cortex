import { Activity } from "lucide-react";

export default function Header() {
  return (
    <header className="flex justify-between items-center py-10">
      <div className="flex flex-col">
        <div className="flex items-center gap-2 mb-1">
          <Activity className="size-4 text-cyan-400 animate-pulse" />
          <span className="text-[10px] font-mono tracking-[0.3em] text-cyan-400/80 uppercase">
            System Monitoring Active
          </span>
        </div>
        <h1 className="text-4xl font-black tracking-tighter text-white">
          CORTEX<span className="text-cyan-500">.</span>
        </h1>
      </div>
      
      <div className="text-right">
        <p className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">Protocol</p>
        <p className="text-sm font-bold text-zinc-300 italic">HEALTH_SCAN_v1.0</p>
      </div>
    </header>
  );
}