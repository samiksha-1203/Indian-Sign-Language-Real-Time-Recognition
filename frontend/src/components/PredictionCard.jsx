import { CheckCircle2, Circle, AlertCircle } from "lucide-react";
import ConfidenceBar from "./ConfidenceBar.jsx";

const statusCopy = {
  no_hand: { label: "No hand detected", tone: "text-mist" },
  low_confidence: { label: "Uncertain", tone: "text-coral" },
  collecting: { label: "Reading gesture…", tone: "text-sky-deep" },
  held: { label: "Stable — hold or release", tone: "text-lav" },
  confirmed: { label: "Confirmed", tone: "text-mint" },
};

export default function PredictionCard({ result }) {
  const status = statusCopy[result?.status] || { label: "Waiting for camera", tone: "text-mist" };
  const display = result?.display && result.display !== "Uncertain" ? result.display : null;

  return (
    <div className="rounded-xl2 border border-navy/5 bg-surface p-6 shadow-soft">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-sm font-semibold text-navy-soft">Prediction</h3>
        {result?.stable ? (
          <CheckCircle2 size={16} className="text-mint" />
        ) : result?.status === "no_hand" ? (
          <Circle size={16} className="text-mist" />
        ) : (
          <AlertCircle size={16} className="text-coral" />
        )}
      </div>

      <div className="my-6 flex h-28 items-center justify-center rounded-xl bg-sky-soft">
        <span className="font-display text-6xl font-bold text-navy">
          {display || "–"}
        </span>
      </div>

      <ConfidenceBar confidence={result?.confidence || 0} />

      <p className={`mt-4 text-sm font-medium ${status.tone}`}>{status.label}</p>
    </div>
  );
}
