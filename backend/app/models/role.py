from typing import List
from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.postgres import Base

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    permissions: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    users: Mapped[List["User"]] = relationship("User", back_populates="role")
