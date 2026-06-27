import { useState } from 'react';
import axios from 'axios';
import { Sparkles, Activity } from 'lucide-react';
import ResumeUploader from '../components/ResumeUploader';
import JDInputPanel from '../components/JDInputPanel';
import AnalysisResultsPanel from '../components/AnalysisResultsPanel';
import ResumeDiffViewer from '../components/ResumeDiffViewer';
import DownloadButton from '../components/DownloadButton';

export default function Home() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jdText, setJdText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  // State for data from backend
  const [analysisResults, setAnalysisResults] = useState(null);
  const [tailoredData, setTailoredData] = useState(null);

  const handleAnalyze = async () => {
    if (!resumeFile || !jdText) {
      alert("Please upload a resume and paste a job description first.");
      return;
    }

    setIsProcessing(true);
    try {
      // 1. Upload Resume
      const formData = new FormData();
      formData.append('file', resumeFile);
      
      const uploadRes = await axios.post(`${API_URL}/api/upload-resume`, formData);
      const parsedResume = uploadRes.data;

      // 2. Parse JD
      const jdRes = await axios.post(`${API_URL}/api/parse-jd`, { text: jdText });
      const parsedJd = jdRes.data;

      // 3. Analyze match
      const analyzeRes = await axios.post(`${API_URL}/api/analyze`, {
        resume: parsedResume,
        job_description: parsedJd
      });
      const analysisReport = analyzeRes.data;

      // 4. Optimize Resume
      const optimizeRes = await axios.post(`${API_URL}/api/optimize`, {
        resume: parsedResume,
        job_description: parsedJd,
        analysis: analysisReport
      });
      
      const tailoredResume = optimizeRes.data;
      
      setAnalysisResults({
        match_score: tailoredResume.match_score || analysisReport.match_score,
        missing_skills: tailoredResume.missing_skills || analysisReport.missing_skills || [],
        experience_gaps: tailoredResume.experience_gaps || analysisReport.experience_gaps || [],
        suggestions: tailoredResume.suggestions || analysisReport.suggestions || []
      });

      setTailoredData({
        match_score: tailoredResume.match_score || analysisReport.match_score,
        original_resume: tailoredResume.original_resume || parsedResume,
        tailored_resume: tailoredResume.tailored_resume,
        missing_skills: tailoredResume.missing_skills || analysisReport.missing_skills || [],
        experience_gaps: tailoredResume.experience_gaps || analysisReport.experience_gaps || [],
        suggestions: tailoredResume.suggestions || analysisReport.suggestions || [],
        changes: tailoredResume.changes || []
      });

    } catch (err) {
      console.error("Error during analysis: ", err);
      alert("Analysis failed! Check the console or backend terminal for more details. (Make sure your Groq API key is set in .env)");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="container py-8">
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-brand">
          <span className="text-neon-cyan">Resume</span> Shapeshifter <span className="text-neon-purple text-sm ml-2">AI Dashboard</span>
        </div>
        <div className="navbar-links">
          <button className="btn btn--secondary btn--sm">Dashboard</button>
          <button className="btn btn--ghost btn--sm">My Resumes</button>
          <button className="btn btn--ghost btn--sm">Job Tracker</button>
          <div className="user-profile-pill">
            <Activity size={14} className="text-muted" />
            Alex Chen
            <div className="status-dot"></div>
          </div>
        </div>
      </nav>

      {/* Row 1: Uploader and JD Input */}
      <div className="grid-2 mb-8">
        <ResumeUploader onFileSelect={setResumeFile} />
        <JDInputPanel jdText={jdText} setJdText={setJdText} />
      </div>

      {/* Row 2: Giant Analyze Button */}
      <div className="flex justify-center mb-12">
        <button 
          className="btn--neon"
          onClick={handleAnalyze}
          disabled={isProcessing || (!resumeFile && !jdText)}
        >
          {isProcessing ? (
            <div className="flex items-center gap-4">
              <div className="spinner" style={{ width: '28px', height: '28px', borderWidth: '4px', borderTopColor: '#fff', borderColor: 'rgba(255,255,255,0.3)' }}></div> 
              PROCESSING...
            </div>
          ) : (
            <div className="flex items-center gap-4">
              <Sparkles size={28} /> ANALYZE & TAILOR RESUME
            </div>
          )}
        </button>
      </div>

      {/* Row 3: Results and Diff */}
      <div className="grid grid-cols-1 lg:grid-cols-[40%_60%] gap-6 mb-12">
        <div className="flex-col gap-6">
          {!analysisResults && !isProcessing ? (
            <div className="card h-full flex flex-col items-center justify-center text-center p-12 border-dashed border-2 border-subtle">
              <Activity size={48} className="text-muted mb-4 opacity-50" />
              <h3 className="text-muted mb-2">Awaiting Analysis</h3>
              <p className="text-sm text-muted">Upload a resume and job description to see your match score and tailored improvements here.</p>
            </div>
          ) : isProcessing ? (
            <div className="card h-full flex flex-col items-center justify-center p-12">
              <div className="spinner mb-6" style={{ width: 48, height: 48, borderWidth: 4, borderColor: 'rgba(0,243,255,0.3)', borderTopColor: 'var(--neon-cyan)' }}></div>
              <h3 className="animate-pulse text-neon-cyan">Optimizing your resume...</h3>
            </div>
          ) : (
            <div className="animate-fade-in h-full">
              <AnalysisResultsPanel results={analysisResults} />
            </div>
          )}
        </div>

        <div className="flex-col h-full relative">
          {tailoredData && !isProcessing ? (
            <div className="animate-fade-in h-full">
              <ResumeDiffViewer tailoredData={tailoredData} />
              <div className="absolute -bottom-4 -right-4">
                <DownloadButton tailoredData={tailoredData} />
              </div>
            </div>
          ) : (
            <div className="card h-full flex flex-col items-center justify-center text-center p-12 border-dashed border-2 border-subtle">
              <Activity size={48} className="text-muted mb-4 opacity-50" />
              <h3 className="text-muted mb-2">Resume Diff Viewer</h3>
              <p className="text-sm text-muted">The side-by-side comparison will appear here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
