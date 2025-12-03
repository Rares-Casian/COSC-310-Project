"use client";

import { useEffect, useState } from "react";
import styles from "../dashboard/page.module.css";

type Penalty = {
  penalty_id: string;
  user_id: string;
  type: string;
  severity: string;
  reason: string;
  issued_by: string;
  expires_at?: string | null;
  status?: string;
};

type Status = "loading" | "ready" | "error";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function PenaltiesPage() {
  const [penalties, setPenalties] = useState<Penalty[]>([]);
  const [status, setStatus] = useState<Status>("loading");
  const [message, setMessage] = useState("");
  const [userId, setUserId] = useState("");
  const [type, setType] = useState("suspension");
  const [severity, setSeverity] = useState("low");
  const [reason, setReason] = useState("");
  const [duration, setDuration] = useState(7);
  const [resolveNotes, setResolveNotes] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const loadPenalties = async () => {
    if (!token) {
      setStatus("error");
      setMessage("Login as moderator/administrator to view penalties.");
      return;
    }
    setStatus("loading");
    setMessage("");
    try {
      const response = await fetch(`${apiBase}/penalties/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json().catch(() => []);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not load penalties.");
      }
      setPenalties(data);
      setStatus("ready");
    } catch (error: any) {
      setStatus("error");
      setMessage(error?.message || "Could not load penalties.");
    }
  };

  useEffect(() => {
    loadPenalties();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const issuePenalty = async () => {
    if (!token) return;
    try {
      const response = await fetch(`${apiBase}/penalties/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: userId,
          type,
          severity,
          reason,
          duration_days: duration,
        }),
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not issue penalty.");
      }
      setMessage("Penalty issued.");
      loadPenalties();
    } catch (error: any) {
      setMessage(error?.message || "Could not issue penalty.");
    }
  };

  const resolvePenalty = async (penaltyId: string) => {
    if (!token) return;
    try {
      const response = await fetch(`${apiBase}/penalties/${encodeURIComponent(penaltyId)}`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}` },
        body: resolveNotes ? null : undefined,
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not resolve penalty.");
      }
      setMessage("Penalty resolved.");
      loadPenalties();
    } catch (error: any) {
      setMessage(error?.message || "Could not resolve penalty.");
    }
  };

  const deletePenalty = async (penaltyId: string) => {
    if (!token) return;
    try {
      const response = await fetch(`${apiBase}/penalties/${encodeURIComponent(penaltyId)}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not delete penalty.");
      }
      setMessage("Penalty deleted.");
      loadPenalties();
    } catch (error: any) {
      setMessage(error?.message || "Could not delete penalty.");
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.header}>
          <div>
            <p className={styles.kicker}>Penalties</p>
            <h1 className={styles.title}>Moderation penalties</h1>
            <p className={styles.meta}>Issue, resolve, and delete penalties.</p>
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
          <p className={styles.sectionLabel}>Issue a penalty</p>
          <div className={styles.stack}>
            <input
              className={styles.input}
              placeholder="User ID"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
            />
            <div className={styles.formRow}>
              <select
                className={styles.select}
                value={type}
                onChange={(e) => setType(e.target.value)}
              >
                <option value="suspension">Suspension</option>
                <option value="posting_ban">Posting ban</option>
                <option value="review_ban">Review ban</option>
                <option value="report_ban">Report ban</option>
              </select>
              <select
                className={styles.select}
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
              <input
                className={styles.input}
                type="number"
                min={1}
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
              />
            </div>
            <textarea
              className={styles.textarea}
              placeholder="Reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
            <button className={styles.primary} type="button" onClick={issuePenalty}>
              Issue penalty
            </button>
          </div>
        </div>

        <div className={styles.card}>
          <p className={styles.sectionLabel}>Resolve notes</p>
          <input
            className={styles.input}
            placeholder="Optional resolution notes"
            value={resolveNotes}
            onChange={(e) => setResolveNotes(e.target.value)}
          />
        </div>

        <div className={styles.main}>
          {status === "loading" ? (
            <div className={styles.card}>
              <p className={styles.titleSm}>Loading penalties…</p>
            </div>
          ) : penalties.length ? (
            penalties.map((penalty) => (
              <div className={styles.card} key={penalty.penalty_id}>
                <p className={styles.titleSm}>
                  {penalty.type} · {penalty.severity}
                </p>
                <p className={styles.meta}>User: {penalty.user_id}</p>
                <p className={styles.meta}>Issued by: {penalty.issued_by}</p>
                {penalty.expires_at && <p className={styles.meta}>Expires: {penalty.expires_at}</p>}
                <p className={styles.lede}>{penalty.reason}</p>
                <div className={styles.buttonRow}>
                  <button className={styles.primary} type="button" onClick={() => resolvePenalty(penalty.penalty_id)}>
                    Resolve
                  </button>
                  <button className={styles.secondary} type="button" onClick={() => deletePenalty(penalty.penalty_id)}>
                    Delete
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className={styles.card}>
              <p className={styles.lede}>No penalties to display.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
