from enum import Enum

from domain.models.order_item import OrderItem


class OrderStatus(Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class InvalidStateTransitionError(Exception):
    pass


class Order:
    STATES = {
        OrderStatus.CREATED: {OrderStatus.PAID, OrderStatus.FAILED, OrderStatus.CANCELED},
        OrderStatus.PAID: {OrderStatus.FAILED, OrderStatus.CANCELED},
        OrderStatus.FAILED: set(),
        OrderStatus.CANCELED: set(),
    }

    def __init__(self, order_id: str, order_items: list[OrderItem]):
        self.order_id = order_id
        self.order_items = order_items
        self.status = OrderStatus.CREATED
        self.total_price = sum(item.quantity * item.unit_price for item in order_items)

    def _change_status(self, new_status: OrderStatus):
        if new_status not in Order.STATES[self.status]:
            raise InvalidStateTransitionError(f"Cannot transition from {self.status.value} to {new_status.value}")
        self.status = new_status

    def mark_as_paid(self):
        self._change_status(OrderStatus.PAID)

    def mark_as_failed(self):
        self._change_status(OrderStatus.FAILED)

    def mark_as_canceled(self):
        self._change_status(OrderStatus.CANCELED)

    def get_total_price(self):
        return self.total_price
