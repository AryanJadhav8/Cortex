import React, { useState } from 'react';
import { UploadCloud, Loader2 } from 'lucide-react';
import axios from 'axios';

export default function FileUploader({ onUploadSuccess }) {
  const [loading, setLoading] = useState(false);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Connecting to your FastAPI endpoint we built earlier
      const response = await axios.post('http://localhost:8000/heal', formData);
      
      // Send the real data back to App.jsx
      onUploadSuccess(response.data);
    } catch (error) {
      console.error("Connection to AI Engine failed:", error);
      alert("Backend not found. Make sure your Python server is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-8">
      <label className="relative group cursor-pointer">
        <input 
          type="file" 
          className="hidden" 
          accept=".csv" 
          onChange={handleFileChange} 
          disabled={loading}
        />
        <div className="border-2 border-dashed border-zinc-800 rounded-3xl p-12 flex flex-col items-center justify-center bg-zinc-900/20 backdrop-blur-sm group-hover:border-cyan-500/50 transition-all">
          {loading ? (
            <>
              <Loader2 className="w-10 h-10 text-cyan-400 animate-spin mb-4" />
              <p className="text-cyan-400 font-mono text-sm animate-pulse">ANALYZING DATASET STRUCTURE...</p>
            </>
          ) : (
            <>
              <UploadCloud className="w-10 h-10 text-zinc-600 group-hover:text-cyan-400 transition-colors mb-4" />
              <p className="text-zinc-400 font-medium">Drop CSV to initiate diagnostic</p>
              <span className="text-zinc-600 text-[10px] mt-2 font-mono uppercase tracking-widest text-center">
                Secure local processing active
              </span>
            </>
          )}
        </div>
      </label>
    </div>
  );
}