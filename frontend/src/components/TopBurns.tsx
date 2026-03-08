import { Card } from "@/components/ui/card";

interface TopBurnsProps {
  burns: string[];
}

export default function TopBurns({ burns }: TopBurnsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
      {burns.map((burn, i) => (
        <Card key={i} className="p-4 bg-card border-primary/20">
          <p className="text-sm italic text-foreground">&ldquo;{burn}&rdquo;</p>
        </Card>
      ))}
    </div>
  );
}
