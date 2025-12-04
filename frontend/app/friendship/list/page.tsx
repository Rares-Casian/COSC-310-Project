"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import styles from "../../dashboard/page.module.css";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type Friend = {
  user_id: string;
  username: string;
  email: string;
};

export default function FriendListPage() {
  const router = useRouter();
  const [friends, setFriends] = useState<Friend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      router.push("/login");
      return;
    }

    const loadFriends = async () => {
      try {
        const res = await fetch(`${apiBase}/friendship/list`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) {
          const data = await res.json().catch(() => null);
          throw new Error(data?.detail || "Could not load friends");
        }

        const data = await res.json();
        setFriends(data.friends || []);
      } catch (err: any) {
        setError(err.message || "Failed to load friends");
      } finally {
        setLoading(false);
      }
    };

    loadFriends();
  }, [router]);

  if (loading) {
    return (
      <div className={styles.page}>
        <div className={styles.shell}>
          <div className={styles.glassCard}>
            <h1 className={styles.title}>Loading friends…</h1>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.glassCard}>
          <h1 className={styles.title}>FRIEND LIST</h1>
          <p className={styles.lede}>Click a friend to view their watchlist.</p>

          {error && (
            <p style={{ color: "#f87171", marginTop: "12px" }}>{error}</p>
          )}

          {friends.length === 0 && (
            <p className={styles.lede} style={{ marginTop: "16px" }}>
              You haven't added any friends yet.
            </p>
          )}

          {/* Friends list */}
          <div
            style={{
              marginTop: "24px",
              display: "grid",
              gap: "14px",
            }}
          >
            {friends.map((friend) => (
              <button
                key={friend.user_id}
                onClick={() =>
                  router.push(`/friendship/${friend.username}/watchlist`)
                }
                className={styles.third}
                style={{
                  padding: "16px",
                  borderRadius: "14px",
                  textAlign: "left",
                  width: "100%",
                  cursor: "pointer",
                  transition: "0.2s ease",
                }}
              >
                <strong style={{ fontSize: "18px" }}>
                  {friend.username}
                </strong>
                <p
                  style={{
                    opacity: 0.7,
                    marginTop: "4px",
                    fontSize: "14px",
                  }}
                >
                  {friend.email}
                </p>
              </button>
            ))}
          </div>

          {/* Back button */}
          <div className={styles.actions} style={{ marginTop: "32px" }}>
            <button
              className={styles.secondary}
              type="button"
              onClick={() => router.push("/dashboard/member")}
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
