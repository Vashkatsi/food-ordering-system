class OrderFailedEvent:
    def __init__(self, order_id: str):
        self.order_id = order_id
