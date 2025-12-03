"use client";

import { useEffect, useState } from "react";
import styles from "../dashboard/page.module.css";

// Define a TypeScript type for movies
interface Movie {
  title: string;
  rating: number;
  [key: string]: any; // optional for extra fields
}

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
export default function TrendingPage() {

  const [movies, setMovies] = useState<Movie[]>([]);

  useEffect(() => {
    fetchMovies();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
  <thead>
    <tr>
      <th style={{ borderBottom: "1px solid #ccc", textAlign: "left", padding: "0.5rem" }}>
        Title
      </th>
      <th style={{ borderBottom: "1px solid #ccc", textAlign: "left", padding: "0.5rem" }}>
        Rating
      </th>
    </tr>
  </thead>
  <tbody>
    {movies.map((movie, idx) => (
      <tr key={idx}>
        <td style={{ padding: "0.5rem", borderBottom: "1px solid #eee" }}>{movie.title}</td>
        <td style={{ padding: "0.5rem", borderBottom: "1px solid #eee" }}>{movie.vote_average}</td>
      </tr>
    ))}
  </tbody>
</table>
    
      </div>
    </div>
  );
}
