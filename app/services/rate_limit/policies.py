def get_rate_limit_policy(path: str):
    if path.startswith("/api/v1/auth"):
        return ("auth", 5, 60)
    elif path.startswith("/api/v1/ai"):
        return ("ai", 20, 60)
    return ("default", 100, 60)
