const BASE_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch (_) {
      /* ignore parse error */
    }
    const error = new Error(detail);
    error.status = res.status;
    throw error;
  }
  return res.json();
}

export const api = {
  health: () => request("/health"),
  modelInfo: () => request("/model-info"),
  datasetInfo: () => request("/dataset-info"),

  predictStatic: (sessionId, imageBase64, confidenceThreshold) =>
    request("/predict/static", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        image_base64: imageBase64,
        confidence_threshold: confidenceThreshold ?? null,
      }),
    }),

  sentenceCreate: () => request("/sentence/create", { method: "POST" }),
  sentenceAdd: (sessionId, character) =>
    request("/sentence/add", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, character }),
    }),
  sentenceSpace: (sessionId) =>
    request("/sentence/space", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId }),
    }),
  sentenceBackspace: (sessionId) =>
    request("/sentence/backspace", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId }),
    }),
  sentenceClear: (sessionId) =>
    request("/sentence/clear", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId }),
    }),
  sentenceGet: (sessionId) => request(`/sentence/${sessionId}`),

  speak: (text) =>
    request("/speak", { method: "POST", body: JSON.stringify({ text }) }),

  analytics: () => request("/analytics"),
  analyticsPredictions: () => request("/analytics/predictions"),
  analyticsClasses: () => request("/analytics/classes"),
};

export default api;
