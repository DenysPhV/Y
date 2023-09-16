from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from PhotoShare.app.api.endpoints.user import router_user
from PhotoShare.app.api.endpoints.authentication import router_auth
from PhotoShare.app.api.endpoints.comments import router_comments
from PhotoShare.app.api.endpoints.tags import router_tags

from PhotoShare.app.api.endpoints.rating import router_rating
from PhotoShare.app.api.endpoints.photos import router as router_photos

from PhotoShare.app.services.redis import RedisService
from PhotoShare.app.models.base import Base


app = FastAPI(swagger_ui_parameters={"operationsSorter": "method"})


@app.on_event("startup")
def startup():
    """
    The startup ініціалізує асинхронний Redis клієнт
    Returns:
    Список Task на виконяння в EvenLoop

    Start up page definition

    :return: dict: health status
    """

    RedisService.init()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_auth)
app.include_router(router_comments)
app.include_router(router_user)
app.include_router(router_photos)
app.include_router(router_rating)
app.include_router(router_tags)


