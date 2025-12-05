"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./page.module.css";

type DashboardUser = {
  username: string;
  email: string;
  role: string;
  status: string;
};

type DashboardData = {
  user: Partial<DashboardUser>;
  actions?: string[];
  links?: { label: string; href: string }[];
};

type Status = "loading" | "ready" | "error";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type RoleDashboardProps = {
  role: "guest" | "member" | "critic" | "moderator" | "administrator";
};

type DashboardSection = {
  title: string;
  description: string;
  href: string;
  cta: string;
};

const ROLE_ALIASES: Record<string, RoleDashboardProps["role"]> = {
  admin: "administrator",
  admins: "administrator",
  mod: "moderator",
};

const ROLE_DESCRIPTIONS: Record<RoleDashboardProps["role"], string> = {
  guest: "Browse public content and previews.",
  member: "Manage your watchlist, ratings, and reviews.",
  critic: "Publish critic-grade reviews and featured picks.",
  moderator: "Review reports, manage flags, and keep the community safe.",
  administrator: "Manage users, roles, and system settings.",
};

const normalizeRole = (value: string): RoleDashboardProps["role"] => {
  return (ROLE_ALIASES[value] ?? value) as RoleDashboardProps["role"];
};

const ROLE_SECTIONS: Record<RoleDashboardProps["role"], DashboardSection[]> = {
  guest: [
    { title: "Movies", description: "Browse movies and trending picks.", href: "/movies", cta: "Open movies" },
    { title: "Reviews", description: "Read community and critic reviews.", href: "/reviews", cta: "Read reviews" },
  ],
  member: [
    { title: "Recommendations", description: "Get personalized movie recommendations.", href: "/recommendations", cta: "View recommendations" },
    { title: "Movies", description: "Browse the catalog and search titles.", href: "/movies", cta: "Browse movies" },
    { title: "Watchlist", description: "View and edit your watch-later list.", href: "/movies/watch-later", cta: "Manage watchlist" },
    { title: "Reviews", description: "Write and edit your own reviews.", href: "/reviews", cta: "Open reviews" },
    { title: "Reports", description: "Submit reports on problematic content.", href: "/reports/new", cta: "File a report" },
  ],
  critic: [
    { title: "Recommendations", description: "Get personalized movie recommendations.", href: "/recommendations", cta: "View recommendations" },
    { title: "Movies", description: "Browse the catalog and search titles.", href: "/movies", cta: "Browse movies" },
    { title: "Watchlist", description: "Keep your watch-later list updated.", href: "/movies/watch-later", cta: "Manage watchlist" },
    { title: "Reviews", description: "Publish critic-grade reviews and edits.", href: "/reviews", cta: "Open reviews" },
    { title: "Reports", description: "Submit reports on problematic content.", href: "/reports/new", cta: "File a report" },
  ],
  moderator: [
    { title: "Recommendations", description: "Get personalized movie recommendations.", href: "/recommendations", cta: "View recommendations" },
    { title: "Movies", description: "Browse the catalog and search titles.", href: "/movies", cta: "Browse movies" },
    { title: "Reports queue", description: "Review, update, or close reports.", href: "/reports", cta: "View reports" },
    { title: "Penalties", description: "Issue and resolve penalties.", href: "/penalties", cta: "Manage penalties" },
    { title: "Watchlist", description: "Assist users with their watch-later lists.", href: "/movies/watch-later", cta: "View watchlists" },
  ],
  administrator: [
    { title: "Recommendations", description: "Get personalized movie recommendations.", href: "/recommendations", cta: "View recommendations" },
    { title: "Movies", description: "Browse the catalog and search titles.", href: "/movies", cta: "Browse movies" },
    { title: "Users", description: "Manage accounts, roles, and status.", href: "/users", cta: "Manage users" },
    { title: "Reports", description: "Oversee report resolutions.", href: "/reports", cta: "Review reports" },
    { title: "Penalties", description: "Issue and resolve penalties.", href: "/penalties", cta: "Manage penalties" },
    { title: "Movies export", description: "Download the full movie dataset.", href: "/movies/download", cta: "Download movies" },
  ],
};

export function RoleDashboard({ role }: RoleDashboardProps) {
  const router = useRouter();
  const [status, setStatus] = useState<Status>("loading");
  const [user, setUser] = useState<DashboardUser | null>(null);
  const [actions, setActions] = useState<string[]>([]);
  const [links, setLinks] = useState<{ label: string; href: string }[]>([]);
  const [message, setMessage] = useState<string>("");
  const [roleSections, setRoleSections] = useState<DashboardSection[]>([]);

  const handleLogout = async () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    try {
      if (token) {
        await fetch(`${apiBase}/auth/logout`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        });
      }
    } catch {
      /* allow logout even if the network call fails */
    } finally {
      localStorage.removeItem("access_token");
      router.replace("/login");
    }
  };

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

    if (role === "guest") {
      // Guest dashboard needs no login
      setUser({
        username: "Guest",
        email: "N/A",
        role: "guest",
        status: "active",
      });
      setActions([]);
      setLinks([]);
      setRoleSections(ROLE_SECTIONS["guest"]);
      setStatus("ready");
      return;
    }
    if (!token) {
      router.replace("/login");
      return;
    }

    const loadDashboard = async () => {
      try {
        const profileResponse = await fetch(`${apiBase}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const profile = await profileResponse.json().catch(() => null);

        if (!profileResponse.ok) {
          throw new Error(
            profile?.error?.message ||
              profile?.detail ||
              "Could not load your profile right now."
          );
        }

        const currentRole = normalizeRole(profile?.role || role);
        const targetRole = normalizeRole(role);
        if (currentRole !== targetRole) {
          router.replace(`/dashboard/${encodeURIComponent(currentRole)}`);
          return;
        }

        const response = await fetch(`${apiBase}/dashboard/${targetRole}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data: DashboardData | null = await response.json().catch(() => null);

        if (!response.ok) {
          throw new Error(
            data && "error" in (data as any)
              ? (data as any).error?.message
              : data && "detail" in (data as any)
                ? (data as any).detail
                : "Could not load your dashboard right now."
          );
        }

        setUser({
          username: data?.user?.username ?? profile?.username ?? "",
          email: data?.user?.email ?? profile?.email ?? "",
          role: normalizeRole(data?.user?.role ?? profile?.role ?? targetRole),
          status: data?.user?.status ?? profile?.status ?? "",
        });
        setActions(Array.isArray(data?.actions) ? data?.actions : []);
        setLinks(Array.isArray(data?.links) ? data.links : []);
        setRoleSections(ROLE_SECTIONS[targetRole] ?? []);
        setStatus("ready");
      } catch (error: any) {
        setStatus("error");
        setMessage(error?.message || "Could not load your dashboard.");
        localStorage.removeItem("access_token");
        router.replace("/login");
      }
    };

    loadDashboard();
  }, [role, router]);

  if (status === "loading") {
    return (
      <div className={styles.page}>
        <div className={styles.shell}>
          <div className={styles.card}>
            <p className={styles.kicker}>Movie Explorer</p>
            <h1 className={styles.title}>Loading dashboard…</h1>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <header className={styles.header}>
          <div>
            <p className={styles.kicker}>Movie Explorer</p>
            <h1 className={styles.title}>Dashboard</h1>
            {user ? (
              <p className={styles.meta}>
                Role: <strong>{user.role}</strong>{" "}
                <span
                  className={`${styles.badge} ${
                    user.status === "active" ? styles.badgeSuccess : styles.badgeMuted
                  }`}
                >
                  {user.status}
                </span>
              </p>
            ) : (
              <p className={styles.meta}>Gathering your account details…</p>
            )}
          </div>
          <div className={styles.headerActions}>
            <button className={styles.secondary} type="button" onClick={() => router.push("/")}>
              Home
            </button>
            <button className={styles.primary} type="button" onClick={handleLogout}>
              Log out
            </button>
          </div>
        </header>

        {message && <div className={`${styles.alert} ${styles.alertError}`}>{message}</div>}

        <div className={styles.layout}>
          <aside className={styles.sidebar}>
            <p className={styles.sectionLabel}>Available actions</p>
            {actions.length ? ( 
              <div className={styles.chipRow}>
                {actions.map((item) => (
                  <span className={styles.chip} key={item}>
                    {item}
                  </span>
                ))}
              </div>
            ) : (
              <p className={styles.lede}>No actions available for this role yet.</p>
            )}

            <p className={styles.sectionLabel}>Quick links</p>
            <div className={styles.stack}>
              {links.map((link) => (
                <a className={styles.sidebarButton} key={`${link.label}-${link.href}`} href={link.href}>
                  {link.label}
                </a>
              ))}
            </div>
          </aside>

          <main className={styles.main}>
            <div className={styles.card}>
              <p className={styles.sectionLabel}>Profile</p>
              {user ? (
                <>
                  <p className={styles.titleSm}>{user.username}</p>
                  <p className={styles.meta}>{user.email}</p>
                  <p className={styles.meta}>
                    Role <strong>{user.role}</strong> · Status{" "}
                    <strong className={styles.metaStrong}>{user.status}</strong>
                  </p>
                </>
              ) : (
                <p className={styles.lede}>Unable to load your details.</p>
              )}
            </div>

            <div className={styles.card}>
              <p className={styles.sectionLabel}>Role summary</p>
              <p className={styles.lede}>{ROLE_DESCRIPTIONS[role]}</p>
            </div>

            <div className={styles.card}>
              <p className={styles.sectionLabel}>Random movies generator</p>
              <p className={styles.lede}>
                In case you have no idea what to watch. Click the button below
              </p>

              <div className={styles.buttonRow}>
                <button
                  className={styles.primary}
                  onClick={() => router.push("/movies/random")}
                >
                  Generator
                </button>
              </div>
            </div>

            

            {roleSections.map((section) => (
              <div className={styles.card} key={section.title}>
                <p className={styles.sectionLabel}>{section.title}</p>
                <p className={styles.lede}>{section.description}</p>
                <div className={styles.buttonRow}>
                  <a className={styles.primary} href={section.href}>
                    {section.cta}
                  </a>
                </div>
              </div>
            ))}
          </main>
        </div>
      </div>
    </div>
  );
}
