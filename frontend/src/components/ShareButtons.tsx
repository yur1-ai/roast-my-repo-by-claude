import { useState } from "react";
import { Button } from "@/components/ui/button";

interface ShareButtonsProps {
  repoName: string;
  score: number;
  grade: string;
}

export default function ShareButtons({ repoName, score, grade }: ShareButtonsProps) {
  const [copied, setCopied] = useState(false);

  function copyLink() {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  const shareText = `My repo ${repoName} got a ${grade} (${score}/100) on RoastMyRepo! Check it out:`;

  return (
    <div className="flex gap-3">
      <Button variant="secondary" onClick={copyLink}>
        {copied ? "Copied!" : "Copy Link"}
      </Button>
      <Button
        variant="secondary"
        onClick={() => {
          const url = `https://x.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(window.location.href)}`;
          window.open(url, "_blank", "noopener");
        }}
      >
        Share on X
      </Button>
    </div>
  );
}
