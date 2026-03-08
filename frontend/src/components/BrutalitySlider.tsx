import { Slider } from "@/components/ui/slider";
import { BRUTALITY_LABELS } from "@/lib/constants";

interface BrutalitySliderProps {
  value: number;
  onChange: (value: number) => void;
}

export default function BrutalitySlider({ value, onChange }: BrutalitySliderProps) {
  const current = BRUTALITY_LABELS[value - 1];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">Brutality Level</span>
        <span className="text-lg font-medium">
          {current.emoji} {current.label}
        </span>
      </div>
      <Slider
        value={[value]}
        onValueChange={(v) => onChange(Array.isArray(v) ? v[0] : v)}
        min={1}
        max={5}
        step={1}
        className="w-full"
      />
      <div className="flex justify-between text-xs text-muted-foreground">
        {BRUTALITY_LABELS.map((b) => (
          <span key={b.level}>{b.emoji}</span>
        ))}
      </div>
    </div>
  );
}
