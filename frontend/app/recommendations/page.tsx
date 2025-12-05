"use client";

import { useEffect, useState } from "react";
import styles from "../dashboard/page.module.css";

type RecommendedMovie = {
  movie_id: string;
  title: string;
  description?: string;
  imdb_rating?: number;
  meta_score?: number;
  release_date?: string;
  genres?: string[];
  directors?: string[];
  main_stars?: string[];
  recommendation_reason: string;
  recommendation_score?: number;
};

type ApiError = {
  message?: string;
  detail?: string;
};

type RecommendationsResponse = {
  user_id: string;
  recommendations: RecommendedMovie[];
  recommendation_type: string;
  total_count: number;
  error?: ApiError;
};

type Status = "loading" | "ready" | "error";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<RecommendedMovie[]>([]);
  const [status, setStatus] = useState<Status>("loading");
  const [message, setMessage] = useState("");
  const [recommendationType, setRecommendationType] = useState("hybrid");
  const [limit, setLimit] = useState(20);

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const loadRecommendations = async () => {
    if (!token) {
      setStatus("error");
      setMessage("Please log in to view recommendations.");
      return;
    }
    setStatus("loading");
    setMessage("");
    try {
      const params = new URLSearchParams();
      params.set("recommendation_type", recommendationType);
      params.set("limit", limit.toString());

      const response = await fetch(`${apiBase}/recommendations/?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data: RecommendationsResponse = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.error?.detail || "Could not load recommendations.");
      }
      setRecommendations(data.recommendations || []);
      setStatus("ready");
      if (data.recommendations.length === 0) {
        setMessage("No recommendations available. Try reviewing more movies or adding friends!");
      }
    } catch (error: any) {
      setStatus("error");
      setMessage(error?.message || "Could not load recommendations.");
    }
  };

  useEffect(() => {
    loadRecommendations();
  }, [recommendationType, limit]);

  const addToWatchlist = async (movieId: string) => {
    if (!token) {
      setMessage("You must be logged in to manage your watchlist.");
      return;
    }
    try {
      const response = await fetch(`${apiBase}/movies/watch-later`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ movie_id: movieId, action: "add" }),
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not update watchlist.");
      }
      setMessage("Movie added to watchlist!");
      setTimeout(() => setMessage(""), 3000);
    } catch (error: any) {
      setMessage(error?.message || "Could not update watchlist.");
    }
  };

  const getRecommendationTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      hybrid: "Hybrid (All Methods)",
      content_based: "Content-Based",
      collaborative: "Collaborative",
      friend_based: "Friend-Based",
      popular: "Popular",
    };
    return labels[type] || type;
  };

  const formatScore = (score?: number) => {
    if (score === undefined || score === null) return "";
    return `${Math.round(score * 100)}% match`;
  };

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.header}>
          <div>
            <p className={styles.kicker}>Recommendations</p>
            <h1 className={styles.title}>Movies for You</h1>
            <p className={styles.meta}>
              Personalized movie recommendations based on your preferences, reviews, and friends.
            </p>
          </div>
          <div className={styles.headerActions}>
            <button
              className={styles.secondary}
              type="button"
              onClick={() => (window.location.href = "/dashboard")}
            >
              Back to dashboard
            </button>
          </div>
        </div>

        {message && (
          <div className={styles.alert} style={{ color: message.includes("added") ? "green" : undefined }}>
            {message}
          </div>
        )}

        <div className={styles.card}>
          <p className={styles.sectionLabel}>Recommendation Settings</p>
          <div className={styles.formRow}>
            <select
              className={styles.select}
              value={recommendationType}
              onChange={(e) => setRecommendationType(e.target.value)}
            >
              <option value="hybrid">Hybrid (All Methods)</option>
              <option value="content_based">Content-Based</option>
              <option value="collaborative">Collaborative</option>
              <option value="friend_based">Friend-Based</option>
              <option value="popular">Popular</option>
            </select>
            <select
              className={styles.select}
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
            >
              <option value="10">10 recommendations</option>
              <option value="20">20 recommendations</option>
              <option value="30">30 recommendations</option>
              <option value="50">50 recommendations</option>
            </select>
            <button className={styles.primary} type="button" onClick={loadRecommendations}>
              Refresh
            </button>
          </div>
          <p className={styles.meta} style={{ marginTop: "0.5rem" }}>
            Current: {getRecommendationTypeLabel(recommendationType)}
          </p>
        </div>

        <div className={styles.main}>
          {status === "loading" ? (
            <div className={styles.card}>
              <p className={styles.titleSm}>Loading recommendations…</p>
            </div>
          ) : status === "error" ? (
            <div className={styles.card}>
              <p className={styles.lede} style={{ color: "red" }}>{message}</p>
            </div>
          ) : recommendations.length ? (
            recommendations.map((movie) => (
              <div className={styles.card} key={movie.movie_id}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div style={{ flex: 1 }}>
                    <p className={styles.titleSm}>{movie.title}</p>
                    {movie.release_date && (
                      <p className={styles.meta}>Released: {movie.release_date}</p>
                    )}
                    {movie.description && (
                      <p className={styles.lede} style={{ marginTop: "0.5rem" }}>
                        {movie.description}
                      </p>
                    )}
                    <div style={{ marginTop: "0.75rem", display: "flex", gap: "1rem", flexWrap: "wrap" }}>
                      {movie.imdb_rating && (
                        <p className={styles.meta}>IMDB: {movie.imdb_rating.toFixed(1)}</p>
                      )}
                      {movie.meta_score && <p className={styles.meta}>Meta: {movie.meta_score}</p>}
                      {movie.genres && movie.genres.length > 0 && (
                        <p className={styles.meta}>Genres: {movie.genres.join(", ")}</p>
                      )}
                    </div>
                    {movie.directors && movie.directors.length > 0 && (
                      <p className={styles.meta} style={{ marginTop: "0.5rem" }}>
                        Directors: {movie.directors.join(", ")}
                      </p>
                    )}
                    <div
                      style={{
                        marginTop: "0.75rem",
                        padding: "0.5rem",
                        backgroundColor: "#f0f0f0",
                        borderRadius: "4px",
                      }}
                    >
                      <p className={styles.meta} style={{ fontWeight: "bold", marginBottom: "0.25rem" }}>
                        Why recommended:
                      </p>
                      <p className={styles.meta}>{movie.recommendation_reason}</p>
                      {movie.recommendation_score !== undefined && (
                        <p className={styles.meta} style={{ marginTop: "0.25rem", fontStyle: "italic" }}>
                          {formatScore(movie.recommendation_score)}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
                <div className={styles.buttonRow} style={{ marginTop: "1rem" }}>
                  <button
                    className={styles.primary}
                    type="button"
                    onClick={() => addToWatchlist(movie.movie_id)}
                  >
                    Add to Watchlist
                  </button>
                  <button
                    className={styles.secondary}
                    type="button"
                    onClick={() => (window.location.href = `/movies?query=${encodeURIComponent(movie.title)}`)}
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className={styles.card}>
              <p className={styles.lede}>No recommendations available.</p>
              <p className={styles.meta} style={{ marginTop: "0.5rem" }}>
                Try reviewing more movies, adding movies to your watchlist, or adding friends to get
                recommendations!
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

