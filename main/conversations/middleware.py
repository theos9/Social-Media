from urllib.parse import parse_qs
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings

User = get_user_model()

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]

        if not token:
            await send({"type": "websocket.close", "code": 4001})
            return

        try:
            # Validate token
            UntypedToken(token)
            # Decode to get user_id
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data.get("user_id")
            if not user_id:
                raise InvalidToken("user_id not found in token")

            # Fetch user from DB
            user = await database_sync_to_async(User.objects.get)(id=user_id)
            scope["user"] = user

        except (InvalidToken, TokenError, User.DoesNotExist):
            await send({"type": "websocket.close", "code": 4001})
            return

        return await self.inner(scope, receive, send)
