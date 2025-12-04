"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import styles from "../../dashboard/page.module.css";

const apiBase =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type Requester = {
  user_id: string;
  username: string;
  email: string;
};

export default function FriendRequestsPage() {
  const router = useRouter();
  const [requests, setRequests] = useState<Requester[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    const loadRequests = async () => {
      try {
        const res = await fetch(`${apiBase}/friendship/requests`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) {
          const data = await res.json().catch(() => null);
          throw new Error(data?.detail || "Could not load friend requests");
        }

        const data = await res.json();
        setRequests(data.pending_requests || []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadRequests();
  }, [router]);

  if (loading) {
    return (
      <div className={styles.page}>
        <div className={styles.shell}>
          <div className={styles.glassCard}>
            <h1 className={styles.title}>Loading friend requests…</h1>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.glassCard}>
          <span className={styles.tag}>Friendship</span>
          <h1 className={styles.title}>Incoming Friend Requests</h1>

          {error && (
            <p style={{ color: "#f87171", marginTop: 12 }}>{error}</p>
          )}

          {requests.length === 0 && (
            <p className={styles.lede} style={{ marginTop: 20 }}>
              You have no friend requests right now.
            </p>
          )}

          {/* Request list */}
          <div style={{ marginTop: 24, display: "grid", gap: "14px" }}>
            {requests.map((req) => (
              <div
                key={req.user_id}
                className={styles.third}
                style={{
                  padding: "16px",
                  borderRadius: "14px",
                }}
              >
                <strong style={{ fontSize: "18px" }}>
                  {req.username}
                </strong>
                <p style={{ opacity: 0.7, fontSize: 14 }}>
                  {req.email}
                </p>

                <div className={styles.actions} style={{ marginTop: 14 }}>
                  <button
                    className={styles.primary}
                    onClick={() =>
                      router.push(`/friendship/accept/${req.username}`)
                    }
                    style={{ flex: "none" }}
                  >
                    Accept Request
                  </button>
                </div>
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
