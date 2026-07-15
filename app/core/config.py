from urllib.parse import quote_plus

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    This class reads values from the .env file automatically.
    Each attribute name below (DB_USER, DB_PASSWORD, etc.) must match
    a key in your .env file exactly.
    """
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"

    @property
    def DATABASE_URL(self) -> str:
        # Builds the MySQL connection string SQLAlchemy needs.
        # quote_plus() escapes special characters (like @, #, /, :) so a
        # password such as "VLJ@w70532" doesn't break the URL structure.
        safe_password = quote_plus(self.DB_PASSWORD)
        return (
            f"mysql+pymysql://{self.DB_USER}:{safe_password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


# Create ONE instance of Settings that the rest of the app imports.
# This is a common pattern: import `settings` anywhere you need config.
settings = Settings()