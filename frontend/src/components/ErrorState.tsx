import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex items-center justify-center min-h-[30vh]">
      <Card className="p-8 text-center space-y-4 max-w-sm w-full">
        <div className="text-4xl">💥</div>
        <p className="text-lg font-medium text-destructive">Something went wrong</p>
        <p className="text-sm text-muted-foreground">{message}</p>
        {onRetry && (
          <Button variant="secondary" onClick={onRetry}>
            Try Again
          </Button>
        )}
      </Card>
    </div>
  );
}
