import { Link } from "react-router-dom";
import { ArrowRight, Cpu, Gauge, Accessibility, Hand } from "lucide-react";

const letters = ["S", "I", "G", "N"];

export default function Home() {
  return (
    <div>
      {/* Hero */}
      <section className="mx-auto grid max-w-6xl gap-12 px-6 pb-20 pt-16 md:grid-cols-2 md:items-center md:pt-24">
        <div>
          <h1 className="font-display text-4xl font-bold leading-[1.1] text-navy md:text-5xl">
            Turn Indian Sign Language into text and speech, instantly.
          </h1>
          <p className="mt-5 max-w-md text-lg text-navy-soft">
            Sign a letter to the camera. SignSpeak AI recognizes the gesture,
            builds it into a sentence, and reads it aloud — all running
            locally, in real time.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-4">
            <Link
              to="/recognize"
              className="focus-ring flex items-center gap-2 rounded-full bg-navy px-6 py-3.5 text-sm font-medium text-white shadow-soft transition-transform hover:scale-[1.02]"
            >
              Start recognition <ArrowRight size={16} />
            </Link>
            <Link
              to="/model"
              className="focus-ring rounded-full px-6 py-3.5 text-sm font-medium text-navy-soft transition-colors hover:text-navy"
            >
              How it works
            </Link>
          </div>
        </div>

        {/* Letter tile illustration - grounded in the actual ISL alphabet subject matter */}
        <div className="relative mx-auto grid w-full max-w-sm grid-cols-2 gap-4">
          {letters.map((letter, i) => (
            <div
              key={letter}
              className={`flex aspect-square items-center justify-center rounded-2xl font-display text-5xl font-bold shadow-soft ${
                ["bg-sky text-white", "bg-lav-soft text-lav", "bg-mint-soft text-mint", "bg-coral-soft text-coral"][i]
              } ${i === 1 ? "translate-y-4" : ""} ${i === 2 ? "-translate-y-2" : ""}`}
            >
              {letter}
            </div>
          ))}
          <span className="absolute -bottom-6 right-0 flex h-12 w-12 items-center justify-center rounded-full bg-surface shadow-soft">
            <Hand size={22} className="text-sky" />
          </span>
        </div>
      </section>

      {/* Feature strip */}
      <section className="border-y border-navy/5 bg-surface">
        <div className="mx-auto grid max-w-6xl gap-8 px-6 py-14 md:grid-cols-3">
          <Feature
            icon={Cpu}
            accent="sky"
            title="AI powered"
            body="A landmark-based MLP classifies normalized hand geometry from MediaPipe. MobileNetV2 remains available as a pixel-model fallback."
          />
          <Feature
            icon={Gauge}
            accent="mint"
            title="Real time"
            body="MediaPipe detects your hand and extracts 21 landmarks. Skeleton visualization shows joint connections in real-time."
          />
          <Feature
            icon={Accessibility}
            accent="lav"
            title="Accessible"
            body="Built sentences are spoken aloud with offline text-to-speech. No API key, no cloud dependency, 100% private."
          />
        </div>
      </section>

      {/* How it works strip */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <h2 className="font-display text-2xl font-semibold text-navy">
          From gesture to sentence
        </h2>
        <div className="mt-8 grid gap-4 md:grid-cols-4">
          {[
            ["Webcam", "Your browser captures frames from the webcam and sends them to the backend."],
            ["Detection", "MediaPipe Hand Pose detects the hand and extracts 21 landmark points with sub-millisecond latency."],
            ["Classification", "A 128-feature landmark MLP classifies up to two hands into one of 35 ISL characters (A–Z, 1–9)."],
            ["Sentence", "Confirmed predictions build into an editable sentence, then spoken aloud using offline TTS."],
          ].map(([title, body], i) => (
            <div key={title} className="rounded-xl2 border border-navy/5 bg-surface p-5 shadow-soft">
              <div className="mb-4 h-1 w-8 rounded-full bg-gradient-to-r from-sky to-lav" />
              <h3 className="font-display font-semibold text-navy">{title}</h3>
              <p className="mt-1.5 text-sm text-navy-soft">{body}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function Feature({ icon: Icon, accent, title, body }) {
  const accents = {
    sky: "bg-sky-soft text-sky-deep",
    mint: "bg-mint-soft text-mint",
    lav: "bg-lav-soft text-lav",
  };
  return (
    <div>
      <span className={`flex h-10 w-10 items-center justify-center rounded-xl ${accents[accent]}`}>
        <Icon size={18} strokeWidth={2.2} />
      </span>
      <h3 className="mt-4 font-display font-semibold text-navy">{title}</h3>
      <p className="mt-1.5 text-sm leading-relaxed text-navy-soft">{body}</p>
    </div>
  );
}
