from datetime import datetime, timedelta
import pickle

ACCESS_TOKEN_TTL = 60*15


async def add_token_to_revoked(token: str, cache=None) -> dict:
    """
    Функція додає дійсний access_token до відкликаних з метою унеможливлення його подальшого використання
    Args:
    token (str): Access_token, який буде додано до списку відкликаних маркерів.
    cache: Передаємо об'єкт Redis
    Returns:
    Словник відкликаних токенів
    """
    key = await get_key_from_token(token=token)
    token_ttl = datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_TTL)
    tokens_revoked_redis = await cache.get('tokens')
    if tokens_revoked_redis:
        token_revoked = pickle.loads(tokens_revoked_redis)
        token_revoked.update({key: token_ttl})
    else:
        token_revoked = {key: token_ttl}
    await cache.set('tokens', pickle.dumps(token_revoked))
    return token_revoked


async def update_valid_tokens_redis(tokens: dict, cache=None):
    """
    Функція оноввлює в кеші ще валідні по часу відкликані токені
    Args:
    tokens: Словник токенів для запису в Redis кеш
    cache: Redis клієнт
    Returns:
    Співпрограмму для EventLoop
    """
    await cache.set('tokens', pickle.dumps(tokens))                                                             # noqa


async def get_revoked_tokens(cache) -> dict:
    """
    Функція отримує усі відкликані токени з кешу
    :cache: Redis кліент
    Returns:
    словник відкликаних токенів
    """
    tokens_revoked_redis = await cache.get('tokens')
    if tokens_revoked_redis:
        return pickle.loads(tokens_revoked_redis)


async def get_valid_token_from_revoked(revoked_tokens: dict, cache=None) -> dict:
    """
    Функція нормалізує словник усіх відкладених токенів. Для кожного відкладеного токена перевіряється час його
    валідності. Як токен вже не валідний, тоді він повністю видаляється зі списку відкликаних токенів.
    revoked_tokens: Словник з усіма відкладеними токенами
    cache: Redis клієнт для роботи з кешом
    Returns:
    Нормалізований словник з відкладеними токенами
    """
    tokens_valid = {}
    if revoked_tokens:
        tokens_valid = list(filter(lambda x: datetime.utcnow() < x[1], revoked_tokens.items()))
        tokens_valid = {box[0]: box[1] for box in tokens_valid}
        await update_valid_tokens_redis(tokens_valid, cache=cache)
    return tokens_valid


async def get_key_from_token(token: str) -> str:
    """
    Функція виділяє унікальну(підписану) частину токена. Оскільки вона не повторюється, то вона буде використовуватись
    як ключ в словнику відкладених токенів
    Args:
    :token: Токен доступу
    Args:
    Поветається тільки підписана частина вхідного токена
    """
    return token.split(".")[2]
