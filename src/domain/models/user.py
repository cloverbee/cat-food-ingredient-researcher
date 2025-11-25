from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from src.core.database import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "user"
