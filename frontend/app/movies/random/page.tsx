"use client";

import { useEffect, useState } from "react";
import styles from "../../dashboard/page.module.css";

const apiBase =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type Movie = {
  id: number;
  title: string;
  overview: string;
  poster_path: string | null;
  rating: number;
  release_date: string;
};

export default function RandomMoviePage() {
  const [movie, setMovie] = useState<Movie | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadMovie = async () => {
    setLoading(true);
    setError("");
    setMovie(null);

    try {
      const res = await fetch(`${apiBase}/movies/random`);
      const data = await res.json().catch(() => null);

      if (!res.ok) {
        throw new Error(data?.detail || "Failed to load movie");
      }

      setMovie(data);
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    }

    setLoading(false);
  };

  useEffect(() => {
    loadMovie();
  }, []);

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.glassCard}>
          <span className={styles.tag}>Random Movie</span>
          <h1 className={styles.title}>Your Movie Pick</h1>

          {loading && <p className={styles.lede}>Fetching a random movie...</p>}

          {error && (
            <p style={{ color: "#f87171", marginTop: "16px" }}>{error}</p>
          )}

          {movie && (
            <>
              {/* Poster */}
              {movie.poster_path && (
                <img
                  src={movie.poster_path}
                  alt={movie.title}
                  style={{
                    width: "100%",
                    borderRadius: "16px",
                    marginTop: "20px",
                    boxShadow: "0 6px 20px rgba(0,0,0,0.4)",
                  }}
                />
              )}

              {/* Movie Info */}
              <h2
                style={{
                  marginTop: "20px",
                  fontSize: "28px",
                  fontWeight: "700",
                }}
              >
                {movie.title}
              </h2>

              <p className={styles.lede}>{movie.overview}</p>

              <div className={styles.callouts} style={{ marginTop: "24px" }}>
                <div className={styles.callout}>
                  <p className={styles.calloutLabel}>Rating</p>
                  <p className={styles.calloutText}>{movie.rating}/10</p>
                </div>

                <div className={styles.callout}>
                  <p className={styles.calloutLabel}>Release Date</p>
                  <p className={styles.calloutText}>{movie.release_date}</p>
                </div>
              </div>
            </>
          )}

          {/* Generate Again */}
          <div className={styles.actions} style={{ marginTop: "32px" }}>
            <button className={styles.primary} onClick={loadMovie}>
              Get Another Movie
            </button>

            <a className={styles.secondary} href="/dashboard/member">
              Back to Dashboard
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
