import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card } from "@/components/ui/card";
import RoastFeedCard from "@/components/RoastFeedCard";
import RoastForm from "@/components/RoastForm";
import { getRecentRoasts } from "@/api/client";
import type { RoastFeedItem } from "@/types/roast";

export default function HomePage() {
  const [recentRoasts, setRecentRoasts] = useState<RoastFeedItem[]>([]);

  useEffect(() => {
    getRecentRoasts(5, 0)
      .then((data) => setRecentRoasts(data.roasts))
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-12">
      <div className="text-center space-y-3 pt-8">
        <h1 className="text-5xl font-bold">RoastMyRepo 🔥</h1>
        <p className="text-xl text-muted-foreground">Get your code brutally reviewed by AI</p>
      </div>

      <Card className="p-6 max-w-lg mx-auto">
        <RoastForm />
      </Card>

      {recentRoasts.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Recent Roasts</h2>
            <Link to="/feed" className="text-sm text-primary hover:underline">
              See all →
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {recentRoasts.map((roast) => (
              <RoastFeedCard key={roast.id} roast={roast} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
