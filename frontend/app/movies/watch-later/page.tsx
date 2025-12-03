"use client";

import { useEffect, useMemo, useState } from "react";
import styles from "../../dashboard/page.module.css";

type WatchLaterItem = {
  movie_id: string;
  title: string;
  description?: string;
};

type Status = "loading" | "ready" | "error";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function WatchLaterPage() {
  const [items, setItems] = useState<WatchLaterItem[]>([]);
  const [status, setStatus] = useState<Status>("loading");
  const [message, setMessage] = useState("");
  const [messageTone, setMessageTone] = useState<"info" | "error" | "success">("info");

  const token = useMemo(
    () => (typeof window !== "undefined" ? localStorage.getItem("access_token") : null),
    []
  );

  const loadWatchLater = async () => {
    if (!token) {
      setStatus("error");
      setMessage("You must be logged in to view your watchlist.");
      return;
    }
    setStatus("loading");
    setMessage("");
    try {
      const response = await fetch(`${apiBase}/movies/watch-later`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not load watchlist.");
      }
      setItems(Array.isArray(data?.watch_later) ? data.watch_later : []);
      setStatus("ready");
    } catch (error: any) {
      setStatus("error");
      setMessage(error?.message || "Could not load watchlist.");
      setMessageTone("error");
    }
  };

  useEffect(() => {
    loadWatchLater();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const removeFromWatchlist = async (movieId: string) => {
    if (!token) {
      setMessage("You must be logged in.");
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
        body: JSON.stringify({ movie_id: movieId, action: "remove" }),
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not update watchlist.");
      }
      setMessage(data?.message || "Removed.");
      setMessageTone("success");
      loadWatchLater();
    } catch (error: any) {
      setMessage(error?.message || "Could not update watchlist.");
      setMessageTone("error");
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.header}>
          <div>
            <p className={styles.kicker}>Watchlist</p>
            <h1 className={styles.title}>Your watch-later list</h1>
          </div>
          <div className={styles.headerActions}>
            <button className={styles.secondary} type="button" onClick={() => (window.location.href = "/dashboard")}>
              Back to dashboard
            </button>
          </div>
        </div>

        {message ? (
          <div className={`${styles.alert} ${messageTone === "success" ? styles.alertSuccess : ""}`}>
            {message}
          </div>
        ) : null}

        <div className={styles.main}>
          {status === "loading" ? (
            <div className={styles.card}>
              <p className={styles.titleSm}>Loading watchlist…</p>
            </div>
          ) : items.length ? (
            items.map((item) => (
              <div className={styles.card} key={item.movie_id}>
                <p className={styles.titleSm}>{item.title}</p>
                {item.description ? <p className={styles.lede}>{item.description}</p> : null}
                <div className={styles.buttonRow}>
                  <button
                    className={styles.secondary}
                    type="button"
                    onClick={() => removeFromWatchlist(item.movie_id)}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className={styles.card}>
              <p className={styles.lede}>Nothing in your watchlist yet.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
