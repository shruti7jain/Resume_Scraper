import { Download } from 'lucide-react';
import { useState } from 'react';
import axios from 'axios';

export default function DownloadButton({ tailoredData }) {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      // Assuming backend returns a blob for the PDF
      const response = await axios.post('http://localhost:8000/api/download-pdf', tailoredData, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'tailored_resume.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to download PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="absolute -bottom-4 -right-4 z-50">
      <button 
        className="btn btn--lg rounded-full flex items-center gap-2 px-6 py-3 font-bold text-white shadow-lg transition-transform hover:scale-105"
        style={{
          background: 'linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%)',
          boxShadow: '0 0 20px rgba(0, 243, 255, 0.6), inset 0 0 10px rgba(255,255,255,0.4)',
          border: '2px solid rgba(255,255,255,0.2)',
          textShadow: '0 1px 2px rgba(0,0,0,0.2)'
        }}
        onClick={handleDownload}
        disabled={isDownloading || !tailoredData}
      >
        {isDownloading ? (
          <div className="spinner mr-2 border-t-white"></div>
        ) : (
          <Download size={20} />
        )}
        Download Tailored PDF
      </button>
    </div>
  );
}
