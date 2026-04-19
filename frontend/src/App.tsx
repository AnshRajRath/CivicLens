import React, { useState } from 'react';
import { 
  Home, 
  FileText, 
  Compass, 
  CloudUpload,    // Renamed from UploadCloud
  CircleCheck,    // Renamed from CheckCircle
  TriangleAlert,  // Renamed from AlertTriangle
  Brain,          // Renamed/Simplified from BrainCircuit
  ShieldCheck, 
  ArrowRight, 
  PieChart,       // Replaced BarChart3 with stable PieChart
  LoaderCircle,   // Renamed from Loader2
  RotateCcw       // Replaced RefreshCcw with RotateCcw for stability
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// THIS CONNECTS TO YOUR PYTHON BACKEND
const API_BASE_URL = "http://localhost:8000";

// --- HELPER: Simple Markdown Parser (Zero Dependency) ---
const SimpleMarkdown = ({ content }: { content: string }) => {
  if (!content) return null;

  // Helper to parse bold text (**text**) within a string
  const parseBold = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="text-slate-100 font-semibold">{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  return (
    <div className="space-y-2">
      {content.split('\n').map((line, index) => {
        // Headers (## Title)
        if (line.trim().startsWith('## ')) {
          return (
            <h3 key={index} className="text-xl font-bold text-emerald-400 mt-6 mb-3 block">
              {line.replace('## ', '')}
            </h3>
          );
        }
        // List Items (- Item)
        if (line.trim().startsWith('- ')) {
          return (
            <div key={index} className="flex items-start ml-4 mb-2">
              <span className="mr-2 text-emerald-500">•</span>
              <span className="text-slate-300">{parseBold(line.replace('- ', ''))}</span>
            </div>
          );
        }
        // Empty lines
        if (!line.trim()) {
          return <div key={index} className="h-2" />;
        }
        // Regular Paragraphs
        return (
          <p key={index} className="text-slate-300 leading-relaxed mb-2">
            {parseBold(line)}
          </p>
        );
      })}
    </div>
  );
};

type ViewState = 'home' | 'decoder' | 'quiz';

// --- COMPONENTS ---

const SidebarItem = ({ icon: Icon, label, active, onClick }: any) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center space-x-3 px-6 py-4 transition-all duration-200 ${
      active 
        ? 'bg-emerald-500 text-white shadow-lg border-r-4 border-emerald-300' 
        : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'
    }`}
  >
    <Icon size={20} />
    <span className="font-medium tracking-wide">{label}</span>
  </button>
);

// --- VIEWS ---

const HomeView = ({ setView }: any) => (
  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto space-y-12 pt-10 text-center">
    <div className="space-y-4">
      <h1 className="text-5xl font-bold text-slate-100 tracking-tight">
        Welcome to <span className="text-emerald-400">CivicLens</span>
      </h1>
      <p className="text-xl text-slate-400 max-w-2xl mx-auto">
        Bringing transparency to political discourse through AI-powered analysis.
      </p>
    </div>

    <div className="grid md:grid-cols-2 gap-8">
      <div 
        className="bg-slate-800/50 border border-slate-700 p-8 rounded-2xl shadow-xl hover:shadow-emerald-500/10 cursor-pointer transition-all hover:-translate-y-1"
        onClick={() => setView('decoder')}
      >
        <div className="bg-emerald-500/10 w-16 h-16 rounded-xl flex items-center justify-center mb-6 mx-auto">
          <FileText className="text-emerald-400" size={32} />
        </div>
        <h2 className="text-2xl font-bold text-slate-100 mb-3">Manifesto Decoder</h2>
        <p className="text-slate-400 mb-6">Upload manifestos for AI feasibility analysis.</p>
        <div className="flex items-center justify-center text-emerald-400 font-medium">
          Start Analysis <ArrowRight size={18} className="ml-2" />
        </div>
      </div>

      <div 
        className="bg-slate-800/50 border border-slate-700 p-8 rounded-2xl shadow-xl hover:shadow-emerald-500/10 cursor-pointer transition-all hover:-translate-y-1"
        onClick={() => setView('quiz')}
      >
        <div className="bg-emerald-500/10 w-16 h-16 rounded-xl flex items-center justify-center mb-6 mx-auto">
          <PieChart className="text-emerald-400" size={32} />
        </div>
        <h2 className="text-2xl font-bold text-slate-100 mb-3">Alignment Compass</h2>
        <p className="text-slate-400 mb-6">Discover your political alignment.</p>
        <div className="flex items-center justify-center text-emerald-400 font-medium">
          Take Quiz <ArrowRight size={18} className="ml-2" />
        </div>
      </div>
    </div>
  </motion.div>
);

const DecoderView = () => {
  const [status, setStatus] = useState<'idle' | 'processing' | 'done' | 'error'>('idle');
  const [result, setResult] = useState<any>(null);
  const [simStep, setSimStep] = useState(0);

  const steps = [
    "Orchestrator: Parsing Document Structure...", 
    "Economist: Cross-referencing Fiscal Claims...", 
    "Sociologist: Evaluating Social Impact...", 
    "Skeptic: Synthesizing Final Verdict..."
  ];

  const handleUpload = async (file: File) => {
    setStatus('processing');
    const interval = setInterval(() => setSimStep(p => (p < steps.length - 1 ? p + 1 : p)), 2000);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE_URL}/analyze/upload`, { method: 'POST', body: formData });
      if (!res.ok) throw new Error("Server Error");
      const data = await res.json();
      setResult(data);
      setStatus('done');
    } catch (e) {
      console.error(e);
      setStatus('error');
    } finally {
      clearInterval(interval);
    }
  };

  if (status === 'processing') return (
    <div className="max-w-2xl mx-auto pt-32 text-center space-y-8">
      <LoaderCircle className="animate-spin text-emerald-500 mx-auto" size={64} />
      <div>
        <h3 className="text-2xl font-bold text-slate-100 tracking-tight">Analyzing Document</h3>
        <p className="text-slate-400 h-6 mt-2 font-medium">{steps[simStep]}</p>
      </div>
      <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
        <motion.div 
          className="h-full bg-emerald-500" 
          animate={{ width: `${((simStep + 1) / steps.length) * 100}%` }} 
        />
      </div>
    </div>
  );

  if (status === 'done' && result) return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-4xl mx-auto space-y-10 pt-10 pb-20">
      <div className="flex justify-between items-end border-b border-slate-800 pb-6">
        <div>
          <h2 className="text-4xl font-bold text-slate-100 tracking-tight">Analysis Report</h2>
          <p className="text-slate-400 mt-2">AI-Driven Manifesto Audit</p>
        </div>
        <button onClick={() => setStatus('idle')} className="flex items-center text-slate-400 hover:text-white text-sm bg-slate-800 px-4 py-2 rounded-lg transition-colors">
          <RotateCcw size={14} className="mr-2" /> Analyze Another
        </button>
      </div>

      {/* Scores Section */}
      {result.feasibility_score > 0 && (
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-slate-800/50 p-8 rounded-2xl border border-slate-700 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-200">Feasibility Score</h3>
              <p className="text-slate-400 text-sm mt-1 max-w-[200px]">Assessment of budget realism and practical implementation.</p>
            </div>
            <div className="text-5xl font-bold text-emerald-400">{result.feasibility_score}</div>
          </div>
          <div className="bg-slate-800/50 p-8 rounded-2xl border border-slate-700 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-200">Trust Meter</h3>
              <p className="text-slate-400 text-sm mt-1 max-w-[200px]">Based on historical consistency and fact-checking.</p>
            </div>
            <div className="text-5xl font-bold text-blue-400">{result.trust_score}</div>
          </div>
        </div>
      )}

      {/* Main Report Area - Full Width */}
      <div className={`bg-slate-800/30 border border-slate-700 rounded-3xl p-10 shadow-2xl ${result.feasibility_score === 0 ? 'border-rose-500/50 bg-rose-900/10' : ''}`}>
        <SimpleMarkdown content={result.summary} />
      </div>
    </motion.div>
  );

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-4xl mx-auto space-y-8 pt-12">
      <div className="text-center space-y-2">
        <h2 className="text-4xl font-bold text-slate-100">Manifesto Decoder</h2>
        <p className="text-slate-400">Upload a political document for a comprehensive AI audit.</p>
      </div>
      
      <div 
        className={`border-2 border-dashed rounded-3xl h-80 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 ${
          status === 'error' ? 'border-rose-500 bg-rose-500/10' : 'border-slate-700 hover:border-emerald-500 hover:bg-slate-800/50'
        }`}
        onClick={() => document.getElementById('file-upload')?.click()}
      >
        <input 
          type="file" 
          id="file-upload" 
          className="hidden" 
          accept=".pdf" 
          onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])} 
        />
        {status === 'error' ? (
          <>
            <TriangleAlert className="text-rose-500 mb-4" size={56} />
            <p className="text-rose-400 font-medium text-lg">Analysis Failed</p>
            <p className="text-rose-300/70 text-sm mt-2">Ensure the backend is running.</p>
          </>
        ) : (
          <>
            <div className="bg-slate-800 p-6 rounded-full mb-6 group-hover:scale-110 transition-transform">
              <CloudUpload className="text-emerald-400" size={48} />
            </div>
            <h3 className="text-xl font-semibold text-slate-200">Click to Upload PDF</h3>
            <p className="text-slate-500 mt-2 text-sm">Supports standard text-based PDF files</p>
          </>
        )}
      </div>
    </motion.div>
  );
};

const QuizView = () => {
  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState<any>({});
  const [result, setResult] = useState<any>(null);

  const qs = [
    {id:"1", t:"The government should increase taxes to fund services."},
    {id:"2", t:"Environmental regulations are more important than growth."},
    {id:"3", t:"Defense spending should be cut."},
    {id:"4", t:"Universal healthcare is a fundamental right."},
    {id:"5", t:"AI development needs strict regulation."}
  ];

  const handleAnswer = (score: number) => {
    const next = {...answers, [qs[idx].id]: score};
    setAnswers(next);
    if (idx < qs.length - 1) {
      setIdx(idx + 1);
    } else {
      fetch(`${API_BASE_URL}/quiz-alignment`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({answers: next})
      })
      .then(r => r.json())
      .then(setResult)
      .catch(() => alert("Backend Error"));
    }
  };

  if (result) return (
    <div className="max-w-4xl mx-auto pt-10 text-center">
      <div className="bg-slate-800 border border-slate-700 rounded-3xl p-12 shadow-2xl inline-block">
        <Compass size={48} className="text-emerald-500 mx-auto mb-6" />
        <h2 className="text-3xl font-bold text-slate-100 mb-2">You align with: <span className="text-emerald-400">{result.aligned_party}</span></h2>
        <p className="text-slate-400 mb-8">{result.match_percentage}% Match</p>
        <p className="text-slate-300 mb-8 max-w-md mx-auto">{result.explanation}</p>
        <button onClick={() => {setResult(null); setIdx(0);}} className="bg-slate-700 text-white px-8 py-3 rounded-full hover:bg-slate-600">
          Retake Quiz
        </button>
      </div>
    </div>
  );

  return (
    <div className="max-w-3xl mx-auto pt-10 space-y-8">
      <h2 className="text-3xl font-bold text-slate-100">Alignment Compass</h2>
      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
        <div className="h-full bg-emerald-500 transition-all duration-300" style={{width: `${((idx+1)/qs.length)*100}%`}} />
      </div>
      <div className="bg-slate-800 border border-slate-700 rounded-3xl p-10 shadow-lg">
        <h3 className="text-2xl font-medium text-slate-100 mb-8">{qs[idx].t}</h3>
        <div className="space-y-3">
          {[{l:'Strongly Disagree',s:-2}, {l:'Disagree',s:-1}, {l:'Neutral',s:0}, {l:'Agree',s:1}, {l:'Strongly Agree',s:2}].map((o, i) => (
            <button 
              key={i} 
              onClick={() => handleAnswer(o.s)}
              className="w-full text-left p-4 rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-700 hover:border-emerald-500 hover:text-white transition-all"
            >
              {o.l}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

function App() {
  const [activeTab, setActiveTab] = useState<ViewState>('home');

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200 font-sans flex">
      <nav className="fixed left-0 top-0 h-full w-72 bg-slate-900 border-r border-slate-800 p-6 flex flex-col">
        <div className="mb-10 flex items-center space-x-3 px-2">
          <ShieldCheck className="text-emerald-500" size={32} />
          <h1 className="text-2xl font-bold tracking-tight">CivicLens</h1>
        </div>
        <div className="space-y-2">
          <SidebarItem icon={Home} label="Home" active={activeTab === 'home'} onClick={() => setActiveTab('home')} />
          <SidebarItem icon={FileText} label="Decoder" active={activeTab === 'decoder'} onClick={() => setActiveTab('decoder')} />
          <SidebarItem icon={Compass} label="Compass" active={activeTab === 'quiz'} onClick={() => setActiveTab('quiz')} />
        </div>
      </nav>
      <main className="pl-72 flex-1 p-12">
        <AnimatePresence mode="wait">
          {activeTab === 'home' && <HomeView key="home" setView={setActiveTab} />}
          {activeTab === 'decoder' && <DecoderView key="decoder" />}
          {activeTab === 'quiz' && <QuizView key="quiz" />}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;