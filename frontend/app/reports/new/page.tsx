"use client";

import { useState } from "react";
import styles from "../../dashboard/page.module.css";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function NewReportPage() {
  const [reportedId, setReportedId] = useState("");
  const [type, setType] = useState("review");
  const [reason, setReason] = useState("");
  const [message, setMessage] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const submit = async () => {
    if (!token) {
      setMessage("Login as member/critic/administrator to file a report.");
      return;
    }
    try {
      const response = await fetch(`${apiBase}/reports/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ reported_id: reportedId, type, reason }),
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not submit report.");
      }
      setMessage("Report submitted.");
      setReportedId("");
      setReason("");
    } catch (error: any) {
      setMessage(error?.message || "Could not submit report.");
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.header}>
          <div>
            <p className={styles.kicker}>Reports</p>
            <h1 className={styles.title}>Submit a report</h1>
            <p className={styles.meta}>Members, critics, and administrators can file reports.</p>
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

        {message && <div className={styles.alert}>{message}</div>}

        <div className={styles.card}>
          <p className={styles.sectionLabel}>Report details</p>
          <div className={styles.stack}>
            <input
              className={styles.input}
              placeholder="Reported user ID"
              value={reportedId}
              onChange={(e) => setReportedId(e.target.value)}
            />
            <select
              className={styles.select}
              value={type}
              onChange={(e) => setType(e.target.value)}
            >
              <option value="review">Review</option>
              <option value="user">User</option>
              <option value="movie">Movie</option>
              <option value="comment">Comment</option>
            </select>
            <textarea
              className={styles.textarea}
              placeholder="Reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
            <button className={styles.primary} type="button" onClick={submit}>
              Submit report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
