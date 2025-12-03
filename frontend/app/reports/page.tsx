"use client";

import { useEffect, useState } from "react";
import styles from "../dashboard/page.module.css";

type Report = {
  report_id: string;
  reporter_id: string;
  reported_id: string;
  type: string;
  reason: string;
  status: string;
  moderator_notes?: string;
};

type Status = "loading" | "ready" | "error";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [status, setStatus] = useState<Status>("loading");
  const [message, setMessage] = useState("");
  const [updateStatus, setUpdateStatus] = useState("pending");
  const [notes, setNotes] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const loadReports = async () => {
    if (!token) {
      setStatus("error");
      setMessage("Login as moderator/administrator to view reports.");
      return;
    }
    setStatus("loading");
    setMessage("");
    try {
      const response = await fetch(`${apiBase}/reports/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json().catch(() => []);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not load reports.");
      }
      setReports(data);
      setStatus("ready");
    } catch (error: any) {
      setStatus("error");
      setMessage(error?.message || "Could not load reports.");
    }
  };

  useEffect(() => {
    loadReports();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const patchReport = async (reportId: string) => {
    if (!token) return;
    try {
      const response = await fetch(`${apiBase}/reports/${encodeURIComponent(reportId)}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
          body: JSON.stringify({ status: updateStatus, moderator_notes: notes }),
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not update report.");
      }
      setMessage("Report updated.");
      loadReports();
    } catch (error: any) {
      setMessage(error?.message || "Could not update report.");
    }
  };

  const deleteReport = async (reportId: string) => {
    if (!token) return;
    try {
      const response = await fetch(`${apiBase}/reports/${encodeURIComponent(reportId)}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not delete report.");
      }
      setMessage("Report deleted.");
      loadReports();
    } catch (error: any) {
      setMessage(error?.message || "Could not delete report.");
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.header}>
          <div>
            <p className={styles.kicker}>Reports</p>
            <h1 className={styles.title}>Moderation queue</h1>
            <p className={styles.meta}>Moderators and administrators can manage reports.</p>
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
          <p className={styles.sectionLabel}>Update settings</p>
          <div className={styles.formRow}>
            <select
              className={styles.select}
              value={updateStatus}
              onChange={(e) => setUpdateStatus(e.target.value)}
            >
              <option value="pending">Pending</option>
              <option value="under_review">Under review</option>
              <option value="resolved">Resolved</option>
              <option value="dismissed">Dismissed</option>
            </select>
            <input
              className={styles.input}
              placeholder="Resolution notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>
        </div>

        <div className={styles.main}>
          {status === "loading" ? (
            <div className={styles.card}>
              <p className={styles.titleSm}>Loading reports…</p>
            </div>
          ) : reports.length ? (
            reports.map((report) => (
              <div className={styles.card} key={report.report_id}>
                <p className={styles.titleSm}>
                  {report.type} · Status: {report.status}
                </p>
                <p className={styles.meta}>Reporter: {report.reporter_id}</p>
                <p className={styles.meta}>Reported: {report.reported_id}</p>
                <p className={styles.lede}>{report.reason}</p>
                {report.moderator_notes && <p className={styles.meta}>Notes: {report.moderator_notes}</p>}
                <div className={styles.buttonRow}>
                  <button className={styles.primary} type="button" onClick={() => patchReport(report.report_id)}>
                    Update
                  </button>
                  <button className={styles.secondary} type="button" onClick={() => deleteReport(report.report_id)}>
                    Delete
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className={styles.card}>
              <p className={styles.lede}>No reports available.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
