import { Volume2, Delete, RotateCcw, Space } from "lucide-react";

export default function SentenceBuilder({ sentence, onSpace, onBackspace, onClear, onSpeak, speaking }) {
  return (
    <div className="rounded-xl2 border border-navy/5 bg-surface p-6 shadow-soft">
      <h3 className="font-display text-sm font-semibold text-navy-soft">Current sentence</h3>

      <div className="mt-3 min-h-[4rem] rounded-xl bg-lav-soft px-5 py-4 font-display text-2xl font-medium tracking-wide text-navy">
        {sentence || <span className="text-mist">Sign a letter to begin…</span>}
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <button
          onClick={onSpace}
          className="focus-ring flex items-center gap-1.5 rounded-full border border-navy/10 bg-surface px-4 py-2 text-sm font-medium text-navy-soft transition-colors hover:bg-sky-soft hover:text-navy"
        >
          <Space size={15} /> Space
        </button>
        <button
          onClick={onBackspace}
          className="focus-ring flex items-center gap-1.5 rounded-full border border-navy/10 bg-surface px-4 py-2 text-sm font-medium text-navy-soft transition-colors hover:bg-sky-soft hover:text-navy"
        >
          <Delete size={15} /> Backspace
        </button>
        <button
          onClick={onClear}
          className="focus-ring flex items-center gap-1.5 rounded-full border border-navy/10 bg-surface px-4 py-2 text-sm font-medium text-navy-soft transition-colors hover:bg-coral-soft hover:text-coral"
        >
          <RotateCcw size={15} /> Clear
        </button>
        <button
          onClick={onSpeak}
          disabled={!sentence || speaking}
          className="focus-ring ml-auto flex items-center gap-1.5 rounded-full bg-navy px-5 py-2 text-sm font-medium text-white transition-transform hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Volume2 size={15} /> {speaking ? "Speaking…" : "Speak"}
        </button>
      </div>
    </div>
  );
}
