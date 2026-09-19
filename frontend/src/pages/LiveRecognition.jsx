import { useCallback, useEffect, useRef, useState } from "react";
import { Circle } from "lucide-react";
import Webcam from "../components/Webcam.jsx";
import PredictionCard from "../components/PredictionCard.jsx";
import SentenceBuilder from "../components/SentenceBuilder.jsx";
import api from "../services/api.js";

function useSessionId() {
  const [sessionId, setSessionId] = useState(null);
  useEffect(() => {
    let id = localStorage.getItem("signspeak_session_id");
    if (!id) {
      api.sentenceCreate().then((res) => {
        localStorage.setItem("signspeak_session_id", res.session_id);
        setSessionId(res.session_id);
      });
    } else {
      setSessionId(id);
    }
  }, []);
  return sessionId;
}

export default function LiveRecognition() {
  const sessionId = useSessionId();
  const [health, setHealth] = useState(null);
  const [result, setResult] = useState(null);
  const [sentence, setSentence] = useState("");
  const [speaking, setSpeaking] = useState(false);
  const [modelError, setModelError] = useState(null);
  const busyRef = useRef(false);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null));
    const id = setInterval(() => {
      api.health().then(setHealth).catch(() => setHealth(null));
    }, 10000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (sessionId) {
      api.sentenceGet(sessionId).then((res) => setSentence(res.sentence)).catch(() => {});
    }
  }, [sessionId]);

  const handleFrame = useCallback(
    async (base64) => {
      if (!sessionId || busyRef.current) return;
      busyRef.current = true;
      try {
        const res = await api.predictStatic(sessionId, base64);
        setResult(res);
        setModelError(null);
        if (res.confirmed && res.confirmed_char) {
          const updated = await api.sentenceAdd(sessionId, res.confirmed_char);
          setSentence(updated.sentence);
        }
      } catch (err) {
        if (err.status === 503) setModelError(err.message);
      } finally {
        busyRef.current = false;
      }
    },
    [sessionId]
  );

  async function handleSpeak() {
    if (!sentence) return;
    setSpeaking(true);
    try {
      await api.speak(sentence);
    } catch (_) {
      /* surfaced via disabled state; keep UI quiet on TTS backend errors */
    } finally {
      setSpeaking(false);
    }
  }

  const handBoxOverlay = result?.hand_box
    ? toBoxPct(result.hand_box)
    : null;

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold text-navy">Live recognition</h1>
          <p className="mt-1 text-sm text-navy-soft">Point your hand to the camera. The white skeleton shows detected hand joints in real-time. Confirmed characters build into a sentence.</p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs font-medium">
          <StatusPill ok={!!health} label={health ? "API connected" : "API offline"} />
          <StatusPill ok={health?.model_loaded} label={health?.model_loaded ? "Model ready" : "Model not trained"} />
          <StatusPill ok={health?.gpu_available} neutral label={health?.gpu_available ? "GPU" : "CPU"} />
        </div>
      </div>

      {modelError && (
        <div className="mb-6 rounded-xl2 border border-coral/20 bg-coral-soft px-5 py-4 text-sm text-coral">
          {modelError} — train the model (see README) then restart the API.
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-[1.3fr_1fr]">
        <Webcam onFrame={handleFrame} handBox={handBoxOverlay} handLandmarks={result?.hand_landmarks} />
        <PredictionCard result={result} />
      </div>

      <div className="mt-6">
        <SentenceBuilder
          sentence={sentence}
          onSpace={async () => setSentence((await api.sentenceSpace(sessionId)).sentence)}
          onBackspace={async () => setSentence((await api.sentenceBackspace(sessionId)).sentence)}
          onClear={async () => setSentence((await api.sentenceClear(sessionId)).sentence)}
          onSpeak={handleSpeak}
          speaking={speaking}
        />
      </div>
    </div>
  );
}

function StatusPill({ ok, neutral, label }) {
  const color = neutral ? "text-sky-deep bg-sky-soft" : ok ? "text-mint bg-mint-soft" : "text-coral bg-coral-soft";
  return (
    <span className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 ${color}`}>
      <Circle size={7} className="fill-current" /> {label}
    </span>
  );
}

// hand_box comes back as [x_min, y_min, x_max, y_max] in source-frame pixel
// coords. We don't know the exact source resolution client-side beyond what
// the canvas captured, so this is a best-effort overlay sized against a
// typical 640x480 capture (see Webcam.jsx canvas sizing).
function toBoxPct([x1, y1, x2, y2], frameW = 640, frameH = 480) {
  return {
    leftPct: (1 - x2 / frameW) * 100,
    topPct: (y1 / frameH) * 100,
    widthPct: ((x2 - x1) / frameW) * 100,
    heightPct: ((y2 - y1) / frameH) * 100,
  };
}
