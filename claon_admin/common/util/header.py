from fastapi import Response


def add_jwt_tokens(
        response: Response,
        access_token: str,
        refresh_token: str
):
    response.headers["access-token"] = access_token
    response.headers["refresh-token"] = refresh_token
