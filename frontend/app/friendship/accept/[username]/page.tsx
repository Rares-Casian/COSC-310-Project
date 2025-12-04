"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { use } from "react";
import styles from "../../../dashboard/page.module.css";

const apiBase =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function AcceptFriendPage({
  params,
}: {
  params: Promise<{ username: string }>;
}) {
  const { username } = use(params); 
  const router = useRouter();

  const [message, setMessage] = useState("Accepting friend request...");
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      router.push("/login");
      return;
    }

    const acceptRequest = async () => {
      try {
        const res = await fetch(
          `${apiBase}/friendship/accept/${username}`,
          {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        const data = await res.json().catch(() => null);

        if (!res.ok) {
          throw new Error(data?.detail || "Could not accept request");
        }

        setMessage(`🎉 Congratulations! You are now friends with ${username}.`);
      } catch (err: any) {
        setError(err.message);
      }
    };

    acceptRequest();
  }, [username, router]);

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.glassCard}>
          <span className={styles.tag}>Friendship</span>
          <h1 className={styles.title}>Friend Request Accepted</h1>

          {error ? (
            <p style={{ color: "#f87171", marginTop: 20 }}>{error}</p>
          ) : (
            <p className={styles.lede} style={{ marginTop: 20 }}>
              {message}
            </p>
          )}

          <div className={styles.actions} style={{ marginTop: 28 }}>
            <button
              className={styles.primary}
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
