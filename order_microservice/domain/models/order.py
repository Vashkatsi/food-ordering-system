from domain.models.order_item import OrderItem


class Order:
    def __init__(self, order_id: str, order_items: list[OrderItem]):
        self.order_id = order_id
        self.order_items = order_items
        self.status = "CREATED"
        self.total_price = sum(item.quantity * item.unit_price for item in order_items)

    def mark_as_paid(self):
        self.status = "PAID"

    def mark_as_canceled(self):
        self.status = "CANCELED"

    def mark_as_failed(self):
        self.status = "FAILED"

    def get_total_price(self):
        return self.total_price
