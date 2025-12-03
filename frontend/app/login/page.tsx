"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./page.module.css";

type Status = "idle" | "loading" | "success" | "error";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");

  useEffect(() => {
    // If already logged in, skip back to dashboard
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (token) {
      router.replace("/dashboard");
    }
  }, [router]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatus("loading");
    setMessage("");

    try {
      const body = new URLSearchParams({
        username,
        password,
      });

      const response = await fetch(`${apiBase}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        const detail =
          data?.error?.message ||
          data?.detail ||
          "Could not log in right now. Please check your details and try again.";
        setStatus("error");
        setMessage(detail);
        return;
      }

      if (data?.access_token) {
        try {
          localStorage.setItem("access_token", data.access_token);
        } catch {
          /* ignore storage failures in non-browser envs */
        }
      }

      setStatus("success");
      setMessage("Logged in successfully. Redirecting...");
      setPassword("");

      router.push("/dashboard");
    } catch (error) {
      setStatus("error");
      setMessage("Network error. Please try again.");
    }
  };

  return (
    <div className={styles.page}>
      <main className={styles.card}>
        <p className={styles.tag}>Movie Explorer</p>
        <h1 className={styles.title}>Log in</h1>
        <p className={styles.lede}>
          Use your username or email with your password. The request goes straight to the backend
          for authentication.
        </p>

        <form className={styles.form} onSubmit={handleSubmit}>
          <label className={styles.label} htmlFor="username">
            Username or email
          </label>
          <input
            id="username"
            name="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="you@example.com"
            required
            autoComplete="username"
          />

          <label className={styles.label} htmlFor="password">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Your password"
            required
            minLength={8}
            autoComplete="current-password"
          />

          <button className={styles.submit} type="submit" disabled={status === "loading"}>
            {status === "loading" ? "Signing in..." : "Log in"}
          </button>
        </form>

        {message ? (
          <div
            className={`${styles.alert} ${
              status === "success" ? styles.success : styles.error
            }`}
            role="status"
            aria-live="polite"
          >
            {message}
          </div>
        ) : null}

        <div className={styles.footer}>
          <span>Need an account?</span>
          <a href="/register">Create one</a>
        </div>
      </main>
    </div>
  );
}
