from domain.events.order_created_event import OrderCreatedEvent
from domain.models.order import Order

from domain.models.order_item import OrderItem


class OrderDomainService:
    def create_order(self, order_id: str, order_items: list[OrderItem]) -> (Order, OrderCreatedEvent):
        new_order = Order(order_id, order_items)
        event = OrderCreatedEvent(order_id, new_order.get_total_price())
        return new_order, event
