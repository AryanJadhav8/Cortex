"use client"
import * as React from "react"
import { CheckIcon, ChevronsUpDownIcon, Fingerprint, Search, X } from "lucide-react"
import { cn } from "../../lib/utils" 

export default function ColumnSelector({ diagnostics, selectedColumns, onSelectionChange }) {
  const [open, setOpen] = React.useState(false);
  const [search, setSearch] = React.useState("");

  // This ensures the list ONLY changes if you type in the search box
  const displayList = React.useMemo(() => {
    if (!diagnostics) return [];
    return diagnostics.filter(col => 
      col.label.toLowerCase().includes(search.toLowerCase())
    );
  }, [diagnostics, search]);

  return (
    <div className="relative w-full">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between bg-zinc-900/50 border border-white/10 text-zinc-300 rounded-2xl h-14 px-4 shadow-lg group"
      >
        <div className="flex flex-col items-start text-left">
          <span className="text-[10px] text-zinc-500 font-mono uppercase tracking-widest">Model Features</span>
          <span className="text-sm font-bold text-white">
              {selectedColumns.length} Active Vectors
          </span>
        </div>
        <ChevronsUpDownIcon className="h-4 w-4 opacity-50" />
      </button>

      {open && (
        <div className="absolute top-full left-0 z-[999] w-[400px] mt-3 bg-zinc-950 border border-white/10 shadow-2xl rounded-2xl overflow-hidden backdrop-blur-xl">
          <div className="p-2 border-b border-white/5 flex items-center gap-2 px-4">
            <Search size={14} className="text-zinc-500" />
            <input 
              className="bg-transparent border-none outline-none text-sm py-3 w-full text-white"
              placeholder="Filter columns..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          
          <div className="max-h-[350px] overflow-y-auto p-1 custom-scrollbar">
            {displayList.map((col) => {
              const isActive = selectedColumns.includes(col.value);
              return (
                <div
                  key={col.value}
                  onClick={(e) => {
                    e.stopPropagation(); // Stop menu from closing
                    onSelectionChange(col.value);
                  }}
                  className="flex items-center justify-between p-3 cursor-pointer hover:bg-white/10 rounded-xl transition-all m-1 group"
                >
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "flex items-center justify-center w-5 h-5 rounded-md border border-white/20 transition-all",
                      isActive ? "bg-cyan-500 border-cyan-500" : "bg-transparent"
                    )}>
                      {isActive && <CheckIcon className="h-3.5 w-3.5 text-black font-black" />}
                    </div>
                    <div className="flex flex-col">
                      <span className="text-sm font-bold text-zinc-100">{col.label}</span>
                      <span className="text-[10px] text-zinc-500 font-mono uppercase">
                        {col.type} • {col.cardinality} Uniques
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={cn(
                      "text-[10px] font-bold px-2 py-0.5 rounded-md border",
                      col.missing_pct > 30 ? "text-red-400 bg-red-950/40" : "text-emerald-400 bg-emerald-950/40"
                    )}>
                      {col.missing_pct}% NULL
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}