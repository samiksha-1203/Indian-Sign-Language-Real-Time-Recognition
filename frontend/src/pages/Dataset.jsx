import { useEffect, useState } from "react";
import MetricCard from "../components/MetricCard.jsx";
import { Images, Layers, FileImage, Ruler } from "lucide-react";
import api from "../services/api.js";

export default function Dataset() {
  const [info, setInfo] = useState(null);

  useEffect(() => {
    api.datasetInfo().then(setInfo).catch(() => setInfo(null));
  }, []);

  const letters = info?.per_class_counts
    ? Object.keys(info.per_class_counts).filter((c) => /[A-Z]/.test(c)).sort()
    : [];
  const digits = info?.per_class_counts
    ? Object.keys(info.per_class_counts).filter((c) => /[0-9]/.test(c)).sort((a, b) => a - b)
    : [];

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="font-display text-2xl font-semibold text-navy">Dataset</h1>
      <p className="mt-1 max-w-2xl text-sm text-navy-soft">
        Indian Sign Language (ISL) character & numeral dataset from Kaggle 
        <a href="https://www.kaggle.com/datasets/prathumarikeri/indian-sign-language-isl" className="text-sky hover:underline"> prathumarikeri/indian-sign-language-isl</a>.
        The source dataset contains 42,745 hand-shape images across 35 classes (A–Z and 1–9).
        MediaPipe extracted usable landmarks from 41,670 images for the active model.
        All statistics are computed from the actual dataset or saved model reports.
      </p>

      {!info?.report_available ? (
        <div className="mt-8 rounded-xl2 border border-coral/20 bg-coral-soft px-5 py-4 text-sm text-coral">
          No dataset report found yet. Run{" "}
          <code className="rounded bg-white/60 px-1.5 py-0.5">python ml/dataset_inspector.py</code>{" "}
          from the backend to generate it.
        </div>
      ) : (
        <>
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard label="Total images" value={info.total_images?.toLocaleString()} icon={Images} accent="sky" />
            <MetricCard label="Classes" value={info.total_classes} icon={Layers} accent="mint" />
            <MetricCard
              label="Formats"
              value={info.image_formats ? Object.keys(info.image_formats).join(", ") : "—"}
              icon={FileImage}
              accent="lav"
            />
            <MetricCard
              label="Most common size"
              value={info.image_dimensions?.most_common ? info.image_dimensions.most_common.join("×") : "—"}
              icon={Ruler}
              accent="coral"
            />
          </div>

          <div className="mt-10 rounded-xl2 border border-navy/5 bg-surface p-6 shadow-soft">
            <h2 className="font-display font-semibold text-navy">Class grid</h2>
            <p className="mt-1 text-sm text-navy-soft">Each tile shows the real image count for that class.</p>

            <p className="mt-5 text-xs font-medium uppercase tracking-normal text-mist">Letters</p>
            <div className="mt-2 grid grid-cols-5 gap-2 sm:grid-cols-7 md:grid-cols-9">
              {letters.map((c) => (
                <ClassTile key={c} label={c} count={info.per_class_counts[c]} />
              ))}
            </div>

            <p className="mt-6 text-xs font-medium uppercase tracking-normal text-mist">Numerals</p>
            <div className="mt-2 grid grid-cols-5 gap-2 sm:grid-cols-7 md:grid-cols-9">
              {digits.map((c) => (
                <ClassTile key={c} label={c} count={info.per_class_counts[c]} />
              ))}
            </div>
            <p className="mt-4 text-xs text-mist">
              No "0" class is present in this dataset, so it isn't recognized.
            </p>
          </div>

          {info.class_imbalance && (
            <div className="mt-6 rounded-xl2 border border-navy/5 bg-surface p-6 shadow-soft text-sm text-navy-soft">
              Class balance: {info.class_imbalance.min_class_count}–{info.class_imbalance.max_class_count} images
              per class ({info.class_imbalance.imbalance_ratio?.toFixed(2)}× ratio) —
              close enough to balanced that no resampling was needed.
            </div>
          )}
        </>
      )}
    </div>
  );
}

function ClassTile({ label, count }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg bg-sky-soft py-3">
      <span className="font-display text-lg font-semibold text-navy">{label}</span>
      <span className="text-[10px] text-navy-soft">{count}</span>
    </div>
  );
}
