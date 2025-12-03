"use client";

import { useEffect, useMemo, useState } from "react";
import styles from "../../dashboard/page.module.css";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function DownloadMoviesPage() {
  const token = useMemo(
    () => (typeof window !== "undefined" ? localStorage.getItem("access_token") : null),
    []
  );
  const [message, setMessage] = useState("");
  const [messageTone, setMessageTone] = useState<"info" | "error" | "success">("info");
  const [isDownloading, setIsDownloading] = useState(false);

  const downloadMovies = async () => {
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

  useEffect(() => {
    // auto-attempt once on load
    downloadMovies();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.header}>
          <div>
            <p className={styles.kicker}>Movies</p>
            <h1 className={styles.title}>Download dataset</h1>
            <p className={styles.meta}>Admins can export the full movie catalog as JSON.</p>
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

        <div className={styles.card}>
          <p className={styles.sectionLabel}>Export</p>
          <p className={styles.lede}>Click to download the movies JSON file.</p>
          <div className={styles.buttonRow}>
            <button className={styles.primary} type="button" onClick={downloadMovies} disabled={isDownloading}>
              {isDownloading ? "Downloading..." : "Download movies"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
