import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Home from "./pages/Home.jsx";
import LiveRecognition from "./pages/LiveRecognition.jsx";
import Analytics from "./pages/Analytics.jsx";
import Dataset from "./pages/Dataset.jsx";
import Model from "./pages/Model.jsx";

export default function App() {
  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/recognize" element={<LiveRecognition />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/dataset" element={<Dataset />} />
        <Route path="/model" element={<Model />} />
      </Routes>
      <footer className="mx-auto max-w-6xl px-6 py-10 text-center text-xs text-mist">
        SignSpeak AI — Real-time Indian Sign Language recognition with hand skeleton visualization.
        Static character classification (A–Z, 1–9) with live landmark tracking, offline TTS, and editable sentence building.
      </footer>
    </div>
  );
}
