from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from PhotoShare.app.api.endpoints.authentication import router_auth
from PhotoShare.app.core.database import get_db
from PhotoShare.app.services.redis import RedisService
app = FastAPI()


@app.on_event("startup")
async def startup():
    await RedisService.init()


@app.get("/", description="Main page")
def root():
    """
    Main page definition

    :return: dict: health status
    """
    return {"message": "Welcome to FastAPI! Check test"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
      Health Checker

      :param db: database session
      :return: dict: health status
      """
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception:
        raise HTTPException(status_code=500, detail="Error connecting to the database")


app.include_router(router_auth)
