
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    openid: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    nickname: Mapped[str] = mapped_column(String, nullable=True)
    phone: Mapped[str] = mapped_column(String, nullable=True)
    point_balance: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    point_logs = relationship("UserPointLog", back_populates="user")
