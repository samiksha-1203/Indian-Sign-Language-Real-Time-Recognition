import { useEffect, useState } from "react";
import { Target, Gauge, Award, Activity } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import MetricCard from "../components/MetricCard.jsx";
import api from "../services/api.js";

export default function Analytics() {
  const [modelInfo, setModelInfo] = useState(null);
  const [summary, setSummary] = useState(null);
  const [classDist, setClassDist] = useState(null);

  useEffect(() => {
    api.modelInfo().then(setModelInfo).catch(() => setModelInfo(null));
    api.analyticsPredictions().then(setSummary).catch(() => setSummary(null));
    api.analyticsClasses().then((res) => setClassDist(res.class_distribution)).catch(() => setClassDist(null));
  }, []);

  const chartData = classDist
    ? Object.entries(classDist).map(([name, count]) => ({ name, count }))
    : [];

  const pct = (v) => (v == null ? "—" : `${(v * 100).toFixed(1)}%`);

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="font-display text-2xl font-semibold text-navy">Analytics</h1>
      <p className="mt-1 text-sm text-navy-soft">
        Test-set metrics for the active landmark model. Predictions are logged with confidence scores, and usage totals update as you use the recognition system.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Test accuracy" value={pct(modelInfo?.test_accuracy)} icon={Target} accent="sky" />
        <MetricCard label="Precision (macro)" value={pct(modelInfo?.precision)} icon={Gauge} accent="mint" />
        <MetricCard label="Recall (macro)" value={pct(modelInfo?.recall)} icon={Activity} accent="lav" />
        <MetricCard label="F1 score (macro)" value={pct(modelInfo?.f1)} icon={Award} accent="coral" />
      </div>

      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        <MetricCard label="Total predictions" value={summary?.total_predictions ?? "—"} />
        <MetricCard label="Average confidence" value={pct(summary?.average_confidence)} />
        <MetricCard label="Most recognized" value={summary?.most_recognized_character ?? "—"} />
      </div>

      <div className="mt-10 rounded-xl2 border border-navy/5 bg-surface p-6 shadow-soft">
        <h2 className="font-display font-semibold text-navy">Class distribution</h2>
        <p className="mt-1 text-sm text-navy-soft">Images per class in the training dataset.</p>
        <div className="mt-4 h-80">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#EAF0FF" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#8790B3" }} />
                <YAxis tick={{ fontSize: 11, fill: "#8790B3" }} />
                <Tooltip
                  contentStyle={{ borderRadius: 12, border: "1px solid #EAF0FF", fontSize: 12 }}
                />
                <Bar dataKey="count" fill="#5B7FDE" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState text="Dataset report not found yet. Run dataset_inspector.py on the backend." />
          )}
        </div>
      </div>

      <div className="mt-10 rounded-xl2 border border-navy/5 bg-surface p-6 shadow-soft">
        <h2 className="font-display font-semibold text-navy">Recent predictions</h2>
        {summary?.recent_predictions?.length ? (
          <table className="mt-4 w-full text-left text-sm">
            <thead>
              <tr className="text-xs uppercase tracking-normal text-mist">
                <th className="pb-2 font-medium">Character</th>
                <th className="pb-2 font-medium">Confidence</th>
                <th className="pb-2 font-medium">Time</th>
              </tr>
            </thead>
            <tbody>
              {summary.recent_predictions.map((p, i) => (
                <tr key={i} className="border-t border-navy/5">
                  <td className="py-2 font-display font-semibold text-navy">{p.predicted_class}</td>
                  <td className="py-2 text-navy-soft">{(p.confidence * 100).toFixed(1)}%</td>
                  <td className="py-2 text-mist">{p.timestamp ? new Date(p.timestamp).toLocaleTimeString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <EmptyState text="No predictions logged yet — try the Live Recognition page." />
        )}
      </div>
    </div>
  );
}

function EmptyState({ text }) {
  return (
    <div className="flex h-full items-center justify-center text-center text-sm text-mist">
      {text}
    </div>
  );
}
