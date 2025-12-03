"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import styles from "./page.module.css";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (!token) {
      router.replace("/login");
      return;
    }

    const fetchRoleAndRedirect = async () => {
      try {
        const response = await fetch(`${apiBase}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await response.json().catch(() => null);
        const role = data?.role || "member";
        router.replace(`/dashboard/${encodeURIComponent(role)}`);
      } catch {
        router.replace("/login");
      }
    };

    fetchRoleAndRedirect();
  }, [router]);

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <p className={styles.tag}>Movie Explorer</p>
        <h1 className={styles.title}>Loading your dashboard…</h1>
      </div>
    </div>
  );
}
