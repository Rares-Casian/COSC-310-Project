import styles from "./page.module.css";

export default function Home() {
  return (
    <div className={styles.page}>
      <main className={styles.panel}>
        <p className={styles.tag}>Movie Explorer</p>
        <h1 className={styles.title}>Welcome back</h1>
        <p className={styles.lede}>
          Sign in to pick up where you left off or create an account to start tracking your watch
          list. Simple, clean, and ready for your next session.
        </p>
        <div className={styles.actions}>
          <a className={styles.primary} href="/login">
            Log in
          </a>
          <a className={styles.secondary} href="/register">
            Create account
          </a>
        </div>
      </main>
    </div>
  );
}
