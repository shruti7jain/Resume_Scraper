import { ChevronDown, ChevronUp } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function AnalysisResultsPanel({ results }) {
  const [isSuggestionsOpen, setIsSuggestionsOpen] = useState(false);
  const [score, setScore] = useState(0);

  // Animate score on mount
  useEffect(() => {
    if (results?.match_score) {
      setTimeout(() => setScore(results.match_score), 300);
    }
  }, [results]);

  if (!results) return null;

  const { missing_skills, experience_gaps, suggestions } = results;

  // Calculate SVG stroke offset for the score (Circumference of r=64 is ~402)
  const radius = 64;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col h-full gap-6">
      <div className="flex gap-6 items-center">
        {/* Left: Score */}
        <div className="flex flex-col items-center justify-center">
          <div className="score-gauge" style={{ width: '180px', height: '180px' }}>
            <svg className="score-gauge__svg" width="180" height="180" viewBox="0 0 180 180" style={{ filter: 'drop-shadow(0 0 10px rgba(0, 243, 255, 0.6))' }}>
              <circle className="score-gauge__track" cx="90" cy="90" r="76" strokeWidth="12" stroke="rgba(255,255,255,0.05)" />
              <circle 
                className="score-gauge__fill" 
                cx="90" 
                cy="90" 
                r="76" 
                strokeWidth="12"
                stroke="var(--neon-cyan)"
                strokeDasharray={477.5}
                strokeDashoffset={477.5 - (score / 100) * 477.5}
              />
            </svg>
            <div className="score-gauge__label" style={{ flexDirection: 'column' }}>
              <span className="text-4xl text-white font-bold">{score}%</span>
              <span className="text-xs text-muted font-normal uppercase tracking-wider mt-1">Match Score</span>
            </div>
          </div>
        </div>

        {/* Right: Missing Skills */}
        <div className="flex-1 flex flex-col justify-center">
          <h4 className="mb-4 text-white font-semibold">Missing Skills & Keywords</h4>
          <div className="flex flex-wrap gap-3">
            {missing_skills && missing_skills.length > 0 ? (
              missing_skills.map((skill, i) => (
                <span key={i} className={`badge ${i % 2 === 0 ? 'badge--accent' : 'badge--brand'}`}>{skill}</span>
              ))
            ) : (
              <span className="badge badge--success">Excellent! No missing skills.</span>
            )}
          </div>
        </div>
      </div>

      {/* Accordions */}
      <div className="flex flex-col gap-3 mt-4">
        {/* AI Suggestions Accordion */}
        <div className="card card--glass p-0 overflow-hidden">
          <button 
            className="flex items-center justify-between w-full p-4 hover:bg-white/5 transition-colors"
            onClick={() => setIsSuggestionsOpen(!isSuggestionsOpen)}
          >
            <h5 className="text-sm text-white font-semibold flex items-center gap-2">
              AI Suggestions <span className="badge badge--warning text-[10px] px-2 py-0">Actionable Insight</span>
            </h5>
            {isSuggestionsOpen ? <ChevronUp size={18} className="text-muted" /> : <ChevronDown size={18} className="text-muted" />}
          </button>
          
          {isSuggestionsOpen && (
            <div className="p-4 pt-0 border-t border-subtle bg-black/20 animate-fade-in">
              <ul className="flex-col gap-3 mt-4">
                {suggestions && suggestions.length > 0 ? suggestions.map((suggestion, i) => (
                  <li key={i} className="text-sm text-secondary flex gap-2">
                    <span className="text-warning">💡</span> {suggestion}
                  </li>
                )) : (
                  <li className="text-sm text-secondary">No suggestions. Your resume looks great!</li>
                )}
              </ul>
            </div>
          )}
        </div>

        {/* AI Insights Accordion (Placeholder for mockup) */}
        <div className="card card--glass p-0 overflow-hidden">
          <button className="flex items-center justify-between w-full p-4 hover:bg-white/5 transition-colors">
            <h5 className="text-sm text-white font-semibold">AI Insights</h5>
            <ChevronDown size={18} className="text-muted" />
          </button>
        </div>
      </div>
    </div>
  );
}
