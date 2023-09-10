import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from PhotoShare.app.api.endpoints.user import router_user
from PhotoShare.app.api.endpoints.authentication import router_auth
from PhotoShare.app.api.endpoints.comments import router_comments
from PhotoShare.app.api.endpoints.photos import router as router_photo
from PhotoShare.app.api.endpoints.tags import router as router_tags
from PhotoShare.app.services.redis import RedisService

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
app.include_router(router_photo)
app.include_router(router_tags)

if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", reload=True, log_level="info", port=8000)
