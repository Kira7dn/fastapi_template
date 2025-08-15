from backend.app.domain.entities.user import User
from sklearn.metrics.pairwise import cosine_similarity  # Import AI lib
import numpy as np


class RecommendationService:
    def recommend(self, user: User, all_users: list[User]) -> list[str]:
        # AI logic: Simple cosine similarity trên preferences
        user_vec = np.array(
            [1 if pref in user.preferences else 0 for pref in ["ai", "ml", "data"]]
        )
        recommendations = []
        for other in all_users:
            other_vec = np.array(
                [1 if pref in other.preferences else 0 for pref in ["ai", "ml", "data"]]
            )
            similarity = cosine_similarity([user_vec], [other_vec])[0][0]
            if similarity > 0.5:
                recommendations.append(other.name)
        return recommendations
