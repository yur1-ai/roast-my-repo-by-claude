import { BrowserRouter, Route, Routes } from "react-router-dom";
import Layout from "@/components/Layout";
import HomePage from "@/pages/HomePage";
import RoastPage from "@/pages/RoastPage";
import FeedPage from "@/pages/FeedPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/roast/:id" element={<RoastPage />} />
          <Route path="/feed" element={<FeedPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
