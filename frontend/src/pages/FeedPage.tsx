import { Button } from "@/components/ui/button";
import ErrorState from "@/components/ErrorState";
import RoastFeedCard from "@/components/RoastFeedCard";
import { useFeed } from "@/hooks/useFeed";

export default function FeedPage() {
  const { roasts, isLoading, error, hasMore, loadMore } = useFeed();

  if (error && roasts.length === 0) {
    return <ErrorState message={error} onRetry={loadMore} />;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Roast Feed 🔥</h1>

      {roasts.length === 0 && !isLoading ? (
        <p className="text-muted-foreground text-center py-12">No roasts yet. Be the first!</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {roasts.map((roast) => (
            <RoastFeedCard key={roast.id} roast={roast} />
          ))}
        </div>
      )}

      {hasMore && (
        <div className="text-center">
          <Button variant="secondary" onClick={loadMore} disabled={isLoading}>
            {isLoading ? "Loading..." : "Load More"}
          </Button>
        </div>
      )}
    </div>
  );
}
