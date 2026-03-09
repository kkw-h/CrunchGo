
from sqlalchemy import Integer, String, ForeignKey, DECIMAL, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin
from datetime import datetime

class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_no: Mapped[str] = mapped_column(String, ForeignKey("orders.order_no"), unique=True, nullable=False)
    transaction_id: Mapped[str] = mapped_column(String, index=True, nullable=True)
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False) # PENDING, SUCCESS, FAILED
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    order = relationship("Order", back_populates="payment")
