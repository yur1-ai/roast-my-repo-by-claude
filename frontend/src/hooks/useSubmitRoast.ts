import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { submitRoast } from "@/api/client";

export function useSubmitRoast() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(repoUrl: string, brutalityLevel: number) {
    setIsSubmitting(true);
    setError(null);

    try {
      const result = await submitRoast(repoUrl, brutalityLevel);
      navigate(`/roast/${result.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsSubmitting(false);
    }
  }

  return { submit, isSubmitting, error };
}
