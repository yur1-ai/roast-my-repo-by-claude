import { useParams } from "react-router-dom";

export default function RoastPage() {
  const { id } = useParams<{ id: string }>();
  return (
    <div className="text-center">
      <h1 className="text-2xl font-bold">Roast: {id}</h1>
      <p className="text-muted-foreground mt-2">Loading roast results...</p>
    </div>
  );
}
