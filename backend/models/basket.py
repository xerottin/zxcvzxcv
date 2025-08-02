from sqlalchemy import ForeignKey, Integer, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from models.base import BaseModel


class Basket(BaseModel):
    __tablename__ = "basket"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_item.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    menu_item = relationship("MenuItem", back_populates="basket")
    user = relationship("User", back_populates="basket_item")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'menu_item_id', name='uq_user_menu_item'),
        CheckConstraint('quantity > 0', name='ck_quantity_positive'),
        CheckConstraint('quantity <= 99', name='ck_quantity_reasonable'),
    )
    
    def __repr__(self) -> str:
        return f"<Basket(id={self.id}, user_id={self.user_id}, menu_item_id={self.menu_item_id}, quantity={self.quantity})>"