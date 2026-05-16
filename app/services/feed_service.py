from fastapi import HTTPException

class FeedService:

    def __init__(self, post_repo, user_repo):
        self.post_repo = post_repo
        self.user_repo = user_repo

    # buscar postagens de usuários da plataforma
    # aparecerá prioridade para amigos, depois para quem o usuário segue e por último para os demais usuários   

    def get_general_feed(self, user_id: str = None):
        posts = self.post_repo.get_all_posts()

        if not user_id:
            return sorted(
                posts,
                key=lambda x: (x["likes"], x["created_at"]),
                reverse=True
            )

        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        following = set(user.get("following", []))
        followers = set(user.get("followers", []))
        friends = following.intersection(followers)

        def feed_priority(post):
            user_id = post["user_id"]
            if user_id in friends:
                return 3
            if user_id in following:
                return 2
            return 1

        return sorted(
            posts,
            key=lambda x: (feed_priority(x), x["likes"], x["created_at"]),
            reverse=True
        )  
    
    # buscar postagens apenas dos amigos do usuário logado

    def get_friends_feed(self, user_id):
        user = self.user_repo.find_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # buscar 
        following = set(user.get("following", []))
        followers = set(user.get("followers", []))

        friends = list(following.intersection(followers))

        posts = self.post_repo.get_posts_by_users(friends)

        return sorted(
            posts,
            key=lambda x: x["created_at"],
            reverse=True
        )