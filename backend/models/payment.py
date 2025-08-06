import enum
from sqlalchemy import Enum as SAEnum, String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models import BaseModel


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(enum.Enum):
    CARD = "card"
    WALLET = "wallet"
    BANK_TRANSFER = "bank_transfer"


class Payment(BaseModel):
    __tablename__ = "payment"
    
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), nullable=False, index=True)
    stripe_payment_intent_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # Amount in cents
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus, name="payment_status", create_type=True),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        SAEnum(PaymentMethod, name="payment_method", create_type=True),
        nullable=True
    )
    stripe_client_secret: Mapped[str] = mapped_column(String(255), nullable=True)
    failure_reason: Mapped[str] = mapped_column(Text, nullable=True)
    receipt_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    order: Mapped["Order"] = relationship("Order", back_populates="payment")
