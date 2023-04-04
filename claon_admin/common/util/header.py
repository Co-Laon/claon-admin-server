from fastapi import Response


def add_jwt_tokens(
        response: Response,
        jwt_tokens: dict
):
    response.headers["access-token"] = jwt_tokens.get("access-token")
    response.headers["refresh-token"] = jwt_tokens.get("refresh-token")
