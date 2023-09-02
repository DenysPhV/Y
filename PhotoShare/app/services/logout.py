from datetime import datetime, timedelta
import pickle

ACCESS_TOKEN_TTL = 900


async def add_token_to_revoked(token: str, cache=None) -> dict:
    key = token.split('.')[2]
    ttl = datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_TTL)
    print(ttl)
    tokens_revoked_redis = await cache.get('tokens')
    if tokens_revoked_redis:
        token_revoked = pickle.loads(tokens_revoked_redis)
        token_revoked.update({key: ttl})
    else:
        token_revoked = {key: ttl}
    await cache.set('tokens', pickle.dumps(token_revoked))
    return token_revoked


async def token_validation(token: str, tokens: dict) -> bool:
    if datetime.utcnow() < tokens.get(token):
        return True
    return False


async def update_valid_tokens_redis(tokens: dict | None = None, cache=None):
    await cache.set('tokens', pickle.dumps(tokens))  # noqa


async def get_revoked_tokens(cache) -> dict:
    tokens_revoked_redis = await cache.get('tokens')
    if tokens_revoked_redis:
        return pickle.loads(tokens_revoked_redis)


async def get_valid_token_from_revoked(revoked_tokens: dict, cache=None) -> dict:
    tokens_valid = {}
    if revoked_tokens:
        for t in revoked_tokens:
            is_valid = await token_validation(t, revoked_tokens)
            if is_valid:
                tokens_valid.update({t: revoked_tokens.get(t)})
            await update_valid_tokens_redis(tokens_valid, cache=cache)
            print(tokens_valid)
    return tokens_valid


async def get_key_from_token(token: str) -> str:
    return token.split(".")[2]
