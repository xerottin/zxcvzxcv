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
    special_instructions: Mapped[str] = mapped_column(String(500), nullable=True)
    delivery_address: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, name="order_status", create_type=True), default=OrderStatus.PENDING,
        nullable=False
    )
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    branch_id: Mapped[int] = mapped_column(ForeignKey("branch.id"))

    user: Mapped["User"] = relationship("User", back_populates="order")
    branch: Mapped["Branch"] = relationship("Branch", back_populates="order")

    # def __repr__(self):
    #     return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status.value})>"


