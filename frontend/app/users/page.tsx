"use client";

import { useEffect, useState } from "react";
import styles from "../dashboard/page.module.css";

type User = {
  user_id: string;
  username: string;
  email: string;
  role: string;
  status: string;
};

type Status = "loading" | "ready" | "error";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [status, setStatus] = useState<Status>("loading");
  const [message, setMessage] = useState("");
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [role, setRole] = useState("member");
  const [userStatus, setUserStatus] = useState("active");

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const loadUsers = async () => {
    if (!token) {
      setStatus("error");
      setMessage("Login as administrator to manage users.");
      return;
    }
    setStatus("loading");
    setMessage("");
    try {
      const response = await fetch(`${apiBase}/users/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json().catch(() => []);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not load users.");
      }
      setUsers(data);
      setStatus("ready");
    } catch (error: any) {
      setStatus("error");
      setMessage(error?.message || "Could not load users.");
    }
  };

  useEffect(() => {
    loadUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const updateUser = async () => {
    if (!token || !selectedUser) return;
    try {
      const response = await fetch(`${apiBase}/users/${encodeURIComponent(selectedUser.user_id)}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ role, status: userStatus }),
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not update user.");
      }
      setMessage("User updated.");
      loadUsers();
    } catch (error: any) {
      setMessage(error?.message || "Could not update user.");
    }
  };

  const deleteUser = async (userId: string) => {
    if (!token) return;
    try {
      const response = await fetch(`${apiBase}/users/${encodeURIComponent(userId)}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not delete user.");
      }
      setMessage("User deleted.");
      loadUsers();
    } catch (error: any) {
      setMessage(error?.message || "Could not delete user.");
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.header}>
          <div>
            <p className={styles.kicker}>Users</p>
            <h1 className={styles.title}>Admin user management</h1>
            <p className={styles.meta}>Administrators can view, update, and delete users.</p>
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
          <p className={styles.sectionLabel}>Edit selected user</p>
          <div className={styles.formRow}>
            <select
              className={styles.select}
              value={selectedUser?.user_id || ""}
              onChange={(e) => {
                const found = users.find((u) => u.user_id === e.target.value) || null;
                setSelectedUser(found);
                if (found) {
                  setRole(found.role);
                  setUserStatus(found.status);
                }
              }}
            >
              <option value="">Select user</option>
              {users.map((u) => (
                <option key={u.user_id} value={u.user_id}>
                  {u.username} ({u.role})
                </option>
              ))}
            </select>
            <select
              className={styles.select}
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="guest">Guest</option>
              <option value="member">Member</option>
              <option value="critic">Critic</option>
              <option value="moderator">Moderator</option>
              <option value="administrator">Administrator</option>
            </select>
            <select
              className={styles.select}
              value={userStatus}
              onChange={(e) => setUserStatus(e.target.value)}
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
            <button className={styles.primary} type="button" onClick={updateUser}>
              Update user
            </button>
          </div>
        </div>

        <div className={styles.main}>
          {status === "loading" ? (
            <div className={styles.card}>
              <p className={styles.titleSm}>Loading users…</p>
            </div>
          ) : users.length ? (
            users.map((user) => (
              <div className={styles.card} key={user.user_id}>
                <p className={styles.titleSm}>
                  {user.username} ({user.role})
                </p>
                <p className={styles.meta}>{user.email}</p>
                <p className={styles.meta}>Status: {user.status}</p>
                <div className={styles.actions}>
                  <button className={styles.secondary} type="button" onClick={() => deleteUser(user.user_id)}>
                    Delete
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className={styles.card}>
              <p className={styles.lede}>No users to display.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
