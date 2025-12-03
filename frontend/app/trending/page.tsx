"use client";

import { useEffect, useState, useMemo } from "react";
import styles from "../dashboard/page.module.css";

// Define a TypeScript type for movies
interface Movie {
  id: string; 
  title: string;
  rating: number;
  [key: string]: any; // optional for extra fields
}

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
export default function TrendingPage() {

  const [movies, setMovies] = useState<Movie[]>([]);
  const [messageTone, setMessageTone] = useState<"info" | "error" | "success">("info");
  const [message, setMessage] = useState("");
  useEffect(() => {
    fetchMovies();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

    const token = useMemo(
    () => (typeof window !== "undefined" ? localStorage.getItem("access_token") : null),
    []
  );
  
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



const fetchMovies = async () => {
    try {
      const response = await fetch(`${apiBase}/trending`);
      const data: Movie[] = await response.json().catch(() => []);
      if (!response.ok) {
        throw new Error("Could not load movies.");
      }
      setMovies(data);
    } catch (error: any) {
      throw new Error("Could not load movies.");
    }
  };
  
  return (
        <div className={styles.page}>
      <header
        style={{
          width: "100%",
          position: "fixed",
          top: 0,
          left: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "1rem 2rem",
          zIndex: 1000,
        }}
      >
        <button
          className={styles.secondary}
          type="button"
          onClick={() => (window.location.href = "/dashboard")}
          style={{ position: "absolute", left: "2rem" }}
        >
          Back to dashboard
        </button>
        <h1 style={{ margin: 0 }}>Trending</h1>
      </header>

      <div style={{ height: "60px" }}></div>

      <div style={{ padding: "2rem" }}>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
              gap: "1.5rem",
            }}
          >
            {movies.map((movie, idx) => (
              <div
                key={idx}
                style={{
                  backgroundColor: "rgba(255, 255, 255, 0.05)",
                  borderRadius: "12px",
                  overflow: "hidden",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
                  textAlign: "center",
                }}
              >
                {/* Movie poster */}
                <img
                  src={
                    movie.poster_path
                      ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
                      : "https://via.placeholder.com/500x750?text=No+Image"
                  }
                  alt={movie.title}
                  style={{ width: "100%", height: "270px", objectFit: "cover" }}
                />

                {/* Movie info */}
                <div style={{ padding: "0.5rem" }}>
                  <h3 style={{ margin: "0.5rem 0", fontSize: "1rem" }}>{movie.title}</h3>
                  <p style={{ margin: 0, fontWeight: "bold" }}>Rating: {movie.vote_average}</p>
                  <button
                    className={styles.primary}
                    type="button"
                    onClick={() => updateWatchLater(movie.id.toString())}
                    style={{padding: "12px 14px", margin: "0.4rem"}}
                  >
                    Add to watchlist
                  </button>
                </div>
              </div>
            ))}
          </div>
      </div>
    </div>

  );
}
