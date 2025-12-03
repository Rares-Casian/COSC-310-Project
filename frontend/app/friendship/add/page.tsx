"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import styles from "../../dashboard/page.module.css";

const apiBase =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function AddFriendPage() {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const sendRequest = async () => {
    setStatusMessage("");
    setErrorMessage("");

    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    if (!search.trim()) {
      setErrorMessage("Please enter a username.");
      return;
    }

    try {
      const res = await fetch(`${apiBase}/friendship/request/${search}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json().catch(() => null);

      if (!res.ok) {
        const detail =
          data?.detail || data?.message || "User does not exist.";
        throw new Error(detail);
      }

      setStatusMessage(`Friend request sent to "${search}"!`);
      setSearch("");
    } catch (error: any) {
      setErrorMessage(error.message);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.glassCard}>
          <span className={styles.tag}>Friend Request</span>
          <h1 className={styles.title}>Add a New Friend</h1>
          <p className={styles.lede}>
            Type a username to send a friend request.
          </p>

          {errorMessage && (
            <p style={{ color: "#f87171", marginTop: "16px" }}>
              {errorMessage}
            </p>
          )}

          {statusMessage && (
            <p style={{ color: "#34d399", marginTop: "16px" }}>
              {statusMessage}
            </p>
          )}

          <input
            type="text"
            placeholder="Enter username"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              marginTop: "24px",
              padding: "12px 16px",
              width: "100%",
              borderRadius: "14px",
              border: "1px solid rgba(148,163,184,0.3)",
              background: "rgba(255,255,255,0.06)",
              color: "#e2e8f0",
              fontSize: "16px",
              outline: "none",
            }}
          />

          <div className={styles.actions} style={{ marginTop: "24px" }}>
            <button className={styles.primary} onClick={sendRequest}>
              Send Request
            </button>

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
