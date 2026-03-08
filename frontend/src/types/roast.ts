export interface RepoMetadata {
  stars: number;
  forks: number;
  language: string | null;
  size_kb: number;
  open_issues: number;
  description: string | null;
  topics: string[];
  default_branch: string;
  last_push: string;
  has_wiki: boolean;
  license: string | null;
}

export interface RoastCategory {
  name: string;
  score: number;
  emoji: string;
  roast: string;
  suggestions: string[];
}

export interface RoastResult {
  overall_score: number;
  letter_grade: string;
  summary: string;
  top_burns: string[];
  categories: RoastCategory[];
}

export interface RoastResponse {
  id: string;
  status: "pending" | "analyzing" | "roasting" | "complete" | "failed";
  repo_url: string;
  repo_owner: string;
  repo_name: string;
  brutality_level: number;
  error_message: string | null;
  repo_metadata: RepoMetadata | null;
  roast_result: RoastResult | null;
  overall_score: number | null;
  letter_grade: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface RoastSubmitResponse {
  id: string;
  status: string;
  repo_url: string;
  repo_owner: string;
  repo_name: string;
  brutality_level: number;
  created_at: string;
}

export interface RoastFeedItem {
  id: string;
  repo_url: string;
  repo_owner: string;
  repo_name: string;
  brutality_level: number;
  overall_score: number;
  letter_grade: string;
  top_burns: string[];
  repo_metadata: RepoMetadata;
  completed_at: string;
}

export interface RoastFeedResponse {
  roasts: RoastFeedItem[];
  total: number;
  limit: number;
  offset: number;
}
