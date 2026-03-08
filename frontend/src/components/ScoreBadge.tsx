import { useEffect, useState } from "react";
import { getScoreStrokeColor } from "@/lib/constants";

interface ScoreBadgeProps {
  score: number;
  size?: "sm" | "lg";
}

export default function ScoreBadge({ score, size = "lg" }: ScoreBadgeProps) {
  const [displayScore, setDisplayScore] = useState(0);
  const dimensions = size === "lg" ? 120 : 60;
  const strokeWidth = size === "lg" ? 8 : 4;
  const radius = (dimensions - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (displayScore / 100) * circumference;
  const color = getScoreStrokeColor(score);

  useEffect(() => {
    let frame: number;
    const duration = 800;
    const start = performance.now();

    function animate(now: number) {
      const elapsed = now - start;
      const t = Math.min(elapsed / duration, 1);
      setDisplayScore(Math.round(t * score));
      if (t < 1) frame = requestAnimationFrame(animate);
    }

    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [score]);

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: dimensions, height: dimensions }}>
      <svg width={dimensions} height={dimensions} className="-rotate-90">
        <circle
          cx={dimensions / 2}
          cy={dimensions / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-muted/30"
        />
        <circle
          cx={dimensions / 2}
          cy={dimensions / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          className="transition-all duration-700"
        />
      </svg>
      <span className={`absolute font-bold ${size === "lg" ? "text-3xl" : "text-sm"}`}>
        {displayScore}
      </span>
    </div>
  );
}
