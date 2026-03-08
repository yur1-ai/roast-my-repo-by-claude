import CategorySection from "@/components/CategorySection";
import GradeBadge from "@/components/GradeBadge";
import RepoMeta from "@/components/RepoMeta";
import ScoreBadge from "@/components/ScoreBadge";
import ShareButtons from "@/components/ShareButtons";
import TopBurns from "@/components/TopBurns";
import type { RoastResponse } from "@/types/roast";

interface RoastResultCardProps {
  roast: RoastResponse;
}

export default function RoastResultCard({ roast }: RoastResultCardProps) {
  if (!roast.roast_result || !roast.repo_metadata) return null;

  const { roast_result, repo_metadata } = roast;

  return (
    <div className="space-y-8">
      <RepoMeta owner={roast.repo_owner} name={roast.repo_name} metadata={repo_metadata} />

      <div className="flex items-center justify-center gap-6">
        <ScoreBadge score={roast_result.overall_score} size="lg" />
        <GradeBadge grade={roast_result.letter_grade} size="lg" />
      </div>

      <p className="text-center text-lg text-foreground/90 max-w-2xl mx-auto">
        {roast_result.summary}
      </p>

      <div>
        <h3 className="text-lg font-semibold mb-3">Top Burns 🔥</h3>
        <TopBurns burns={roast_result.top_burns} />
      </div>

      <div className="space-y-3">
        <h3 className="text-lg font-semibold">Categories</h3>
        {roast_result.categories.map((cat) => (
          <CategorySection key={cat.name} category={cat} />
        ))}
      </div>

      <div className="flex justify-center">
        <ShareButtons
          repoName={`${roast.repo_owner}/${roast.repo_name}`}
          score={roast_result.overall_score}
          grade={roast_result.letter_grade}
        />
      </div>
    </div>
  );
}
