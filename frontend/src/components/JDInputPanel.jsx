import { useState } from 'react';
import { Clipboard, Trash2 } from 'lucide-react';

export default function JDInputPanel({ jdText, setJdText }) {
  const [charCount, setCharCount] = useState(jdText ? jdText.length : 0);

  const handleTextChange = (e) => {
    const text = e.target.value;
    setJdText(text);
    setCharCount(text.length);
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      const newText = jdText + (jdText ? '\n' : '') + text;
      setJdText(newText);
      setCharCount(newText.length);
    } catch (err) {
      console.error('Failed to read clipboard contents: ', err);
    }
  };

  const handleClear = () => {
    setJdText('');
    setCharCount(0);
  };

  return (
    <div className="card card--neon mb-8 h-full flex flex-col">
      <div className="mb-6">
        <h3 className="text-xl">Job Description Input Panel</h3>
      </div>

      <div className="form-group flex-1 flex flex-col mb-4">
        <textarea 
          className="form-textarea flex-1" 
          style={{ minHeight: '120px', resize: 'none' }}
          placeholder="Paste the job description you want to target here..."
          value={jdText}
          onChange={handleTextChange}
        ></textarea>
      </div>
      
      <div className="flex gap-4">
        <button className="btn btn--secondary flex-1" onClick={handlePaste}>
          Paste from Clipboard
        </button>
        <button className="btn btn--secondary flex-1" onClick={handleClear}>
          Clear
        </button>
      </div>
    </div>
  );
}
