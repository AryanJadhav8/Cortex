"use client"
import * as React from "react"
import { CheckIcon, ChevronsUpDownIcon, Target } from "lucide-react"
import { cn } from "../../lib/utils" 

export default function TargetSelector({ diagnostics, selectedTarget, onTargetChange, isOpen, onToggle }) {
  return (
    <div className="relative w-full">
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          onToggle();
        }}
        className="w-full flex items-center justify-between bg-zinc-900/50 border border-white/10 text-zinc-300 rounded-2xl h-14 px-4 shadow-lg group"
      >
        <div className="flex flex-col items-start text-left">
          <span className="text-[10px] text-zinc-500 font-mono uppercase tracking-widest">Prediction Target</span>
          <span className="text-sm font-bold text-cyan-400">
            {selectedTarget || "Select Target Column"}
          </span>
        </div>
        <ChevronsUpDownIcon className="h-4 w-4 opacity-50" />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 z-[999] w-[400px] mt-3 bg-zinc-950 border border-white/10 shadow-2xl rounded-2xl overflow-hidden backdrop-blur-xl">
          <div className="max-h-[350px] overflow-y-auto p-1 custom-scrollbar">
            {diagnostics.map((col) => {
              const isSelected = selectedTarget === col.value;
              return (
                <div
                  key={col.value}
                  onClick={(e) => {
                    e.stopPropagation();
                    onTargetChange(col.value);
                  }}
                  className="flex items-center justify-between p-3 cursor-pointer hover:bg-white/10 rounded-xl transition-all m-1 group"
                >
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "flex items-center justify-center w-5 h-5 rounded-md border transition-all",
                      isSelected 
                        ? "bg-cyan-500 border-cyan-500" 
                        : "bg-transparent border-white/20"
                    )}>
                      {isSelected && <CheckIcon className="h-3.5 w-3.5 text-black font-black" />}
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