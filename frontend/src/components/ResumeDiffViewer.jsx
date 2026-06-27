import { useState } from 'react';

export default function ResumeDiffViewer({ tailoredData }) {
  const [viewMode, setViewMode] = useState('full'); // 'full' or 'changes'

  if (!tailoredData) return null;

  const { original_resume, tailored_resume, changes } = tailoredData;

  const hasChanged = (text) => {
    return changes?.some(c => c.updated.includes(text) || c.original.includes(text));
  };

  const renderSection = (title, originalContent, tailoredContent) => {
    return (
      <div className="mb-6">
        <h5 className="text-sm uppercase text-muted mb-2">{title}</h5>
        <div className="diff-viewer">
          {/* Original */}
          <div className="diff-panel diff-panel--original">
            <div className="diff-panel__header">Original</div>
            <div className={`diff-line ${hasChanged(originalContent) ? 'diff-line--removed' : ''}`}>
              {originalContent}
            </div>
          </div>
          {/* Tailored */}
          <div className="diff-panel diff-panel--tailored">
            <div className="diff-panel__header">Tailored</div>
            <div className={`diff-line ${hasChanged(tailoredContent) ? 'diff-line--added' : ''}`}>
              {tailoredContent}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="card card--glass h-full flex flex-col p-6 animate-fade-in">
      <div className="flex justify-between items-center mb-6 border-b border-subtle pb-4">
        <h3 className="text-lg font-bold text-white">Resume Diff Viewer: Original vs. Tailored</h3>
        <div className="flex items-center gap-3">
          <span className="text-sm text-secondary">View Changes Only</span>
          <div 
            className="w-12 h-6 rounded-full bg-overlay border border-subtle relative cursor-pointer"
            onClick={() => setViewMode(viewMode === 'full' ? 'changes' : 'full')}
          >
            <div className={`absolute top-1 left-1 w-4 h-4 rounded-full transition-transform ${viewMode === 'changes' ? 'translate-x-6 bg-neon-cyan' : 'bg-muted'}`}></div>
          </div>
        </div>
      </div>

      <div className="diff-viewer flex-1 overflow-hidden" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {/* Original */}
        <div className="diff-panel bg-input border-subtle overflow-y-auto" style={{ borderRadius: '12px' }}>
          <div className="text-white font-bold mb-4 bg-overlay p-2 rounded text-center">Original</div>
          <div className="flex flex-col gap-4">
            <div>
              <h6 className="text-white font-bold text-sm mb-1">Experience</h6>
              <div className="text-sm text-secondary leading-relaxed">
                Led a team of 5 developers, <span className="bg-orange-900/40 text-orange-200 rounded px-1">team of 5 developers</span>, achieving a 20% increase in efficiency using Agile methodologies, to manage select net-swrator atandance, and entinization domamic scontest and programming, sustononacles and data.
              </div>
            </div>
            <div>
              <h6 className="text-white font-bold text-sm mb-1">Education</h6>
              <div className="text-sm text-secondary leading-relaxed">
                Professional University Technology at University, Bentaowons, 2012
              </div>
            </div>
            <div>
              <h6 className="text-white font-bold text-sm mb-1">Skills</h6>
              <div className="text-sm text-secondary leading-relaxed">
                Professional UIA, Mamitowring, Traming, Eoaehing, Fomsaerviov, Data Visualization
              </div>
            </div>
          </div>
        </div>

        {/* Tailored */}
        <div className="diff-panel bg-input border-subtle overflow-y-auto" style={{ borderRadius: '12px' }}>
          <div className="text-white font-bold mb-4 bg-overlay p-2 rounded text-center">Tailored</div>
          <div className="flex flex-col gap-4">
            <div>
              <h6 className="text-white font-bold text-sm mb-1">Experience</h6>
              <div className="text-sm text-secondary leading-relaxed">
                <span className="bg-emerald-900/40 text-emerald-300 rounded px-1">Spearheaded a high-performing team of 5 developers</span>, achieving a <span className="bg-emerald-900/40 text-emerald-300 rounded px-1">20% increase in efficiency</span> using Agile methodologies, to manage select net-swrator atandance, and entinization domamic scontest and programming, sustononacles and data.
              </div>
            </div>
            <div>
              <h6 className="text-white font-bold text-sm mb-1">Education</h6>
              <div className="text-sm text-secondary leading-relaxed">
                Professional University Technology at University, Bentaowns, 2012
              </div>
            </div>
            <div>
              <h6 className="text-white font-bold text-sm mb-1">Skills</h6>
              <div className="text-sm text-secondary leading-relaxed text-muted">
                Professional UIA, Mxnmitowing, Tumming, Exowkling, Ternssomlow, <span className="text-secondary">Data Visualization</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
