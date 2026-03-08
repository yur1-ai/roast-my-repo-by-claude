export const BRUTALITY_LABELS = [
  { level: 1, emoji: "\u{1F60A}", label: "Gentle" },
  { level: 2, emoji: "\u{1F60F}", label: "Constructive" },
  { level: 3, emoji: "\u{1F624}", label: "Honest" },
  { level: 4, emoji: "\u{1F480}", label: "Brutal" },
  { level: 5, emoji: "\u{1FAA6}", label: "Savage" },
] as const;

export const GRADE_COLORS: Record<string, string> = {
  S: "bg-purple-600",
  A: "bg-green-600",
  B: "bg-blue-600",
  C: "bg-yellow-600",
  D: "bg-orange-600",
  F: "bg-red-600",
};

export const SCORE_COLORS = {
  high: "text-green-400",
  medium: "text-yellow-400",
  low: "text-orange-400",
  critical: "text-red-400",
} as const;

export function getScoreColor(score: number): string {
  if (score >= 80) return SCORE_COLORS.high;
  if (score >= 60) return SCORE_COLORS.medium;
  if (score >= 40) return SCORE_COLORS.low;
  return SCORE_COLORS.critical;
}

export function getScoreStrokeColor(score: number): string {
  if (score >= 80) return "#4ade80";
  if (score >= 60) return "#facc15";
  if (score >= 40) return "#fb923c";
  return "#f87171";
}
