from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv(override=True)

class DatabaseSettings(BaseSettings):
    host: str = Field(validation_alias="POSTGRES_HOST", default="localhost")
    db: str = Field(validation_alias="POSTGRES_DB", default="sangrahalayamu")
    password: str = Field(validation_alias="POSTGRES_PASSWORD", default="postgres")

ds = DatabaseSettings()
print(f"Host: {ds.host}")
print(f"DB: {ds.db}")
print(f"Pass: {ds.password}")
