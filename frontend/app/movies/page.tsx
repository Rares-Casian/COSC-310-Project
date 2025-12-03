"use client";

import { useEffect, useMemo, useState } from "react";
import styles from "../dashboard/page.module.css";

type Movie = {
  movie_id: string;
  title: string;
  description?: string;
  imdb_rating?: number;
  meta_score?: number;
  release_date?: string;
};

type Status = "idle" | "loading" | "error";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function MoviesPage() {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");
  const [messageTone, setMessageTone] = useState<"info" | "error" | "success">("info");
  const [query, setQuery] = useState("");
  const [genre, setGenre] = useState("");
  const [director, setDirector] = useState("");
  const [star, setStar] = useState("");
  const [minRating, setMinRating] = useState("");
  const [maxRating, setMaxRating] = useState("");
  const [minYear, setMinYear] = useState("");
  const [maxYear, setMaxYear] = useState("");
  const [sortBy, setSortBy] = useState("title");
  const [order, setOrder] = useState<"asc" | "desc">("asc");
  const [isDownloading, setIsDownloading] = useState(false);

  const token = useMemo(
    () => (typeof window !== "undefined" ? localStorage.getItem("access_token") : null),
    []
  );

  const fetchMovies = async () => {
    setStatus("loading");
    setMessage("");
    setMessageTone("info");
    try {
      const params = new URLSearchParams();
      if (query) params.set("query", query);
      if (genre) params.set("genre", genre);
      if (director) params.set("director", director);
      if (star) params.set("star", star);
      if (minRating) params.set("min_rating", minRating);
      if (maxRating) params.set("max_rating", maxRating);
      if (minYear) params.set("min_year", minYear);
      if (maxYear) params.set("max_year", maxYear);
      params.set("sort_by", sortBy);
      params.set("order", order);

      const response = await fetch(`${apiBase}/movies/${params.toString() ? `?${params}` : ""}`);
      const data: Movie[] = await response.json().catch(() => []);
      if (!response.ok) {
        throw new Error("Could not load movies.");
      }
      setMovies(data);
      setStatus("idle");
    } catch (error: any) {
      setStatus("error");
      setMessage(error?.message || "Failed to load movies.");
      setMessageTone("error");
    }
  };

  useEffect(() => {
    fetchMovies();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const updateWatchLater = async (movieId: string) => {
    if (!token) {
      setMessage("You must be logged in to manage your watchlist.");
      setMessageTone("error");
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
      setMessage(data?.message || "Movie added to watchlist.");
      setMessageTone("success");
    } catch (error: any) {
      setMessage(error?.message || "Could not update watchlist.");
      setMessageTone("error");
    }
  };

  const downloadMovies = async () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (!token) {
      setMessage("You must be logged in as admin to download movies.");
      setMessageTone("error");
      return;
    }
    setIsDownloading(true);
    setMessage("");
    try {
      const response = await fetch(`${apiBase}/movies/download`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.error?.message || data?.detail || "Download failed.");
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "movies.json";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setMessage("Movies downloaded.");
      setMessageTone("success");
    } catch (error: any) {
      setMessage(error?.message || "Could not download movies.");
      setMessageTone("error");
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.header}>
          <div>
            <p className={styles.kicker}>Movies</p>
            <h1 className={styles.title}>Browse movies</h1>
            <p className={styles.meta}>Search and add items to your watchlist.</p>
          </div>
          <div className={styles.headerActions}>
            <input
              className={styles.input}
              aria-label="Search movies"
              placeholder="Search..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button className={styles.primary} type="button" onClick={fetchMovies}>
              Search
            </button>
            <button className={styles.secondary} type="button" onClick={() => (window.location.href = "/dashboard")}>
              Back to dashboard
            </button>
            <button className={styles.secondary} type="button" onClick={downloadMovies} disabled={isDownloading}>
              {isDownloading ? "Downloading..." : "Download movies"}
            </button>
          </div>
        </div>

        {message ? (
          <div className={`${styles.alert} ${messageTone === "success" ? styles.alertSuccess : ""}`}>
            {message}
          </div>
        ) : null}

        <div className={styles.card}>
          <p className={styles.sectionLabel}>Filters</p>
          <div className={styles.filterGrid}>
            <input
              className={styles.input}
              placeholder="Genre"
              value={genre}
              onChange={(e) => setGenre(e.target.value)}
            />
            <input
              className={styles.input}
              placeholder="Director"
              value={director}
              onChange={(e) => setDirector(e.target.value)}
            />
            <input
              className={styles.input}
              placeholder="Star"
              value={star}
              onChange={(e) => setStar(e.target.value)}
            />
          </div>
          <div className={styles.filterGrid}>
            <input
              className={styles.input}
              placeholder="Min rating"
              type="number"
              min={0}
              max={10}
              step={0.1}
              value={minRating}
              onChange={(e) => setMinRating(e.target.value)}
            />
            <input
              className={styles.input}
              placeholder="Max rating"
              type="number"
              min={0}
              max={10}
              step={0.1}
              value={maxRating}
              onChange={(e) => setMaxRating(e.target.value)}
            />
            <input
              className={styles.input}
              placeholder="Min year"
              type="number"
              value={minYear}
              onChange={(e) => setMinYear(e.target.value)}
            />
            <input
              className={styles.input}
              placeholder="Max year"
              type="number"
              value={maxYear}
              onChange={(e) => setMaxYear(e.target.value)}
            />
          </div>
          <div className={styles.filterRow}>
            <select className={styles.select} value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="title">Title</option>
              <option value="release_date">Release date</option>
              <option value="rating">IMDb rating</option>
              <option value="meta_score">Meta score</option>
              <option value="total_rating_count">Total ratings</option>
            </select>
            <select className={styles.select} value={order} onChange={(e) => setOrder(e.target.value as "asc" | "desc")}>
              <option value="asc">Ascending</option>
              <option value="desc">Descending</option>
            </select>
            <button className={styles.primary} type="button" onClick={fetchMovies}>
              Apply
            </button>
          </div>
        </div>

        <div className={styles.main}>
          {status === "loading" ? (
            <div className={styles.card}>
              <p className={styles.titleSm}>Loading movies…</p>
            </div>
          ) : movies.length ? (
            movies.map((movie) => (
              <div className={styles.card} key={movie.movie_id}>
                <p className={styles.titleSm}>{movie.title}</p>
                <p className={styles.meta}>
                  {movie.release_date ? `Released ${movie.release_date}` : "Release date unknown"}
                </p>
                <p className={styles.lede}>{movie.description || "No overview available."}</p>
                <div className={styles.chipRow}>
                  {movie.imdb_rating ? <span className={styles.chip}>IMDb {movie.imdb_rating}</span> : null}
                  {movie.meta_score ? <span className={styles.chip}>Meta {movie.meta_score}</span> : null}
                </div>
                <div className={styles.buttonRow}>
                  <button
                    className={styles.primary}
                    type="button"
                    onClick={() => updateWatchLater(movie.movie_id)}
                  >
                    Add to watchlist
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className={styles.card}>
              <p className={styles.lede}>No movies found.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
