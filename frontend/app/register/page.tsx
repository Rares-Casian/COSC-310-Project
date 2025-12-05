"use client";

import { FormEvent, useState } from "react";
import styles from "./page.module.css";

type Status = "idle" | "loading" | "success" | "error";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatus("loading");
    setMessage("");

    try {
      const response = await fetch(`${apiBase}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });

      const bodyText = await response.text();
      let data: any = null;
      try {
        data = bodyText ? JSON.parse(bodyText) : null;
      } catch {
        /* Body was not JSON; fallback to plain text below */
      }

      if (!response.ok) {
        const validationDetails = Array.isArray(data?.error?.details)
          ? data.error.details.join(" ")
          : undefined;
        const detail =
          data?.error?.message ||
          validationDetails ||
          data?.detail ||
          bodyText?.trim() ||
          `Request failed with status ${response.status}`;
        setStatus("error");
        setMessage(detail);
        console.error("Registration failed", {
          status: response.status,
          body: bodyText,
          parsed: data,
        });
        return;
      }

      setStatus("success");
      setMessage("Account created. You can now log in.");
      setUsername("");
      setEmail("");
      setPassword("");
    } catch (error) {
      setStatus("error");
      setMessage("Network error. Please try again.");
    }
  };

  return (
    <div className={styles.page}>
      <main className={styles.card}>
        <p className={styles.tag}>Movie Explorer</p>
        <h1 className={styles.title}>Create your account</h1>
        <p className={styles.lede}>
          Connect to the backend and start tracking your watch list. Use the same credentials when
          you sign in later.
        </p>
        <div className={styles.hintsBox}>
          <p className={styles.hintTitle}>Registration tips</p>
          <ul className={styles.hints}>
            <li>Username: 3-20 characters, letters and numbers only.</li>
            <li>Password: 8+ characters with upper, lower, number, and symbol.</li>
            <li>Email must be valid and not already registered.</li>
          </ul>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          <label className={styles.label} htmlFor="username">
            Username
          </label>
          <input
            id="username"
            name="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Choose a username"
            required
            minLength={3}
            maxLength={20}
            autoComplete="username"
          />

          <label className={styles.label} htmlFor="email">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            autoComplete="email"
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
            placeholder="At least 8 chars, mixed case, number, symbol"
            required
            minLength={8}
            autoComplete="new-password"
          />

          <button className={styles.submit} type="submit" disabled={status === "loading"}>
            {status === "loading" ? "Creating..." : "Create account"}
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
          <span>Already have an account?</span>
          <a href="/login">Log in</a>
        </div>
      </main>
    </div>
  );
}
