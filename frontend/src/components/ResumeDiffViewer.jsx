import { useState } from 'react';

export default function ResumeDiffViewer({ tailoredData }) {
  if (!tailoredData) return null;

  const { original_resume, tailored_resume, changes } = tailoredData;

  // Helper to check if a specific text is in the changes as updated (Right column)
  const isTextUpdated = (text) => {
    if (!changes || !text) return false;
    return changes.some(c => 
      c.updated === text || 
      text.includes(c.updated) || 
      c.updated.includes(text)
    );
  };

  // Helper to check if a specific text is in the changes as original (Left column)
  const isTextOriginal = (text) => {
    if (!changes || !text) return false;
    return changes.some(c => 
      c.original === text || 
      text.includes(c.original) || 
      c.original.includes(text)
    );
  };

  return (
    <div className="card card--glass h-full flex flex-col p-6 animate-fade-in">
      <div className="flex justify-between items-center mb-6 border-b border-subtle pb-4">
        <h3 className="text-lg font-bold text-white">Resume Comparison</h3>
      </div>

      <div className="diff-viewer flex-1 overflow-hidden" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        
        {/* Original Resume (Full) */}
        <div className="diff-panel bg-input border-subtle overflow-y-auto p-4" style={{ borderRadius: '12px' }}>
          <div className="text-white font-bold mb-4 bg-overlay p-2 rounded text-center sticky top-0 z-10">
            Original Resume
          </div>
          <div className="flex flex-col gap-6">
            
            {/* Personal Info */}
            {(original_resume.name || original_resume.email || original_resume.phone) && (
              <div className="text-center pb-4 border-b border-subtle/50">
                <h4 className="text-white font-bold text-xl">{original_resume.name || "Name"}</h4>
                <div className="text-sm text-muted mt-1 flex justify-center gap-3 flex-wrap">
                  {original_resume.email && <span>{original_resume.email}</span>}
                  {original_resume.phone && <span>{original_resume.phone}</span>}
                  {original_resume.location && <span>{original_resume.location}</span>}
                  {original_resume.linkedin && <span>LinkedIn</span>}
                </div>
              </div>
            )}

            {/* Summary */}
            {original_resume.professional_summary && (
              <div>
                <h6 className="text-white font-bold text-sm mb-2 uppercase tracking-wider text-neon-cyan">Professional Summary</h6>
                <div className={`text-sm leading-relaxed p-2 rounded ${isTextOriginal(original_resume.professional_summary) ? 'bg-red-900/20 text-red-300 border border-red-900/50 line-through decoration-red-500/50' : 'text-secondary'}`}>
                  {original_resume.professional_summary}
                </div>
              </div>
            )}

            {/* Experience */}
            {original_resume.experience && original_resume.experience.length > 0 && (
              <div>
                <h6 className="text-white font-bold text-sm mb-3 uppercase tracking-wider text-neon-cyan">Experience</h6>
                <div className="flex flex-col gap-5">
                  {original_resume.experience.map((exp, i) => (
                    <div key={i} className="flex flex-col gap-1">
                      <div className="flex justify-between items-start">
                        <span className="text-white font-bold text-sm">{exp.role}</span>
                        <span className="text-muted text-xs">{exp.duration}</span>
                      </div>
                      <div className="text-muted text-xs mb-2">{exp.company}{exp.location ? `, ${exp.location}` : ''}</div>
                      <ul className="list-disc pl-4 flex flex-col gap-1.5">
                        {exp.bullets.map((bullet, j) => (
                          <li key={j} className={`text-sm ${isTextOriginal(bullet) ? 'bg-red-900/20 text-red-300 rounded px-1 line-through decoration-red-500/50' : 'text-secondary'}`}>
                            {bullet}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Projects */}
            {original_resume.projects && original_resume.projects.length > 0 && (
              <div>
                <h6 className="text-white font-bold text-sm mb-3 uppercase tracking-wider text-neon-cyan">Projects</h6>
                <div className="flex flex-col gap-5">
                  {original_resume.projects.map((proj, i) => (
                    <div key={i} className="flex flex-col gap-1">
                      <span className="text-white font-bold text-sm">{proj.name}</span>
                      <div className="text-sm text-secondary leading-relaxed">{proj.description}</div>
                      {proj.tech_stack && proj.tech_stack.length > 0 && (
                        <div className="text-xs text-muted mt-1">Tech: {proj.tech_stack.join(', ')}</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Skills */}
            {original_resume.skills && original_resume.skills.length > 0 && (
              <div>
                <h6 className="text-white font-bold text-sm mb-2 uppercase tracking-wider text-neon-cyan">Skills</h6>
                <div className="flex flex-wrap gap-2">
                  {original_resume.skills.map((skill, i) => (
                    <span key={i} className={`text-xs px-2 py-1 rounded ${isTextOriginal(skill) ? 'bg-red-900/30 text-red-300 border border-red-800 line-through decoration-red-500/50' : 'bg-overlay text-secondary'}`}>
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Education */}
            {original_resume.education && original_resume.education.length > 0 && (
              <div>
                <h6 className="text-white font-bold text-sm mb-3 uppercase tracking-wider text-neon-cyan">Education</h6>
                <div className="flex flex-col gap-3">
                  {original_resume.education.map((edu, i) => (
                    <div key={i} className="flex flex-col">
                      <div className="flex justify-between items-start">
                        <span className="text-white font-bold text-sm">{edu.degree}</span>
                        <span className="text-muted text-xs">{edu.year}</span>
                      </div>
                      <span className="text-secondary text-sm">{edu.institution}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Certifications */}
            {original_resume.certifications && original_resume.certifications.length > 0 && (
              <div>
                <h6 className="text-white font-bold text-sm mb-2 uppercase tracking-wider text-neon-cyan">Certifications</h6>
                <ul className="list-disc pl-4 flex flex-col gap-1">
                  {original_resume.certifications.map((cert, i) => (
                    <li key={i} className="text-sm text-secondary">{cert}</li>
                  ))}
                </ul>
              </div>
            )}

          </div>
        </div>

        {/* Tailored Resume (Full) */}
        <div className="diff-panel bg-input border-subtle overflow-y-auto p-4" style={{ borderRadius: '12px' }}>
          <div className="text-white font-bold mb-4 bg-overlay p-2 rounded text-center sticky top-0 z-10">
            Tailored Resume
          </div>
          <div className="flex flex-col gap-6">
            
            {/* Personal Info */}
            {(tailored_resume.name || tailored_resume.email || tailored_resume.phone) && (
              <div className="text-center pb-4 border-b border-subtle/50">
                <h4 className="text-white font-bold text-xl">{tailored_resume.name || "Name"}</h4>
                <div className="text-sm text-muted mt-1 flex justify-center gap-3 flex-wrap">
                  {tailored_resume.email && <span>{tailored_resume.email}</span>}
                  {tailored_resume.phone && <span>{tailored_resume.phone}</span>}
                  {tailored_resume.location && <span>{tailored_resume.location}</span>}
                  {tailored_resume.linkedin && <span>LinkedIn</span>}
                </div>
              </div>
            )}

            {/* Summary */}
            {tailored_resume.professional_summary && (
              <div>
                <h6 className="text-white font-bold text-sm mb-2 uppercase tracking-wider text-neon-cyan">Professional Summary</h6>
                <div className={`text-sm leading-relaxed p-2 rounded ${isTextUpdated(tailored_resume.professional_summary) ? 'bg-emerald-900/20 text-emerald-200 border border-emerald-900/50' : 'text-secondary'}`}>
                  {tailored_resume.professional_summary}
                </div>
              </div>
            )}

            {/* Experience */}
            {tailored_resume.experience && tailored_resume.experience.length > 0 && (
              <div>
                <h6 className="text-white font-bold text-sm mb-3 uppercase tracking-wider text-neon-cyan">Experience</h6>
                <div className="flex flex-col gap-5">
                  {tailored_resume.experience.map((exp, i) => (
                    <div key={i} className="flex flex-col gap-1">
                      <div className="flex justify-between items-start">
                        <span className="text-white font-bold text-sm">{exp.role}</span>
                        <span className="text-muted text-xs">{exp.duration}</span>
                      </div>
                      <div className="text-muted text-xs mb-2">{exp.company}{exp.location ? `, ${exp.location}` : ''}</div>
                      <ul className="list-disc pl-4 flex flex-col gap-1.5">
                        {exp.bullets.map((bullet, j) => (
                          <li key={j} className={`text-sm ${isTextUpdated(bullet) ? 'bg-emerald-900/20 text-emerald-300 rounded px-1' : 'text-secondary'}`}>
                            {bullet}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Projects */}
            {tailored_resume.projects && tailored_resume.projects.length > 0 && (
              <div>
                <h6 className="text-white font-bold text-sm mb-3 uppercase tracking-wider text-neon-cyan">Projects</h6>
                <div className="flex flex-col gap-5">
                  {tailored_resume.projects.map((proj, i) => (
                    <div key={i} className="flex flex-col gap-1">
                      <span className="text-white font-bold text-sm">{proj.name}</span>
                      <div className="text-sm text-secondary leading-relaxed">{proj.description}</div>
                      {proj.tech_stack && proj.tech_stack.length > 0 && (
                        <div className="text-xs text-muted mt-1">Tech: {proj.tech_stack.join(', ')}</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Skills */}
            {tailored_resume.skills && tailored_resume.skills.length > 0 && (
              <div>
                <h6 className="text-white font-bold text-sm mb-2 uppercase tracking-wider text-neon-cyan">Skills</h6>
                <div className="flex flex-wrap gap-2">
                  {tailored_resume.skills.map((skill, i) => (
                    <span key={i} className={`text-xs px-2 py-1 rounded ${isTextUpdated(skill) ? 'bg-emerald-900/30 text-emerald-300 border border-emerald-800' : 'bg-overlay text-secondary'}`}>
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Education */}
            {tailored_resume.education && tailored_resume.education.length > 0 && (
              <div>
                <h6 className="text-white font-bold text-sm mb-3 uppercase tracking-wider text-neon-cyan">Education</h6>
                <div className="flex flex-col gap-3">
                  {tailored_resume.education.map((edu, i) => (
                    <div key={i} className="flex flex-col">
                      <div className="flex justify-between items-start">
                        <span className="text-white font-bold text-sm">{edu.degree}</span>
                        <span className="text-muted text-xs">{edu.year}</span>
                      </div>
                      <span className="text-secondary text-sm">{edu.institution}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Certifications */}
            {tailored_resume.certifications && tailored_resume.certifications.length > 0 && (
              <div>
                <h6 className="text-white font-bold text-sm mb-2 uppercase tracking-wider text-neon-cyan">Certifications</h6>
                <ul className="list-disc pl-4 flex flex-col gap-1">
                  {tailored_resume.certifications.map((cert, i) => (
                    <li key={i} className="text-sm text-secondary">{cert}</li>
                  ))}
                </ul>
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}
