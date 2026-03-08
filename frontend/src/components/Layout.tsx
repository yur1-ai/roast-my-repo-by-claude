import { Link, Outlet } from "react-router-dom";

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <nav className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur">
        <div className="mx-auto max-w-5xl flex items-center justify-between px-4 h-14">
          <Link to="/" className="text-xl font-bold text-foreground hover:text-primary transition-colors">
            RoastMyRepo 🔥
          </Link>
          <Link to="/feed" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Feed
          </Link>
        </div>
      </nav>

      <main className="flex-1 mx-auto w-full max-w-5xl px-4 py-8">
        <Outlet />
      </main>

      <footer className="border-t border-border py-6 text-center text-sm text-muted-foreground">
        Built to test agentic coding tools
      </footer>
    </div>
  );
}
