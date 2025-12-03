"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./page.module.css";

type UserInfo = {
  username: string;
  email: string;
  role: string;
  status: string;
};

type Status = "loading" | "ready" | "error";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function DashboardPage() {
  const router = useRouter();
  const [status, setStatus] = useState<Status>("loading");
  const [user, setUser] = useState<UserInfo | null>(null);
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (!token) {
      router.replace("/login");
      return;
    }

    const fetchProfile = async () => {
      try {
        const response = await fetch(`${apiBase}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        const data = await response.json().catch(() => null);

        if (!response.ok) {
          throw new Error(
            data?.error?.message || data?.detail || "Could not load your profile right now."
          );
        }

        setUser({
          username: data.username,
          email: data.email,
          role: data.role,
          status: data.status,
        });
        setStatus("ready");
      } catch (error: any) {
        setStatus("error");
        setMessage(error?.message || "Could not load your profile.");
        localStorage.removeItem("access_token");
        router.replace("/login");
      }
    };

    fetchProfile();
  }, [router]);

  const roleActions = useMemo(() => {
    const role = (user?.role || "member") as string;
    const common = [
      "View your watchlist and recent activity",
      "Update profile details",
      "See recently watched items",
    ];
    const roleSpecific: Record<string, string[]> = {
      guest: ["Browse public reviews"],
      member: ["Add reviews and ratings", "Save watchlist entries"],
      critic: ["Submit critic-grade reviews", "Highlight featured picks"],
      moderator: ["Review reports", "Manage penalties and flags"],
      administrator: ["Manage users and roles", "Oversee reports and system settings"],
    };
    return [...common, ...(roleSpecific[role] || [])];
  }, [user?.role]);

  if (status === "loading") {
    return (
      <div className={styles.page}>
        <div className={styles.card}>
          <p className={styles.tag}>Movie Explorer</p>
          <h1 className={styles.title}>Loading dashboard…</h1>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.grid}>
        <div className={styles.card}>
          <p className={styles.tag}>Movie Explorer</p>
          <h1 className={styles.title}>Dashboard</h1>
          {user ? (
            <p className={styles.lede}>
              Signed in as <strong>{user.username}</strong> ({user.email}) · Role:{" "}
              <strong>{user.role}</strong>
            </p>
          ) : (
            <p className={styles.lede}>Unable to load your details.</p>
          )}
          {message && <div className={`${styles.alert} ${styles.error}`}>{message}</div>}
          <div className={styles.actions}>
            <button
              className={styles.secondary}
              type="button"
              onClick={() => router.push("/")}
            >
              Home
            </button>
            <button
              className={styles.primary}
              type="button"
              onClick={() => {
                localStorage.removeItem("access_token");
                router.replace("/login");
              }}
            >
              Log out
            </button>
          </div>
        </div>

        <div className={styles.card}>
          <p className={styles.sectionLabel}>What you can do</p>
          <ul className={styles.list}>
            {roleActions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
