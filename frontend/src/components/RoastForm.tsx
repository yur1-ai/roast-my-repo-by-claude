import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import BrutalitySlider from "@/components/BrutalitySlider";
import { useSubmitRoast } from "@/hooks/useSubmitRoast";

const URL_PATTERN = /^https:\/\/github\.com\/[a-zA-Z0-9\-_.]+\/[a-zA-Z0-9\-_.]+\/?$/;

export default function RoastForm() {
  const [url, setUrl] = useState("");
  const [brutality, setBrutality] = useState(3);
  const [urlError, setUrlError] = useState<string | null>(null);
  const { submit, isSubmitting, error } = useSubmitRoast();

  function validateUrl(value: string) {
    if (!value) {
      setUrlError(null);
      return;
    }
    if (!URL_PATTERN.test(value)) {
      setUrlError("Please enter a valid GitHub URL (https://github.com/owner/repo)");
    } else {
      setUrlError(null);
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!URL_PATTERN.test(url)) {
      setUrlError("Please enter a valid GitHub URL");
      return;
    }
    submit(url, brutality);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <Input
          type="url"
          placeholder="https://github.com/owner/repo"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onBlur={() => validateUrl(url)}
          className="text-base h-12"
        />
        {urlError && <p className="text-sm text-destructive mt-1">{urlError}</p>}
      </div>

      <BrutalitySlider value={brutality} onChange={setBrutality} />

      <Button type="submit" className="w-full h-12 text-base font-semibold" disabled={isSubmitting}>
        {isSubmitting ? "Submitting..." : "Roast It 🔥"}
      </Button>

      {error && <p className="text-sm text-destructive text-center">{error}</p>}
    </form>
  );
}
