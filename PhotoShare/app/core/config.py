from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: int
    postgres_domain: str
    postgres_port: int
    postgres_db_name: str
    postgres_path: str

    secret_access_key: str
    secret_refresh_key: str
    secret_email_key: str
    algorithm: str

    email_username: str
    email_password: str
    email_from: str
    email_port: int
    email_server: str
    email_from_name: str

    redis_host: str
    redis_port: int

    class Config:
        env_file = Path(__file__).parent.joinpath(".env")
        env_file_encoding = "utf-8"


settings = Settings()
print(settings.Config.env_file)
