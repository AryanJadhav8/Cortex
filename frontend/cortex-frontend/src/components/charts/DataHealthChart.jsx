import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function DataHealthChart({ data }) {
  // We look for 'health_data' from the backend payload
  const rawData = data?.health_data || {};
  
  // Transform the { "Col": 5 } object into the Array Recharts needs
  const chartData = Object.entries(rawData)
    .map(([name, value]) => ({
      // Shorten long column names so they don't overlap
      name: name.length > 10 ? name.substring(0, 8) + '..' : name,
      fullName: name,
      value: value
    }))
    .sort((a, b) => b.value - a.value);

  // If no data, show the empty state
  if (chartData.length === 0) {
    return (
      <div className="bg-zinc-900/50 border border-white/5 p-8 rounded-[2rem] h-[450px] flex flex-col items-center justify-center text-center">
        <p className="text-zinc-500 font-mono text-[10px] uppercase tracking-widest">No Anomalies Detected</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900/50 border border-white/5 p-8 rounded-[2rem] h-[450px] flex flex-col">
      <div className="mb-8">
        <p className="text-zinc-500 text-[10px] font-mono uppercase tracking-[0.2em]">Integrity Module</p>
        <h3 className="text-xl font-bold text-white tracking-tight">Anomalies <span className="text-cyan-500">Healed</span></h3>
      </div>

      <div className="flex-1 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: -20, right: 20 }}>
            <XAxis type="number" hide />
            <YAxis 
              dataKey="name" 
              type="category" 
              tick={{ fill: '#71717a', fontSize: 10, fontFamily: 'monospace' }}
              width={80}
            />
            <Tooltip 
              cursor={{ fill: 'rgba(34, 211, 238, 0.05)' }}
              contentStyle={{ 
                backgroundColor: '#09090b', 
                border: '1px solid rgba(255,255,255,0.1)', 
                borderRadius: '12px',
                fontSize: '12px',
                fontFamily: 'monospace'
              }}
              itemStyle={{ color: '#22d3ee' }}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={18}>
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={index === 0 ? '#22d3ee' : '#0891b2'} 
                  fillOpacity={0.8}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}