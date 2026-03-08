import { useState } from "react";
import { Card } from "@/components/ui/card";
import { getScoreStrokeColor } from "@/lib/constants";
import type { RoastCategory } from "@/types/roast";

interface CategorySectionProps {
  category: RoastCategory;
  defaultOpen?: boolean;
}

export default function CategorySection({ category, defaultOpen = true }: CategorySectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const barColor = getScoreStrokeColor(category.score);

  return (
    <Card className="overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-4 flex items-center gap-3 hover:bg-accent/50 transition-colors text-left"
      >
        <span className="text-xl">{category.emoji}</span>
        <span className="font-medium flex-1">{category.name}</span>
        <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{ width: `${category.score}%`, backgroundColor: barColor }}
          />
        </div>
        <span className="text-sm font-mono w-8 text-right">{category.score}</span>
        <span className="text-muted-foreground text-sm">{isOpen ? "▲" : "▼"}</span>
      </button>
      {isOpen && (
        <div className="px-4 pb-4 space-y-3 border-t border-border pt-3">
          <p className="text-sm text-foreground/90 whitespace-pre-line">{category.roast}</p>
          {category.suggestions.length > 0 && (
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-1">Suggestions:</p>
              <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                {category.suggestions.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
