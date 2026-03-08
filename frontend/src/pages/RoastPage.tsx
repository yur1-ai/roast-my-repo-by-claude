import { useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import RoastResultCard from "@/components/RoastResultCard";
import { useRoastPolling } from "@/hooks/useRoastPolling";

export default function RoastPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { roast, error } = useRoastPolling(id);

  if (error) {
    return <ErrorState message={error} onRetry={() => navigate("/")} />;
  }

  if (!roast) {
    return <LoadingState status="pending" />;
  }

  if (roast.status === "failed") {
    return (
      <div className="text-center space-y-4 py-12">
        <div className="text-4xl">💥</div>
        <p className="text-lg font-medium text-destructive">Roast Failed</p>
        <p className="text-sm text-muted-foreground">{roast.error_message || "Something went wrong"}</p>
        <Button variant="secondary" onClick={() => navigate("/")}>Try Again</Button>
      </div>
    );
  }

  if (roast.status !== "complete") {
    return <LoadingState status={roast.status} />;
  }

  return <RoastResultCard roast={roast} />;
}
