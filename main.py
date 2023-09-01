from fastapi import FastAPI
from PhotoShare.app.api.endpoints.authentication import router_auth
app = FastAPI()

app.include_router(router_auth)




