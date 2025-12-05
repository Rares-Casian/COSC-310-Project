"""Recommendation algorithms and utilities."""
from typing import List, Dict, Optional, Tuple
from collections import Counter, defaultdict
from backend.movies import utils as movie_utils
from backend.reviews import utils as review_utils
from backend.friendship import utils as friendship_utils
from backend.authentication import utils as user_utils
from backend.recommendations.schemas import RecommendedMovie


def get_user_reviewed_movies(user_id: str) -> List[str]:
    """Get list of movie IDs the user has reviewed."""
    reviews = review_utils.get_reviews_by_user(user_id)
    return list(set([r.get("movie_id") for r in reviews if r.get("movie_id")]))


def get_user_ratings(user_id: str) -> Dict[str, int]:
    """Get user's ratings for movies as {movie_id: rating}."""
    reviews = review_utils.get_reviews_by_user(user_id)
    return {r.get("movie_id"): r.get("rating", 0) for r in reviews if r.get("movie_id") and r.get("rating")}


def get_user_watchlist(user_id: str) -> List[str]:
    """Get user's watchlist movie IDs."""
    user = user_utils.get_user_by_id(user_id)
    if not user:
        return []
    return user.get("watch_later", [])


def get_user_preferences(user_id: str) -> Dict[str, float]:
    """Extract user preferences: favorite genres, directors, stars."""
    reviewed_movies = get_user_reviewed_movies(user_id)
    ratings = get_user_ratings(user_id)
    watchlist = get_user_watchlist(user_id)
    
    all_movie_ids = list(set(reviewed_movies + watchlist))
    all_movies = [movie_utils.get_movie(mid) for mid in all_movie_ids]
    all_movies = [m for m in all_movies if m]
    
    genre_scores = defaultdict(float)
    director_scores = defaultdict(float)
    star_scores = defaultdict(float)
    
    for movie in all_movies:
        movie_id = movie.get("movie_id")
        rating = ratings.get(movie_id, 5) 
        weight = rating / 10.0
        
        for genre in movie.get("genres", []):
            genre_scores[genre.lower()] += weight
        for director in movie.get("directors", []):
            director_scores[director.lower()] += weight
        for star in movie.get("main_stars", []):
            star_scores[star.lower()] += weight
    
    return {
        "genres": dict(genre_scores),
        "directors": dict(director_scores),
        "stars": dict(star_scores),
    }


def content_based_recommendations(user_id: str, limit: int = 20) -> List[RecommendedMovie]:
    """Recommend movies based on user's preferred genres, directors, and stars."""
    preferences = get_user_preferences(user_id)
    reviewed_movies = set(get_user_reviewed_movies(user_id))
    watchlist = set(get_user_watchlist(user_id))
    excluded = reviewed_movies | watchlist
    
    all_movies = movie_utils.load_movies()
    scored_movies = []
    
    for movie in all_movies:
        movie_id = movie.get("movie_id")
        if movie_id in excluded:
            continue
        
        score = 0.0
        reasons = []
        
        # Matching
        
        movie_genres = [g.lower() for g in movie.get("genres", [])]
        genre_matches = sum(preferences["genres"].get(g, 0) for g in movie_genres)
        if genre_matches > 0:
            score += genre_matches * 0.4
            top_genre = max(movie_genres, key=lambda g: preferences["genres"].get(g, 0))
            reasons.append(f"Similar genre: {top_genre.title()}")
        
        movie_directors = [d.lower() for d in movie.get("directors", [])]
        director_matches = sum(preferences["directors"].get(d, 0) for d in movie_directors)
        if director_matches > 0:
            score += director_matches * 0.3
            reasons.append(f"Director you like")
        
        movie_stars = [s.lower() for s in movie.get("main_stars", [])]
        star_matches = sum(preferences["stars"].get(s, 0) for s in movie_stars)
        if star_matches > 0:
            score += star_matches * 0.2
            reasons.append(f"Star you like")
        
        # Boost high rated movies
        imdb_rating = movie.get("imdb_rating", 0) or 0
        if imdb_rating >= 7.5:
            score += 0.1
        
        if score > 0:
            reason = ", ".join(reasons) if reasons else "Based on your preferences"
            scored_movies.append((score, movie, reason))
    
    # Sort by score and return top results
    scored_movies.sort(key=lambda x: x[0], reverse=True)
    recommendations = []
    
    for score, movie, reason in scored_movies[:limit]:
        rec_movie = RecommendedMovie(
            **movie,
            recommendation_reason=reason,
            recommendation_score=min(score / 10.0, 1.0)  # Normalize to 0-1
        )
        recommendations.append(rec_movie)
    
    return recommendations


def collaborative_recommendations(user_id: str, limit: int = 20) -> List[RecommendedMovie]:
    """Recommend movies based on similar users' preferences (collaborative filtering)."""
    user_ratings = get_user_ratings(user_id)
    if not user_ratings:
        return []
    
    reviewed_movies = set(get_user_reviewed_movies(user_id))
    watchlist = set(get_user_watchlist(user_id))
    excluded = reviewed_movies | watchlist
    
    # Get all users and ratings
    all_users = user_utils.load_active_users()
    user_similarities = []
    
    for other_user in all_users:
        other_id = other_user.get("user_id")
        if other_id == user_id or other_id == "guest":
            continue
        
        other_ratings = get_user_ratings(other_id)
        if not other_ratings:
            continue
        
        # Calculate similarity
        common_movies = set(user_ratings.keys()) & set(other_ratings.keys())
        if len(common_movies) < 2:
            continue
        
        dot_product = sum(user_ratings[m] * other_ratings[m] for m in common_movies)
        user_norm = sum(r * r for r in user_ratings.values()) ** 0.5
        other_norm = sum(r * r for r in other_ratings.values()) ** 0.5
        
        if user_norm == 0 or other_norm == 0:
            continue
        
        similarity = dot_product / (user_norm * other_norm)
        if similarity > 0:
            user_similarities.append((other_id, similarity))
    
    # Sort by similarity
    user_similarities.sort(key=lambda x: x[1], reverse=True)
    
    movie_scores = defaultdict(float)
    movie_reasons = defaultdict(list)
    
    for other_id, similarity in user_similarities[:10]:  # Top 10 most similar users
        other_ratings = get_user_ratings(other_id)
        for movie_id, rating in other_ratings.items():
            if movie_id in excluded:
                continue
            if rating >= 7: 
                movie_scores[movie_id] += similarity * rating
                movie_reasons[movie_id].append(f"Liked by similar users")
    
    # Convert to recommendations
    scored_items = [(score, mid) for mid, score in movie_scores.items()]
    scored_items.sort(key=lambda x: x[0], reverse=True)
    
    recommendations = []
    for score, movie_id in scored_items[:limit]:
        movie = movie_utils.get_movie(movie_id)
        if movie:
            reason = ", ".join(set(movie_reasons[movie_id])) or "Liked by users with similar taste"
            rec_movie = RecommendedMovie(
                **movie,
                recommendation_reason=reason,
                recommendation_score=min(score / 100.0, 1.0)
            )
            recommendations.append(rec_movie)
    
    return recommendations


def friend_based_recommendations(user_id: str, limit: int = 20) -> List[RecommendedMovie]:
    """Recommend movies based on what friends have reviewed highly."""
    friends = friendship_utils.get_friends(user_id)
    if not friends:
        return []
    
    reviewed_movies = set(get_user_reviewed_movies(user_id))
    watchlist = set(get_user_watchlist(user_id))
    excluded = reviewed_movies | watchlist
    
    movie_scores = defaultdict(float)
    movie_reasons = defaultdict(list)
    
    for friend_id in friends:
        friend_ratings = get_user_ratings(friend_id)
        for movie_id, rating in friend_ratings.items():
            if movie_id in excluded:
                continue
            if rating >= 7:  # Only consider movies liked by friends
                movie_scores[movie_id] += rating
                friend = user_utils.get_user_by_id(friend_id)
                friend_name = friend.get("username", "friend") if friend else "friend"
                movie_reasons[movie_id].append(friend_name)
    
    # Convert to recommendations
    scored_items = [(score, mid) for mid, score in movie_scores.items()]
    scored_items.sort(key=lambda x: x[0], reverse=True)
    
    recommendations = []
    for score, movie_id in scored_items[:limit]:
        movie = movie_utils.get_movie(movie_id)
        if movie:
            friend_names = list(set(movie_reasons[movie_id]))[:3]
            if len(friend_names) == 1:
                reason = f"Liked by {friend_names[0]}"
            elif len(friend_names) == 2:
                reason = f"Liked by {friend_names[0]} and {friend_names[1]}"
            else:
                reason = f"Liked by {', '.join(friend_names[:-1])}, and {friend_names[-1]}"
            
            rec_movie = RecommendedMovie(
                **movie,
                recommendation_reason=reason,
                recommendation_score=min(score / 50.0, 1.0)
            )
            recommendations.append(rec_movie)
    
    return recommendations


def popular_recommendations(user_id: str, limit: int = 20) -> List[RecommendedMovie]:
    """Recommend popular/highly-rated movies."""
    reviewed_movies = set(get_user_reviewed_movies(user_id))
    watchlist = set(get_user_watchlist(user_id))
    excluded = reviewed_movies | watchlist
    
    all_movies = movie_utils.load_movies()
    scored_movies = []
    
    for movie in all_movies:
        movie_id = movie.get("movie_id")
        if movie_id in excluded:
            continue
        
        score = 0.0
        reasons = []
        
        # High IMDB rating
        imdb_rating = movie.get("imdb_rating", 0) or 0
        if imdb_rating >= 8.0:
            score += 0.5
            reasons.append("Highly rated")
        elif imdb_rating >= 7.0:
            score += 0.3
            reasons.append("Well-rated")
        
        # High meta score
        meta_score = movie.get("meta_score", 0) or 0
        if meta_score >= 80:
            score += 0.3
            reasons.append("Critic favorite")
        
        # High amount of reviews
        total_reviews = movie.get("total_user_reviews", 0) or 0
        if total_reviews > 100:
            score += 0.2
            reasons.append("Popular")
        
        if score > 0:
            reason = ", ".join(reasons) if reasons else "Popular choice"
            scored_movies.append((score, movie, reason))
    
    scored_movies.sort(key=lambda x: x[0], reverse=True)
    recommendations = []
    
    for score, movie, reason in scored_movies[:limit]:
        rec_movie = RecommendedMovie(
            **movie,
            recommendation_reason=reason,
            recommendation_score=min(score, 1.0)
        )
        recommendations.append(rec_movie)
    
    return recommendations


def hybrid_recommendations(user_id: str, limit: int = 20) -> List[RecommendedMovie]:
    """Combine multiple recommendation strategies."""
    all_recommendations = {}
    
    # Get recommendations from different sources for hybrid
    content_recs = content_based_recommendations(user_id, limit * 2)
    collab_recs = collaborative_recommendations(user_id, limit * 2)
    friend_recs = friend_based_recommendations(user_id, limit * 2)
    popular_recs = popular_recommendations(user_id, limit * 2)
    
    # Combine and weight
    for rec in content_recs:
        movie_id = rec.movie_id
        if movie_id not in all_recommendations:
            all_recommendations[movie_id] = {
                "movie": rec,
                "score": rec.recommendation_score * 0.4, 
                "reasons": [rec.recommendation_reason]
            }
        else:
            all_recommendations[movie_id]["score"] += rec.recommendation_score * 0.4
            all_recommendations[movie_id]["reasons"].append(rec.recommendation_reason)
    
    for rec in collab_recs:
        movie_id = rec.movie_id
        if movie_id not in all_recommendations:
            all_recommendations[movie_id] = {
                "movie": rec,
                "score": rec.recommendation_score * 0.3,  # Collaborative weight
                "reasons": [rec.recommendation_reason]
            }
        else:
            all_recommendations[movie_id]["score"] += rec.recommendation_score * 0.3
            all_recommendations[movie_id]["reasons"].append(rec.recommendation_reason)
    
    for rec in friend_recs:
        movie_id = rec.movie_id
        if movie_id not in all_recommendations:
            all_recommendations[movie_id] = {
                "movie": rec,
                "score": rec.recommendation_score * 0.2,  # Friend-based weight
                "reasons": [rec.recommendation_reason]
            }
        else:
            all_recommendations[movie_id]["score"] += rec.recommendation_score * 0.2
            all_recommendations[movie_id]["reasons"].append(rec.recommendation_reason)
    
    for rec in popular_recs:
        movie_id = rec.movie_id
        if movie_id not in all_recommendations:
            all_recommendations[movie_id] = {
                "movie": rec,
                "score": rec.recommendation_score * 0.1,  # Popular weight
                "reasons": [rec.recommendation_reason]
            }
        else:
            all_recommendations[movie_id]["score"] += rec.recommendation_score * 0.1
            all_recommendations[movie_id]["reasons"].append(rec.recommendation_reason)
    
    # Sort by combined score
    sorted_recs = sorted(all_recommendations.values(), key=lambda x: x["score"], reverse=True)
    
    recommendations = []
    for item in sorted_recs[:limit]:
        reason = ", ".join(set(item["reasons"][:2]))  # Combine top 2 reasons
        movie_obj = item["movie"]
        try:
            movie_data = movie_obj.model_dump() if hasattr(movie_obj, "model_dump") else movie_obj.dict()
        except:
            # Fallback
            movie_data = movie_obj if isinstance(movie_obj, dict) else movie_obj.dict()

        # Avoid passing duplicate recommendation fields when rebuilding the combined object
        movie_data.pop("recommendation_reason", None)
        movie_data.pop("recommendation_score", None)
        
        rec_movie = RecommendedMovie(
            **movie_data,
            recommendation_reason=reason,
            recommendation_score=min(item["score"], 1.0)
        )
        recommendations.append(rec_movie)
    
    return recommendations
