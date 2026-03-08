import { useCallback, useEffect, useRef, useState } from "react";
import { getRoast } from "@/api/client";
import type { RoastResponse } from "@/types/roast";

export function useRoastPolling(id: string | undefined) {
  const [roast, setRoast] = useState<RoastResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!id) return;

    let cancelled = false;

    async function poll() {
      try {
        const data = await getRoast(id!);
        if (cancelled) return;
        setRoast(data);

        if (data.status === "complete" || data.status === "failed") {
          stopPolling();
        }
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Failed to load roast");
        stopPolling();
      }
    }

    // Initial fetch
    poll();

    // Start polling
    intervalRef.current = setInterval(poll, 2000);

    return () => {
      cancelled = true;
      stopPolling();
    };
  }, [id, stopPolling]);

  return { roast, error };
}
