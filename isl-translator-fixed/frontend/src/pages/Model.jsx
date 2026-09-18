import { useEffect, useState } from "react";
import MetricCard from "../components/MetricCard.jsx";
import { Brain, Boxes, HardDrive, Calendar } from "lucide-react";
import api from "../services/api.js";

const rows = (info) => [
  ["Model", info?.model_name || "Not trained yet"],
  ["Architecture", info?.architecture || "—"],
  ["Framework", info?.framework || "—"],
  ["Input shape", info?.input_shape ? info.input_shape.join(" × ") : "—"],
  ["Feature vector", info?.feature_dim ? `${info.feature_dim} normalized landmark values` : "—"],
  ["Classes", info?.num_classes ?? "—"],
  ["Dataset", info?.dataset || "—"],
  ["Test accuracy", info?.test_accuracy != null ? `${(info.test_accuracy * 100).toFixed(2)}%` : "—"],
  ["Macro F1", info?.f1 != null ? `${(info.f1 * 100).toFixed(2)}%` : "—"],
  ["Model size", info?.model_size_mb ? `${info.model_size_mb} MB` : "—"],
  ["Trained on", info?.training_date ? new Date(info.training_date).toLocaleString() : "—"],
];

export default function Model() {
  const [info, setInfo] = useState(null);

  useEffect(() => {
    api.modelInfo().then(setInfo).catch(() => setInfo(null));
  }, []);

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <h1 className="font-display text-2xl font-semibold text-navy">Model</h1>
      <p className="mt-1 text-sm text-navy-soft">
        The active system uses MediaPipe hand landmarks and a TensorFlow/Keras MLP. It normalizes up to two hands into a 128-value feature vector, then applies confidence thresholding and temporal smoothing for real-time predictions.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Architecture" value={info?.architecture || "—"} icon={Brain} accent="sky" />
        <MetricCard label="Classes" value={info?.num_classes ?? "—"} icon={Boxes} accent="mint" />
        <MetricCard label="Size" value={info?.model_size_mb ? `${info.model_size_mb} MB` : "—"} icon={HardDrive} accent="lav" />
        <MetricCard
          label="Trained"
          value={info?.training_date ? new Date(info.training_date).toLocaleDateString() : "Not yet"}
          icon={Calendar}
          accent="coral"
        />
      </div>

      <div className="mt-8 rounded-xl2 border border-navy/5 bg-surface p-6 shadow-soft">
        {!info?.model_loaded && (
          <div className="mb-5 rounded-xl bg-coral-soft px-4 py-3 text-sm text-coral">
            No trained model is currently loaded. Run{" "}
            <code className="rounded bg-white/60 px-1.5 py-0.5">train.py --mode full</code>{" "}
            then <code className="rounded bg-white/60 px-1.5 py-0.5">evaluate.py</code> on the backend.
          </div>
        )}
        <dl className="divide-y divide-navy/5">
          {rows(info).map(([label, value]) => (
            <div key={label} className="flex items-center justify-between py-3 text-sm">
              <dt className="text-navy-soft">{label}</dt>
              <dd className="font-medium text-navy">{value}</dd>
            </div>
          ))}
        </dl>
      </div>

      {info?.classes && (
        <div className="mt-6 rounded-xl2 border border-navy/5 bg-surface p-6 shadow-soft">
          <h2 className="font-display font-semibold text-navy">Recognized classes</h2>
          <p className="mt-1 text-sm text-navy-soft">All 35 ISL alphabet characters and numerals supported by the active model.</p>
          <div className="mt-4 grid grid-cols-7 gap-2 sm:grid-cols-9 md:grid-cols-11">
            {info.classes.map((c) => (
              <div
                key={c}
                className="flex items-center justify-center rounded-lg bg-sky-soft py-2 px-1.5 text-sm font-semibold text-sky-deep shadow-sm"
              >
                {c}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
