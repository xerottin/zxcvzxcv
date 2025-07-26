import enum

from sqlalchemy import Integer, ForeignKey, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel


class OrderStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(BaseModel):
    __tablename__ = "order"
    username: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    menu_item_id: Mapped[int] = mapped_column(Integer, ForeignKey('menu_item.id'), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, name="order_status", create_type=True), default=OrderStatus.PENDING,
        nullable=False
    )

    special_instructions: Mapped[str] = mapped_column(String(500), nullable=True)
    delivery_address: Mapped[str] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="order")
    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="order")

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status.value})>"
