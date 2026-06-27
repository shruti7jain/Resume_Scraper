import { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle } from 'lucide-react';

export default function ResumeUploader({ onFileSelect }) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFile = (file) => {
    const validMimes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const validExtensions = ['.pdf', '.docx'];
    
    const isValid = validMimes.includes(file.type) || 
                    validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    
    if (isValid) {
      setSelectedFile(file);
      if (onFileSelect) onFileSelect(file);
    } else {
      alert("Please upload a PDF or DOCX file.");
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  return (
    <div className="card card--neon mb-8 h-full">
      <div className="mb-6">
        <h3 className="text-xl">Drag-and-Drop Resume Uploader</h3>
      </div>
      
      {!selectedFile ? (
        <div 
          className={`dropzone ${isDragging ? 'dropzone--active' : ''}`}
          style={{ 
            borderColor: 'var(--neon-cyan)', 
            boxShadow: 'inset 0 0 20px rgba(0, 243, 255, 0.1)',
            minHeight: '200px'
          }}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current.click()}
        >
          <div className="dropzone__icon mb-4" style={{ background: 'transparent', boxShadow: '0 0 20px rgba(0, 243, 255, 0.5)' }}>
            <FileText className="text-neon-cyan" size={40} />
          </div>
          <h4 className="mb-2 text-primary">Drop your resume here or click to upload</h4>
          <p className="text-sm text-muted mb-4">Supports PDF, DOCX, TXT (Max 10MB)</p>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            className="sr-only" 
            accept=".pdf,.docx,.txt"
          />
        </div>
      ) : (
        <div className="flex items-center justify-between p-6 bg-overlay border border-brand rounded-lg animate-fade-in h-[200px]">
          <div className="flex items-center gap-4">
            <div className="bg-brand rounded p-4 text-white shadow-brand">
              <FileText size={32} />
            </div>
            <div>
              <h5 className="mb-2 text-lg text-neon-cyan">{selectedFile.name}</h5>
              <p className="text-sm text-success flex items-center gap-2">
                <CheckCircle size={16} /> Ready for analysis
              </p>
            </div>
          </div>
          <button 
            className="btn btn--outline text-danger"
            style={{ borderColor: 'var(--brand-danger)', color: 'var(--brand-danger)' }}
            onClick={(e) => {
              e.stopPropagation();
              setSelectedFile(null);
              if (onFileSelect) onFileSelect(null);
            }}
          >
            Remove
          </button>
        </div>
      )}
    </div>
  );
}
