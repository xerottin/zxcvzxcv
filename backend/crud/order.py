import logging

logger = logging.getLogger(__name__)


async def create_order(db: AsyncSession, data: OrderCreate, user_id: str) -> Order:
    
    db_order = Order(
        user_id=user_id,
        customer_name=data.customer_name,
        customer_email=data.customer_email,
        customer_phone=data.customer_phone,
        shipping_address=data.shipping_address,
        notes=data.notes
    )
    
    total_amount = 0.0
    order_items = []
    
    for item_data in data.items:
        total_price = item_data.quantity * item_data.unit_price
        total_amount += total_price
        
        order_item = OrderItem(
            product_name=item_data.product_name,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=total_price
        )
        order_items.append(order_item)
    
    db_order.total_amount = total_amount
    db_order.items = order_items
    
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == db_order.id)
    )
    return result.scalar_one()
        

