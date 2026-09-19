export default function MetricCard({ label, value, accent = "sky", icon: Icon, hint }) {
  const accents = {
    sky: "bg-sky-soft text-sky-deep",
    lav: "bg-lav-soft text-lav",
    mint: "bg-mint-soft text-mint",
    coral: "bg-coral-soft text-coral",
  };

  return (
    <div className="rounded-xl2 border border-navy/5 bg-surface p-5 shadow-soft">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-navy-soft">{label}</span>
        {Icon && (
          <span className={`flex h-8 w-8 items-center justify-center rounded-lg ${accents[accent]}`}>
            <Icon size={16} strokeWidth={2.2} />
          </span>
        )}
      </div>
      <p className="mt-3 font-display text-2xl font-semibold text-navy">{value}</p>
      {hint && <p className="mt-1 text-xs text-mist">{hint}</p>}
    </div>
  );
}
