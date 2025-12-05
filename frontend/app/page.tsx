"use client"; // enables client-side hooks

import { useEffect, useState } from "react";
import styles from "./page.module.css";

export default function Home() {
  const [backendMessage, setBackendMessage] = useState("");

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/hello`)
      .then((res) => res.json())
      .then((data) => setBackendMessage(data.message))
      .catch((err) => console.error(err));
  }, []);

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.glassCard}>
          <p className={styles.tag}>Movie Explorer</p>
          <h1 className={styles.title}>Welcome</h1>
          <p className={styles.lede}>
            Sign in to access your watchlist or create an account to start tracking what you have
            watched. Everything stays in sync with the backend API.
          </p>

          {/* Backend message */}
          {backendMessage && (
            <p style={{ marginTop: "1rem", fontWeight: "bold", color: "green" }}>
              Message from backend: {backendMessage}
            </p>
          )}

          <div className={styles.actions}>
            <a className={styles.primary} href="/login">
              Log in
            </a>
            <a className={styles.secondary} href="/register">
              Create account
            </a>
            <a className={styles.third} href="/dashboard/guest">
              Browse as a guest
            </a>
          </div>
        </div>

        <div className={styles.callouts}>
          <div className={styles.callout}>
            <p className={styles.calloutLabel}>Live sync</p>
            <p className={styles.calloutText}>
              Saves directly to the backend when you update your list.
            </p>
          </div>
          <div className={styles.callout}>
            <p className={styles.calloutLabel}>Flexible roles</p>
            <p className={styles.calloutText}>
              Guest, member, critic, moderator—ready for permission layers.
            </p>
          </div>
          <div className={styles.callout}>
            <p className={styles.calloutLabel}>Clean start</p>
            <p className={styles.calloutText}>
              Straightforward shell to extend with browse, search, and reviews.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
