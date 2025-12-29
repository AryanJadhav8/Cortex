export default function DataTable({ rows }) {
  if (!rows || rows.length === 0) return null;
  const columns = Object.keys(rows[0]);

  return (
    <div className="bg-zinc-900/50 border border-white/10 rounded-[2rem] flex flex-col h-[550px] w-full overflow-hidden">
      
      {/* Header Branding Section */}
      <div className="p-5 border-b border-white/10 flex justify-between items-center bg-zinc-900/80 backdrop-blur-md z-30">
        <span className="text-zinc-500 text-[10px] font-mono uppercase tracking-[0.2em]">Live Data Preview</span>
        <div className="flex items-center gap-2">
           <div className="h-1.5 w-1.5 rounded-full bg-cyan-500 animate-pulse" />
           <span className="text-zinc-400 text-[10px] font-mono italic">Synchronized</span>
        </div>
      </div>
      
      {/* FIX: This container now handles all scrolling. 
         The scrollbar will now reach the top of the table content area.
      */}
      <div className="flex-1 overflow-auto custom-scrollbar relative">
        <table className="w-full border-collapse border-spacing-0">
          <thead>
            <tr className="sticky top-0 z-20 bg-zinc-950 shadow-[0_1px_0_rgba(255,255,255,0.1)]">
              {columns.map(col => (
                <th 
                  key={col} 
                  className="px-6 py-4 text-cyan-400 text-[10px] font-mono uppercase tracking-widest border-r border-white/10 last:border-r-0 text-center whitespace-nowrap bg-zinc-950"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="font-mono text-xs text-zinc-300">
            {rows.map((row, i) => (
              <tr key={i} className="border-b border-white/5 hover:bg-cyan-500/[0.03] transition-colors group">
                {columns.map(col => (
                  <td 
                    key={col} 
                    className="px-6 py-4 whitespace-nowrap border-r border-white/5 last:border-r-0 text-center"
                  >
                    <span className={typeof row[col] === 'number' ? 'text-cyan-400/90' : ''}>
                      {row[col]?.toString() || "—"}
                    </span>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}