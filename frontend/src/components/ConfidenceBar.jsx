export default function ConfidenceBar({ confidence = 0 }) {
  const pct = Math.round(Math.max(0, Math.min(1, confidence)) * 100);
  const color =
    pct >= 75 ? "bg-mint" : pct >= 50 ? "bg-sky" : "bg-coral";

  return (
    <div>
      <div className="flex items-center justify-between text-xs text-navy-soft">
        <span>Confidence</span>
        <span className="font-medium text-navy">{pct}%</span>
      </div>
      <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-sky-soft">
        <div
          className={`h-full rounded-full ${color} transition-[width] duration-300 ease-out`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
