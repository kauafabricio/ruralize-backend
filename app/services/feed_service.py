from fastapi import HTTPException

class FeedService:

    def __init__(self, post_repo, user_repo):
        self.post_repo = post_repo
        self.user_repo = user_repo

    def get_general_feed(self):
        posts = self.post_repo.get_all_posts()

        return sorted(
            posts,
            key=lambda x: (x["likes"], x["created_at"]),
            reverse=True
        )

    def get_friends_feed(self, user_id):
        user = self.user_repo.find_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        following = set(user.get("following", []))
        followers = set(user.get("followers", []))

        friends = list(following.intersection(followers))

        posts = self.post_repo.get_posts_by_users(friends)

        return sorted(
            posts,
            key=lambda x: x["created_at"],
            reverse=True
        )