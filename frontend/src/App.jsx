import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Thermometer,
  Droplets,
  Wind,
  Upload,
  Sparkles,
  Sprout,
  Activity,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  MapPin,
  ShieldCheck,
  ChevronRight,
  Sun,
  Layers,
  Leaf
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function App() {
  // Backend connection status
  const [backendStatus, setBackendStatus] = useState('checking');

  // Section 1: Geo & Environment State
  const [lat, setLat] = useState('37.7749');
  const [lon, setLon] = useState('-122.4194');
  const [envData, setEnvData] = useState(null);
  const [envLoading, setEnvLoading] = useState(false);
  const [envError, setEnvError] = useState('');

  // Section 2: AI Disease Diagnosis State
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [diagLoading, setDiagLoading] = useState(false);
  const [diagResult, setDiagResult] = useState(null);
  const [diagError, setDiagError] = useState('');

  // Section 3: Regenerative Advisory State
  const [selectedCrop, setSelectedCrop] = useState('Tomato');
  const [cropStatusText, setCropStatusText] = useState('Early blight identified with brown spot lesions on lower leaves');
  const [advisoryLoading, setAdvisoryLoading] = useState(false);
  const [advisoryResult, setAdvisoryResult] = useState(null);
  const [advisoryError, setAdvisoryError] = useState('');

  // Check backend health on mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/health`)
      .then((res) => res.json())
      .then((data) => {
        if (data.status === 'healthy') setBackendStatus('online');
        else setBackendStatus('degraded');
      })
      .catch(() => setBackendStatus('offline'));
  }, []);

  // Fetch Environment Data
  const handleFetchEnvironment = async () => {
    setEnvLoading(true);
    setEnvError('');
    try {
      const res = await fetch(`${API_BASE_URL}/environment?lat=${lat}&lon=${lon}`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      setEnvData(data);
    } catch (err) {
      setEnvError('Failed to fetch environment data. Ensure backend is running.');
    } finally {
      setEnvLoading(false);
    }
  };

  // Drag & Drop File Handlers
  const handleFileDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      processFile(file);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file) => {
    if (!file.type.startsWith('image/')) {
      setDiagError('Please select a valid image file (JPG, PNG, WebP)');
      return;
    }
    setSelectedFile(file);
    setDiagError('');
    setDiagResult(null);

    const reader = new FileReader();
    reader.onloadend = () => setImagePreview(reader.result);
    reader.readAsDataURL(file);
  };

  // Run Crop Disease Diagnosis
  const handleDiagnose = async () => {
    if (!selectedFile) {
      setDiagError('Please upload a plant leaf image first.');
      return;
    }

    setDiagLoading(true);
    setDiagError('');
    setDiagResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await fetch(`${API_BASE_URL}/diagnose`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errorDetail = await res.json();
        throw new Error(errorDetail.detail || `HTTP Error ${res.status}`);
      }

      const data = await res.json();
      setDiagResult(data);

      // Auto-update section 3 crop status text
      if (data.top_prediction) {
        setCropStatusText(`${data.top_prediction} (Confidence: ${(data.confidence * 100).toFixed(1)}%)`);
      }
    } catch (err) {
      setDiagError(err.message || 'Diagnosis failed. Check backend endpoint.');
    } finally {
      setDiagLoading(false);
    }
  };

  // Generate 3-Step Regenerative Advisory
  const handleGenerateAdvisory = async () => {
    setAdvisoryLoading(true);
    setAdvisoryError('');
    setAdvisoryResult(null);

    const payload = {
      crop_type: selectedCrop,
      crop_status: cropStatusText,
      latitude: parseFloat(lat) || undefined,
      longitude: parseFloat(lon) || undefined,
      temperature_celsius: envData?.temperature_celsius ?? undefined,
      soil_moisture: envData?.soil_moisture_0_to_1cm ?? undefined,
    };

    try {
      const res = await fetch(`${API_BASE_URL}/generate-advisory`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error(`HTTP Error ${res.status}`);
      const data = await res.json();
      setAdvisoryResult(data);
    } catch (err) {
      setAdvisoryError('Failed to generate advisory. Check API connection.');
    } finally {
      setAdvisoryLoading(false);
    }
  };

  // Motion Variants
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 25 },
    show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
  };

  const stepContainerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2, // Requirement: 0.2s delay between step cards
      },
    },
  };

  const stepCardVariants = {
    hidden: { opacity: 0, x: -30, scale: 0.95 },
    show: { opacity: 1, x: 0, scale: 1, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
  };

  return (
    <div className="min-h-screen bg-[#070D08] text-emerald-50 relative overflow-hidden pb-20">
      {/* Background Ambient Glows */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/3 right-1/4 w-[30rem] h-[30rem] bg-lime-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[40rem] h-[40rem] bg-teal-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <header className="border-b border-emerald-900/40 bg-[#0A140D]/80 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-lime-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Sprout className="w-6 h-6 text-black" />
            </div>
            <div>
              <h1 className="font-heading font-extrabold text-2xl tracking-tight text-white flex items-center gap-2">
                AgriPulse <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-sans font-medium border border-emerald-500/30">v1.0</span>
              </h1>
              <p className="text-xs text-emerald-400/80">Digital Agriculture Interoperability Network</p>
            </div>
          </div>

          {/* Backend Connection Indicator */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-950/60 border border-emerald-800/40 text-xs">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                backendStatus === 'online'
                  ? 'bg-emerald-400 animate-pulse shadow-[0_0_8px_#34d399]'
                  : backendStatus === 'checking'
                  ? 'bg-amber-400 animate-ping'
                  : 'bg-rose-500'
              }`}
            />
            <span className="text-emerald-200/90 font-mono">
              FastAPI: {backendStatus === 'online' ? 'http://localhost:8000' : backendStatus}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-12">
        {/* Intro Hero banner */}
        <div className="glass-panel p-6 rounded-2xl border border-emerald-500/20 relative overflow-hidden">
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h2 className="font-heading text-3xl font-bold text-white mb-2">
                Regenerative Farm Telemetry & AI Intelligence
              </h2>
              <p className="text-emerald-300/80 text-sm max-w-2xl">
                Real-time Open-Meteo micro-climate tracking, Hugging Face crop pathology diagnosis, and Groq-powered 3-step regenerative advisory engine.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-emerald-400/70 bg-emerald-950/80 border border-emerald-800/50 px-3 py-2 rounded-lg font-mono">
                No Database • Pure API Interop
              </span>
            </div>
          </div>
        </div>

        {/* SECTION 1: Geo & Environment */}
        <section className="space-y-6">
          <div className="flex items-center justify-between border-b border-emerald-900/40 pb-3">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <MapPin className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-heading text-xl font-bold text-white">1. Geo & Environmental Telemetry</h3>
                <p className="text-xs text-emerald-400/70">Fetch real-time microclimate and soil moisture data from Open-Meteo API</p>
              </div>
            </div>
          </div>

          {/* Location Form Controls */}
          <div className="glass-card p-6 rounded-2xl grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
            <div>
              <label className="block text-xs font-semibold text-emerald-300/80 uppercase tracking-wider mb-2">
                Latitude (°N)
              </label>
              <input
                type="number"
                step="any"
                value={lat}
                onChange={(e) => setLat(e.target.value)}
                placeholder="37.7749"
                className="w-full bg-[#061009] border border-emerald-800/60 rounded-xl px-4 py-2.5 text-white font-mono text-sm focus:outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400 transition"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-emerald-300/80 uppercase tracking-wider mb-2">
                Longitude (°E)
              </label>
              <input
                type="number"
                step="any"
                value={lon}
                onChange={(e) => setLon(e.target.value)}
                placeholder="-122.4194"
                className="w-full bg-[#061009] border border-emerald-800/60 rounded-xl px-4 py-2.5 text-white font-mono text-sm focus:outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400 transition"
              />
            </div>
            <div>
              <button
                onClick={handleFetchEnvironment}
                disabled={envLoading}
                className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-black font-semibold py-2.5 px-6 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20 active:scale-[0.98] transition disabled:opacity-50 cursor-pointer"
              >
                {envLoading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Fetching Data...</span>
                  </>
                ) : (
                  <>
                    <Activity className="w-4 h-4" />
                    <span>Fetch Data</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {envError && (
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/50 text-rose-300 text-sm flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              <span>{envError}</span>
            </div>
          )}

          {/* Staggered Children Telemetry Display */}
          <AnimatePresence mode="wait">
            {envData && (
              <motion.div
                key={`${envData.latitude}-${envData.longitude}`}
                variants={containerVariants}
                initial="hidden"
                animate="show"
                className="grid grid-cols-1 sm:grid-cols-3 gap-6"
              >
                {/* Metric 1: Temperature */}
                <motion.div
                  variants={itemVariants}
                  className="glass-panel p-6 rounded-2xl border border-amber-500/20 relative overflow-hidden group hover:border-amber-500/40 transition"
                >
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-semibold uppercase tracking-wider text-amber-400/90">Temperature</span>
                    <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      <Thermometer className="w-5 h-5" />
                    </div>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-extrabold font-heading text-white">
                      {envData.temperature_celsius ?? '--'}
                    </span>
                    <span className="text-xl text-amber-400 font-semibold">°C</span>
                  </div>
                  <p className="text-xs text-amber-300/70 mt-2">Surface ambient air temp (2m)</p>
                  <div className="w-full bg-amber-950/40 h-1.5 rounded-full mt-4 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(Math.max((envData.temperature_celsius || 0) * 2, 10), 100)}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut' }}
                      className="bg-gradient-to-r from-amber-500 to-orange-400 h-full rounded-full"
                    />
                  </div>
                </motion.div>

                {/* Metric 2: Soil Moisture (0-1cm) */}
                <motion.div
                  variants={itemVariants}
                  className="glass-panel p-6 rounded-2xl border border-emerald-500/20 relative overflow-hidden group hover:border-emerald-500/40 transition"
                >
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400/90">Soil Moisture (0-1cm)</span>
                    <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <Droplets className="w-5 h-5" />
                    </div>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-extrabold font-heading text-white">
                      {envData.soil_moisture_0_to_1cm ?? '--'}
                    </span>
                    <span className="text-sm text-emerald-400 font-semibold">m³/m³</span>
                  </div>
                  <p className="text-xs text-emerald-300/70 mt-2">Topsoil volumetric water content</p>
                  <div className="w-full bg-emerald-950/40 h-1.5 rounded-full mt-4 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(Math.max((envData.soil_moisture_0_to_1cm || 0) * 200, 10), 100)}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut', delay: 0.1 }}
                      className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full"
                    />
                  </div>
                </motion.div>

                {/* Metric 3: Root Soil Moisture (1-3cm) */}
                <motion.div
                  variants={itemVariants}
                  className="glass-panel p-6 rounded-2xl border border-cyan-500/20 relative overflow-hidden group hover:border-cyan-500/40 transition"
                >
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400/90">Root Zone Moisture (1-3cm)</span>
                    <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                      <Layers className="w-5 h-5" />
                    </div>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-extrabold font-heading text-white">
                      {envData.soil_moisture_1_to_3cm ?? '--'}
                    </span>
                    <span className="text-sm text-cyan-400 font-semibold">m³/m³</span>
                  </div>
                  <p className="text-xs text-cyan-300/70 mt-2">Subsurface root moisture absorption</p>
                  <div className="w-full bg-cyan-950/40 h-1.5 rounded-full mt-4 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(Math.max((envData.soil_moisture_1_to_3cm || 0) * 200, 10), 100)}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
                      className="bg-gradient-to-r from-cyan-500 to-blue-400 h-full rounded-full"
                    />
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </section>

        {/* SECTION 2: AI Disease Diagnosis */}
        <section className="space-y-6">
          <div className="flex items-center justify-between border-b border-emerald-900/40 pb-3">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/20">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-heading text-xl font-bold text-white">2. AI Crop Pathology Diagnosis</h3>
                <p className="text-xs text-emerald-400/70">Forward leaf image to Hugging Face Inference API for disease classification</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
            {/* Drag and Drop Zone */}
            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleFileDrop}
              className={`glass-card p-6 rounded-2xl border-2 border-dashed relative overflow-hidden transition flex flex-col items-center justify-center text-center min-h-[300px] ${
                isDragging
                  ? 'border-emerald-400 bg-emerald-950/40 shadow-xl shadow-emerald-500/10'
                  : 'border-emerald-800/60 hover:border-emerald-500/40'
              }`}
            >
              {imagePreview ? (
                <div className="relative w-full h-64 rounded-xl overflow-hidden group">
                  <img src={imagePreview} alt="Crop Leaf Upload" className="w-full h-full object-cover rounded-xl" />

                  {/* Pulsing Loading Animation Overlay Requirement */}
                  {diagLoading && (
                    <div className="absolute inset-0 bg-black/75 backdrop-blur-sm flex flex-col items-center justify-center p-4">
                      {/* Scanning laser line effect */}
                      <div className="absolute inset-0 scan-line animate-pulse" />
                      <div className="w-16 h-16 rounded-full border-4 border-emerald-400/30 border-t-emerald-400 animate-spin mb-4" />
                      <p className="font-heading font-semibold text-emerald-300 text-sm animate-pulse">
                        Analyzing Leaf Biometrics...
                      </p>
                      <p className="text-xs text-emerald-400/60 mt-1 font-mono">Calling Hugging Face Inference API</p>
                    </div>
                  )}

                  {!diagLoading && (
                    <button
                      onClick={() => { setSelectedFile(null); setImagePreview(null); setDiagResult(null); }}
                      className="absolute top-3 right-3 bg-black/70 text-emerald-300 text-xs px-3 py-1.5 rounded-lg border border-emerald-800/80 hover:bg-rose-950/80 hover:text-rose-300 transition"
                    >
                      Change Image
                    </button>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center mx-auto">
                    <Upload className="w-8 h-8" />
                  </div>
                  <div>
                    <p className="font-medium text-white text-sm">Drag & drop leaf image here</p>
                    <p className="text-xs text-emerald-400/60 mt-1">Supports JPG, PNG, WebP up to 10MB</p>
                  </div>
                  <label className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-950/80 border border-emerald-700/50 text-xs font-semibold text-emerald-300 hover:bg-emerald-900/60 cursor-pointer transition">
                    <span>Browse Image File</span>
                    <input type="file" accept="image/*" onChange={handleFileSelect} className="hidden" />
                  </label>
                </div>
              )}

              {/* Diagnose Action Button */}
              {selectedFile && !diagLoading && (
                <button
                  onClick={handleDiagnose}
                  className="mt-4 w-full bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-black font-semibold py-2.5 px-6 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-teal-500/20 active:scale-[0.98] transition cursor-pointer"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>Run Disease Diagnosis</span>
                </button>
              )}
            </div>

            {/* Diagnostic Results View (Animated Entry Requirement) */}
            <div className="glass-card p-6 rounded-2xl min-h-[300px] flex flex-col justify-center">
              {diagError && (
                <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/50 text-rose-300 text-sm flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                  <span>{diagError}</span>
                </div>
              )}

              {!diagResult && !diagError && !diagLoading && (
                <div className="text-center text-emerald-400/50 py-12">
                  <Leaf className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p className="text-sm">Upload a crop leaf image to reveal AI diagnostic classification & confidence score.</p>
                </div>
              )}

              <AnimatePresence>
                {diagResult && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.92, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                    className="space-y-6"
                  >
                    <div className="border-b border-emerald-900/40 pb-4">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">Diagnosis Classification</span>
                        <span className="text-xs font-mono text-emerald-400/60">{diagResult.model_used?.split('/')[1] || 'Vision Model'}</span>
                      </div>
                      <h4 className="font-heading text-2xl font-extrabold text-white flex items-center gap-2">
                        {diagResult.top_prediction}
                      </h4>
                    </div>

                    {/* Confidence score progress indicator */}
                    <div>
                      <div className="flex justify-between items-center text-xs mb-2">
                        <span className="text-emerald-300/80 font-medium">Confidence Score</span>
                        <span className="font-mono font-bold text-emerald-400 text-sm">
                          {(diagResult.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-emerald-950/60 h-3 rounded-full overflow-hidden border border-emerald-800/40">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${Math.min(diagResult.confidence * 100, 100)}%` }}
                          transition={{ duration: 0.8, ease: 'easeOut' }}
                          className="bg-gradient-to-r from-emerald-500 via-teal-400 to-lime-400 h-full rounded-full"
                        />
                      </div>
                    </div>

                    {/* Predictions breakdown */}
                    {diagResult.predictions && diagResult.predictions.length > 0 && (
                      <div className="space-y-2 pt-2">
                        <span className="text-xs font-semibold text-emerald-300/70 uppercase tracking-wider block mb-2">
                          Top Predicted Probabilities
                        </span>
                        <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
                          {diagResult.predictions.slice(0, 4).map((pred, i) => (
                            <div key={i} className="flex justify-between text-xs bg-emerald-950/40 px-3 py-1.5 rounded-lg border border-emerald-900/30">
                              <span className="text-emerald-200/90 truncate">{pred.label}</span>
                              <span className="font-mono text-emerald-400 font-medium ml-2">
                                {(pred.score * 100).toFixed(1)}%
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </section>

        {/* SECTION 3: Regenerative Advisory */}
        <section className="space-y-6">
          <div className="flex items-center justify-between border-b border-emerald-900/40 pb-3">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-lime-500/10 text-lime-400 border border-lime-500/20">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-heading text-xl font-bold text-white">3. Groq 3-Step Regenerative Advisory Engine</h3>
                <p className="text-xs text-emerald-400/70">Generate tailored 3-step regenerative farming actions based on soil/temp telemetry & disease pathology</p>
              </div>
            </div>
          </div>

          {/* Input Controls */}
          <div className="glass-card p-6 rounded-2xl grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div>
              <label className="block text-xs font-semibold text-emerald-300/80 uppercase tracking-wider mb-2">
                Select Target Crop
              </label>
              <select
                value={selectedCrop}
                onChange={(e) => setSelectedCrop(e.target.value)}
                className="w-full bg-[#061009] border border-emerald-800/60 rounded-xl px-4 py-2.5 text-white font-sans text-sm focus:outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400 transition"
              >
                <option value="Tomato">🍅 Tomato</option>
                <option value="Wheat">🌾 Wheat</option>
                <option value="Corn">🌽 Corn</option>
                <option value="Grape">🍇 Grape</option>
                <option value="Rice">🌾 Rice</option>
                <option value="Potato">🥔 Potato</option>
                <option value="Apple">🍎 Apple</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-emerald-300/80 uppercase tracking-wider mb-2">
                Crop Health Condition / Pathology Description
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={cropStatusText}
                  onChange={(e) => setCropStatusText(e.target.value)}
                  placeholder="e.g. Early blight identified with brown lesions"
                  className="w-full bg-[#061009] border border-emerald-800/60 rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400 transition"
                />
                <button
                  onClick={handleGenerateAdvisory}
                  disabled={advisoryLoading}
                  className="bg-gradient-to-r from-lime-500 to-emerald-500 hover:from-lime-400 hover:to-emerald-400 text-black font-bold py-2.5 px-6 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-lime-500/20 active:scale-[0.98] transition disabled:opacity-50 whitespace-nowrap cursor-pointer"
                >
                  {advisoryLoading ? (
                    <>
                      <Sparkles className="w-4 h-4 animate-spin" />
                      {/* Requirement: Generating... micro-animation */}
                      <span className="animate-pulse">Generating...</span>
                    </>
                  ) : (
                    <>
                      <Sprout className="w-4 h-4" />
                      <span>Generate Advisory</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {advisoryError && (
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/50 text-rose-300 text-sm flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              <span>{advisoryError}</span>
            </div>
          )}

          {/* Sequential 0.2s Delay Card Rendering (Requirement 4) */}
          <AnimatePresence mode="wait">
            {advisoryResult && (
              <div className="space-y-6">
                {/* Advisory Summary Header */}
                <div className="glass-panel p-5 rounded-2xl border border-lime-500/30">
                  <span className="text-xs font-semibold uppercase tracking-wider text-lime-400 block mb-1">
                    Regenerative Action Strategy Overview
                  </span>
                  <p className="text-emerald-100 text-sm font-medium">
                    {advisoryResult.advisory_summary}
                  </p>
                </div>

                {/* Staggered Cards (0.2s delay requirement) */}
                <motion.div
                  variants={stepContainerVariants}
                  initial="hidden"
                  animate="show"
                  className="grid grid-cols-1 md:grid-cols-3 gap-6"
                >
                  {advisoryResult.three_step_advisory?.map((step, idx) => (
                    <motion.div
                      key={step.step_number || idx}
                      variants={stepCardVariants}
                      className="glass-card p-6 rounded-2xl border border-emerald-500/20 flex flex-col justify-between relative overflow-hidden group hover:border-emerald-400/40 transition"
                    >
                      <div>
                        {/* Step Number Pill */}
                        <div className="flex items-center justify-between mb-4">
                          <span className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-heading font-extrabold text-sm flex items-center justify-center">
                            0{step.step_number}
                          </span>
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 opacity-60" />
                        </div>

                        <h4 className="font-heading font-bold text-lg text-white mb-3">
                          {step.title}
                        </h4>

                        <div className="space-y-3 mb-4">
                          <div>
                            <span className="text-[10px] uppercase font-bold text-emerald-400/80 tracking-wider block mb-1">
                              Action Step
                            </span>
                            <p className="text-emerald-100/90 text-xs leading-relaxed">
                              {step.action}
                            </p>
                          </div>

                          <div>
                            <span className="text-[10px] uppercase font-bold text-lime-400/80 tracking-wider block mb-1">
                              Agronomic Rationale
                            </span>
                            <p className="text-emerald-300/70 text-xs leading-relaxed italic bg-emerald-950/40 p-2.5 rounded-lg border border-emerald-900/30">
                              "{step.rationale}"
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="pt-3 border-t border-emerald-900/40 text-[10px] font-mono text-emerald-400/50 flex items-center gap-1">
                        <ChevronRight className="w-3 h-3 text-emerald-400" />
                        <span>Regenerative Protocol</span>
                      </div>
                    </motion.div>
                  ))}
                </motion.div>
              </div>
            )}
          </AnimatePresence>
        </section>
      </main>
    </div>
  );
}
