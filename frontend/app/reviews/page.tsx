"use client";

import { useEffect, useState } from "react";
import styles from "../dashboard/page.module.css";

type Review = {
  review_id: string;
  user_id: string;
  rating: number;
  title: string;
  text: string;
  usefulness?: { helpful: number; total_votes: number };
  created_at?: string;
};

type Status = "idle" | "loading" | "error";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function ReviewsPage() {
  const [movieId, setMovieId] = useState("");
  const [movieOptions, setMovieOptions] = useState<{ movie_id: string; title: string }[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");
  const [title, setTitle] = useState("");
  const [rating, setRating] = useState(8);
  const [content, setContent] = useState("");
  const [hoverRating, setHoverRating] = useState<number | null>(null);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [currentRole, setCurrentRole] = useState<string | null>(null);
  const [filterRating, setFilterRating] = useState<number | "">("");
  const [sortBy, setSortBy] = useState("date");
  const [order, setOrder] = useState<"asc" | "desc">("desc");

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const loadReviews = async () => {
    if (!movieId) return;
    setStatus("loading");
    setMessage("");
    try {
      const params = new URLSearchParams();
      if (filterRating !== "") params.set("rating", String(filterRating));
      params.set("sort_by", sortBy);
      params.set("order", order);
      const response = await fetch(
        `${apiBase}/reviews/${encodeURIComponent(movieId)}${params.toString() ? `?${params}` : ""}`
      );
      const data: Review[] = await response.json().catch(() => []);
      if (!response.ok) {
        throw new Error("Could not load reviews.");
      }
      setReviews(data);
      setStatus("idle");
    } catch (error: any) {
      setStatus("error");
      setMessage(error?.message || "Failed to load reviews.");
    }
  };

  const submitReview = async () => {
    if (!token || !movieId) {
      setMessage("Login and select a movie to review.");
      return;
    }
    try {
      const response = await fetch(`${apiBase}/reviews/${encodeURIComponent(movieId)}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ rating: Math.round(rating), title, text: content }),
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not add review.");
      }
      setMessage("Review submitted.");
      setContent("");
      setTitle("");
      setRating(8);
      loadReviews();
    } catch (error: any) {
      setMessage(error?.message || "Could not add review.");
    }
  };

  const vote = async (reviewId: string, isHelpful: boolean) => {
    if (!token || !movieId) {
      setMessage("Login to vote on reviews.");
      return;
    }
    try {
      const response = await fetch(
        `${apiBase}/reviews/${encodeURIComponent(movieId)}/${encodeURIComponent(reviewId)}/vote`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ vote: isHelpful }),
        }
      );
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not vote.");
      }
      setMessage("Vote recorded.");
      loadReviews();
    } catch (error: any) {
      setMessage(error?.message || "Could not vote on review.");
    }
  };

  const deleteReview = async (reviewId: string) => {
    if (!token || !movieId) return;
    try {
      const response = await fetch(
        `${apiBase}/reviews/${encodeURIComponent(movieId)}/${encodeURIComponent(reviewId)}`,
        {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(data?.error?.message || data?.detail || "Could not delete review.");
      }
      setMessage("Review deleted.");
      loadReviews();
    } catch (error: any) {
      setMessage(error?.message || "Could not delete review.");
    }
  };

  useEffect(() => {
    const loadMovieOptions = async () => {
      try {
        const response = await fetch(`${apiBase}/movies/?limit=50`);
        const data = await response.json().catch(() => []);
        if (Array.isArray(data)) {
          setMovieOptions(data.map((m: any) => ({ movie_id: m.movie_id, title: m.title })));
          if (data[0]?.movie_id) {
            setMovieId(data[0].movie_id);
          }
        }
      } catch {
        /* ignore */
      }
    };
    const loadMe = async () => {
      if (!token) return;
      try {
        const response = await fetch(`${apiBase}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await response.json().catch(() => null);
        if (response.ok && data?.user_id) {
          setCurrentUserId(data.user_id);
          setCurrentRole(data.role);
        }
      } catch {
        /* ignore */
      }
    };
    loadMovieOptions();
    loadMe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <div className={styles.header}>
          <div>
            <p className={styles.kicker}>Reviews</p>
            <h1 className={styles.title}>Reviews per movie</h1>
            <p className={styles.meta}>Fetch, submit, vote, and delete reviews.</p>
          </div>
          <div className={styles.headerActions}>
            <select
              className={styles.select}
              aria-label="Movie"
              value={movieId}
              onChange={(e) => setMovieId(e.target.value)}
            >
              {movieOptions.map((m) => (
                <option key={m.movie_id} value={m.movie_id}>
                  {m.title}
                </option>
              ))}
            </select>
            <button className={styles.primary} type="button" onClick={loadReviews}>
              Load reviews
            </button>
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
          <p className={styles.sectionLabel}>Add a review</p>
          <div className={styles.formRow}>
            <div className={styles.stack} style={{ minWidth: 180 }}>
              <span className={styles.meta}>Rating (tap to set)</span>
              <div className={styles.ratingRow}>
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((value) => {
                  const active = hoverRating ? value <= hoverRating : value <= rating;
                  return (
                    <button
                      type="button"
                      key={value}
                      className={`${styles.ratingDot} ${active ? styles.ratingDotActive : ""}`}
                      onMouseEnter={() => setHoverRating(value)}
                      onMouseLeave={() => setHoverRating(null)}
                      onFocus={() => setHoverRating(value)}
                      onBlur={() => setHoverRating(null)}
                      onClick={() => {
                        setRating(value);
                        setHoverRating(null);
                      }}
                      aria-label={`Set rating to ${value}`}
                    >
                      {value}
                    </button>
                  );
                })}
              </div>
            </div>
            <label className={styles.stack} style={{ flex: 1 }}>
              Title
              <input
                className={styles.input}
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Title of your review"
              />
            </label>
          </div>
          <div className={styles.stack} style={{ marginTop: 8 }}>
            <label className={styles.stack}>
              Content
              <textarea
                className={styles.textarea}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Write your thoughts..."
              />
            </label>
            <div className={styles.buttonRow}>
              <button className={styles.primary} type="button" onClick={submitReview}>
                Submit review
              </button>
            </div>
          </div>
        </div>

        <div className={styles.card}>
          <p className={styles.sectionLabel}>Filters</p>
          <div className={styles.formRow}>
            <select
              className={styles.select}
              value={filterRating === "" ? "" : filterRating}
              onChange={(e) => setFilterRating(e.target.value === "" ? "" : Number(e.target.value))}
            >
              <option value="">All ratings</option>
              {[1,2,3,4,5,6,7,8,9,10].map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
            <select className={styles.select} value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="date">Date</option>
              <option value="rating">Rating</option>
              <option value="helpful">Helpful</option>
              <option value="total_votes">Total votes</option>
            </select>
            <select className={styles.select} value={order} onChange={(e) => setOrder(e.target.value as "asc" | "desc")}>
              <option value="desc">Newest / High first</option>
              <option value="asc">Oldest / Low first</option>
            </select>
            <button className={styles.primary} type="button" onClick={loadReviews}>
              Apply
            </button>
          </div>
        </div>

        <div className={styles.main}>
          {status === "loading" ? (
            <div className={styles.card}>
              <p className={styles.titleSm}>Loading reviews…</p>
            </div>
          ) : reviews.length ? (
            reviews.map((review) => (
              <div className={`${styles.card} ${styles.reviewCard}`} key={review.review_id}>
                <p className={styles.titleSm}>
                  {review.title} · Rating {review.rating}/10
                </p>
                <p className={styles.meta}>Posted by {review.user_id}</p>
                <div className={styles.scrollBody}>
                  <p className={styles.lede}>{review.text}</p>
                </div>
                <p className={styles.meta}>
                  Helpful {review.usefulness?.helpful ?? 0}/{review.usefulness?.total_votes ?? 0}
                </p>
                <div className={styles.buttonRow}>
                  <button className={styles.primary} type="button" onClick={() => vote(review.review_id, true)}>
                    Helpful
                  </button>
                  <button className={styles.secondary} type="button" onClick={() => vote(review.review_id, false)}>
                    Not helpful
                  </button>
                  {(currentUserId && review.user_id === currentUserId) ||
                  (currentRole === "administrator" || currentRole === "moderator") ? (
                    <button className={styles.secondary} type="button" onClick={() => deleteReview(review.review_id)}>
                      Delete
                    </button>
                  ) : null}
                </div>
              </div>
            ))
          ) : (
            <div className={styles.card}>
              <p className={styles.lede}>No reviews loaded.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
