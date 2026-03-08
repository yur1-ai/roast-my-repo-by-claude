import { Badge } from "@/components/ui/badge";
import type { RepoMetadata } from "@/types/roast";

interface RepoMetaProps {
  owner: string;
  name: string;
  metadata: RepoMetadata;
}

export default function RepoMeta({ owner, name, metadata }: RepoMetaProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <h2 className="text-xl font-bold">
        {owner}/{name}
      </h2>
      {metadata.language && (
        <Badge variant="secondary">{metadata.language}</Badge>
      )}
      <span className="text-sm text-muted-foreground">
        {metadata.stars.toLocaleString()} stars
      </span>
      <span className="text-sm text-muted-foreground">
        {metadata.forks.toLocaleString()} forks
      </span>
    </div>
  );
}
