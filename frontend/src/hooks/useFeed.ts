import { useCallback, useEffect, useState } from "react";
import { getRecentRoasts } from "@/api/client";
import type { RoastFeedItem } from "@/types/roast";

export function useFeed() {
  const [roasts, setRoasts] = useState<RoastFeedItem[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const limit = 20;

  const loadMore = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getRecentRoasts(limit, offset);
      setRoasts((prev) => (offset === 0 ? data.roasts : [...prev, ...data.roasts]));
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load feed");
    } finally {
      setIsLoading(false);
    }
  }, [offset]);

  useEffect(() => {
    loadMore();
  }, [loadMore]);

  function handleLoadMore() {
    setOffset((prev) => prev + limit);
  }

  const hasMore = roasts.length < total;

  return { roasts, total, isLoading, error, hasMore, loadMore: handleLoadMore };
}
