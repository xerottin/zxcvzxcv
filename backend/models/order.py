import enum

from models import BaseModel
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OrderStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(BaseModel):
    __tablename__ = "order"
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branch.id"), nullable=False)
    special_instructions: Mapped[str] = mapped_column(String(500), nullable=True)
    delivery_address: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, name="order_status", create_type=True),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True,
    )
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    branch: Mapped["Branch"] = relationship("Branch", back_populates="order")
    user: Mapped["User"] = relationship("User", back_populates="order")
    order_item: Mapped["OrderItem"] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    # def __repr__(self):
    #     return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status.value})>"


class OrderItem(BaseModel):
    __tablename__ = "order_item"
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), nullable=False)
    menu_item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_item.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    total_price: Mapped[int] = mapped_column(Integer, nullable=False)

    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="order_item")
    order: Mapped["Order"] = relationship("Order", back_populates="order_item")
