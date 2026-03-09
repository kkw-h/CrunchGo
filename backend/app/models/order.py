
from sqlalchemy import Integer, String, ForeignKey, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    order_no: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String, index=True, nullable=False) # PENDING, PAID, PREPARING, REFUNDING, REFUNDED, CANCELLED, COMPLETED
    pickup_code: Mapped[str] = mapped_column(String, nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=False) # DINE_IN, PICKUP

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    payment = relationship("Payment", back_populates="order", uselist=False)

class OrderItem(Base, TimestampMixin):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_no: Mapped[str] = mapped_column(String, ForeignKey("orders.order_no"), nullable=False)
    product_sku_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_skus.id"), nullable=True)
    product_name_snapshot: Mapped[str] = mapped_column(String, nullable=False)
    specs_snapshot: Mapped[str] = mapped_column(String, nullable=True)
    price_snapshot: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    order = relationship("Order", back_populates="items")
