"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { use } from "react"; // Required for new Next.js dynamic params
import styles from "../../../dashboard/page.module.css";

const apiBase =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type Movie = {
  movie_id: string;
  title: string;
};

export default function FriendWatchlistPage({
  params,
}: {
  params: Promise<{ username: string }>;
}) {
 
  const { username } = use(params);

  const router = useRouter();
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      router.push("/login");
      return;
    }

    const loadWatchlist = async () => {
      try {
        const res = await fetch(
          `${apiBase}/friendship/${username}/watchlist`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (!res.ok) {
          const data = await res.json().catch(() => null);
          throw new Error(
            data?.detail || "Could not load friend's watchlist."
          );
        }

        const data = await res.json();
        setMovies(data.watch_later || []);
      } catch (err: any) {
        setError(err.message || "Failed to load watchlist.");
      } finally {
        setLoading(false);
      }
    };

    loadWatchlist();
  }, [username, router]);

  if (loading) {
    return (
      <div className={styles.page}>
        <div className={styles.shell}>
          <div className={styles.glassCard}>
            <h1 className={styles.title}>Loading watchlist…</h1>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.glassCard}>
          <span className={styles.tag}>Watchlist</span>
          <h1 className={styles.title}>{username}'s Watchlist</h1>

          {error && (
            <p style={{ color: "#f87171", marginTop: 16 }}>{error}</p>
          )}

          {movies.length === 0 && (
            <p className={styles.lede} style={{ marginTop: 20 }}>
              No movies in this watchlist.
            </p>
          )}

          {/* Only titles */}
          <div
            style={{
              marginTop: 24,
              display: "grid",
              gap: "12px",
            }}
          >
            {movies.map((movie) => (
              <div
                key={movie.movie_id}
                className={styles.third}
                style={{
                  padding: "14px",
                  borderRadius: "12px",
                  fontSize: "18px",
                  fontWeight: "600",
                }}
              >
                {movie.title}
              </div>
            ))}
          </div>

          <div className={styles.actions} style={{ marginTop: 28 }}>
            <button
              className={styles.secondary}
              onClick={() => router.push("/friendship/list")}
            >
              Back to Friends
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
