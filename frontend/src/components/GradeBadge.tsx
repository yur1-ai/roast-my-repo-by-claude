import { GRADE_COLORS } from "@/lib/constants";

interface GradeBadgeProps {
  grade: string;
  size?: "sm" | "lg";
}

export default function GradeBadge({ grade, size = "lg" }: GradeBadgeProps) {
  const bg = GRADE_COLORS[grade] || "bg-gray-600";
  const sizeClass = size === "lg" ? "w-16 h-16 text-3xl" : "w-8 h-8 text-sm";

  return (
    <div className={`${bg} ${sizeClass} rounded-lg flex items-center justify-center font-bold text-white`}>
      {grade}
    </div>
  );
}
