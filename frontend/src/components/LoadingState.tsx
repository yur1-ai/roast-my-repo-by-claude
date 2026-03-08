import { Card } from "@/components/ui/card";

interface LoadingStateProps {
  status: string;
}

const STATUS_TEXT: Record<string, { text: string; icon: string }> = {
  pending: { text: "Queueing your roast...", icon: "\u23F3" },
  analyzing: { text: "Scanning the codebase...", icon: "\U0001F440" },
  roasting: { text: "Generating burns...", icon: "\U0001F525" },
};

export default function LoadingState({ status }: LoadingStateProps) {
  const info = STATUS_TEXT[status] || STATUS_TEXT.pending;

  return (
    <div className="flex items-center justify-center min-h-[40vh]">
      <Card className="p-8 text-center space-y-4 max-w-sm w-full">
        <div className={`text-5xl ${status === "roasting" ? "animate-bounce" : "animate-pulse"}`}>
          {info.icon}
        </div>
        <p className="text-lg font-medium">{info.text}</p>
        <div className="flex justify-center gap-1">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 bg-primary rounded-full animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
      </Card>
    </div>
  );
}
