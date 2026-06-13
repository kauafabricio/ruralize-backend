from fastapi import HTTPException

class FeedService:

    def __init__(self, post_repo, user_repo, profile_repo=None):
        self.post_repo = post_repo
        self.user_repo = user_repo
        self.profile_repo = profile_repo

    def _filter_posts_with_existing_users(self, posts):
        existing_users = {}
        filtered_posts = []

        for post in posts:
            user_id = post.get("user_id")
            if not user_id:
                continue

            if user_id not in existing_users:
                existing_users[user_id] = bool(self.user_repo.find_by_id(user_id))

            if existing_users[user_id]:
                filtered_posts.append(post)

        return filtered_posts

    def _enrich_post_with_author(self, post):
        if self.profile_repo:
            profile = self.profile_repo.find_by_user_id(post.get("user_id"))
            if profile:
                post["user_name"] = profile.get("name") or "Usuário"
                post["user_photo"] = profile.get("profile_photo_url")
                return post

        user = self.user_repo.find_by_id(post.get("user_id"))
        if user:
            post["user_name"] = user.get("name") or "Usuário"
            post["user_photo"] = user.get("profile_photo_url")
        else:
            post["user_name"] = "Usuário"
            post["user_photo"] = None
        return post

    # buscar postagens de usuários da plataforma
    # aparecerá prioridade para amigos, depois para quem o usuário segue e por último para os demais usuários   

    def get_general_feed(self, user_id: str = None):
        posts = self.post_repo.get_all_posts()
        posts = self._filter_posts_with_existing_users(posts)
        return sorted(
            [self._enrich_post_with_author(p) for p in posts],
            key=lambda x: x["created_at"],
            reverse=True,
        )
    
    # buscar postagens apenas dos usuários que o usuário logado segue

    def get_following_feed(self, user_id):
        user = self.user_repo.find_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        following = list(user.get("following", []))
        posts = self.post_repo.get_posts_by_users(following)
        posts = self._filter_posts_with_existing_users(posts)

        return sorted(
            [self._enrich_post_with_author(p) for p in posts],
            key=lambda x: x["created_at"],
            reverse=True
        )