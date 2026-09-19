import { useEffect, useRef, useState } from "react";
import { Video, VideoOff } from "lucide-react";

/**
 * Renders a webcam feed and periodically emits a base64 JPEG frame via
 * onFrame(base64). Throttled with `intervalMs` so we don't hammer the
 * backend with inference requests on every browser frame.
 */
export default function Webcam({ onFrame, intervalMs = 350, active = true, handBox = null, handLandmarks = null }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const [cameraOn, setCameraOn] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function start() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480, facingMode: "user" },
          audio: false,
        });
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        setCameraOn(true);
        setError(null);
      } catch (err) {
        setError(err.message || "Could not access camera.");
        setCameraOn(false);
      }
    }

    if (active) start();

    return () => {
      cancelled = true;
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, [active]);

  useEffect(() => {
    if (!active || !cameraOn) return;
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext("2d");

    const id = setInterval(() => {
      if (!video || video.readyState < 2) return;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const base64 = canvas.toDataURL("image/jpeg", 0.8);
      onFrame?.(base64);
    }, intervalMs);

    return () => clearInterval(id);
  }, [active, cameraOn, intervalMs, onFrame]);

  return (
    <div className="relative overflow-hidden rounded-xl2 bg-navy shadow-soft">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="aspect-[4/3] w-full scale-x-[-1] object-cover"
      />
      <canvas ref={canvasRef} className="hidden" />

      {handBox && (
        <div
          className="pointer-events-none absolute rounded-lg border-4"
          style={{
            left: `${handBox.leftPct}%`,
            top: `${handBox.topPct}%`,
            width: `${handBox.widthPct}%`,
            height: `${handBox.heightPct}%`,
            borderColor: '#00FF00',
          }}
        />
      )}

      {handLandmarks && <HandTrace landmarks={handLandmarks} />}

      <div className="absolute left-3 top-3 flex items-center gap-1.5 rounded-full bg-navy/70 px-3 py-1.5 text-xs font-medium text-white backdrop-blur">
        {cameraOn ? (
          <>
            <Video size={13} className="text-mint" /> Camera active
          </>
        ) : (
          <>
            <VideoOff size={13} className="text-coral" /> Camera off
          </>
        )}
      </div>

      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-navy/90 p-6 text-center text-sm text-white">
          {error}. Check your browser's camera permissions and reload.
        </div>
      )}
    </div>
  );
}

const HAND_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4],
  [0, 5], [5, 6], [6, 7], [7, 8],
  [5, 9], [9, 10], [10, 11], [11, 12],
  [9, 13], [13, 14], [14, 15], [15, 16],
  [13, 17], [17, 18], [18, 19], [19, 20], [0, 17],
];

function HandTrace({ landmarks }) {
  return (
    <svg 
      className="pointer-events-none absolute inset-0 h-full w-full" 
      viewBox="0 0 1 1" 
      preserveAspectRatio="none"
      style={{ overflow: 'visible' }}
    >
      {landmarks.map((hand, handIndex) => (
        <g key={handIndex}>
          {/* Connection lines - draw first so they appear behind dots */}
          {HAND_CONNECTIONS.map(([start, end], idx) => {
            const x1 = 1 - hand[start][0];
            const y1 = hand[start][1];
            const x2 = 1 - hand[end][0];
            const y2 = hand[end][1];
            
            return (
              <g key={`line-${idx}`}>
                {/* White line only */}
                <line
                  x1={x1} y1={y1}
                  x2={x2} y2={y2}
                  stroke="#FFFFFF" 
                  strokeWidth="0.008"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </g>
            );
          })}
          
          {/* Landmark points */}
          {hand.map(([x, y], index) => {
            const cx = 1 - x;
            const cy = y;
            return (
              <g key={`dot-${index}`}>
                {/* Outer white circle (border) */}
                <circle cx={cx} cy={cy} r="0.012" fill="#FFFFFF" />
                {/* Inner red dot */}
                <circle cx={cx} cy={cy} r="0.007" fill="#FF3333" />
              </g>
            );
          })}
        </g>
      ))}
    </svg>
  );
}