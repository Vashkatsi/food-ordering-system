from configs import PlaceOrderUseCaseDep
from domain.models.order_item import OrderItem
from fastapi import APIRouter
from pydantic import BaseModel

order_router = APIRouter()


class OrderItemInput(BaseModel):
    product_id: str
    quantity: int
    unit_price: float


class PlaceOrderInput(BaseModel):
    items: list[OrderItemInput]


@order_router.post("/orders")
def place_order(
        input_data: PlaceOrderInput,
        place_order_use_case: PlaceOrderUseCaseDep
):
    order_items = [
        OrderItem(product_id=item.product_id, quantity=item.quantity, unit_price=item.unit_price)
        for item in
        input_data.items
    ]
    created_order = place_order_use_case.execute(order_items)

    return {
        "order_id": created_order.order_id,
        "status": created_order.status,
        "total_price": created_order.get_total_price()
    }
