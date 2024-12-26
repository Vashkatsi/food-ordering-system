class OrderCreatedEvent:
    def __init__(self, order_id: str, total_price: float):
        self.order_id = order_id
        self.total_price = total_price
