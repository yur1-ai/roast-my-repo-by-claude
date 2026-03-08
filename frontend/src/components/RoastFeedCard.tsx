import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import GradeBadge from "@/components/GradeBadge";
import ScoreBadge from "@/components/ScoreBadge";
import { BRUTALITY_LABELS } from "@/lib/constants";
import type { RoastFeedItem } from "@/types/roast";

interface RoastFeedCardProps {
  roast: RoastFeedItem;
}

export default function RoastFeedCard({ roast }: RoastFeedCardProps) {
  const brutality = BRUTALITY_LABELS[roast.brutality_level - 1];

  return (
    <Link to={`/roast/${roast.id}`}>
      <Card className="p-4 hover:border-primary/50 transition-colors cursor-pointer h-full">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="font-medium">{roast.repo_owner}/{roast.repo_name}</h3>
            <div className="flex items-center gap-2 mt-1">
              {roast.repo_metadata.language && (
                <Badge variant="secondary" className="text-xs">{roast.repo_metadata.language}</Badge>
              )}
              <span className="text-xs text-muted-foreground">{brutality.emoji} {brutality.label}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ScoreBadge score={roast.overall_score} size="sm" />
            <GradeBadge grade={roast.letter_grade} size="sm" />
          </div>
        </div>
        {roast.top_burns[0] && (
          <p className="text-xs text-muted-foreground italic truncate">
            &ldquo;{roast.top_burns[0]}&rdquo;
          </p>
        )}
      </Card>
    </Link>
  );
}
