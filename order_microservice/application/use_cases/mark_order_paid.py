from domain.events.order_paid_event import OrderPaidEvent
from infrastructure.database.order_repository import OrderRepository
from infrastructure.database.outbox_repository import OutboxRepository


class MarkOrderPaidUseCase:
    def __init__(self, order_repository: OrderRepository,
                 outbox_repository: OutboxRepository):
        self.order_repository = order_repository
        self.outbox_repository = outbox_repository

    def execute(self, order_id: str):
        connection = None
        try:
            connection = self.order_repository.get_connection()
            with connection.cursor() as cursor:
                order = self.order_repository.find_order_in_transaction(cursor, order_id)
                if not order:
                    return

                order.mark_as_paid()
                self.order_repository.update_order_in_transaction(cursor, order)

                event = OrderPaidEvent(order.order_id)
                self.outbox_repository.save_event_in_transaction(
                    cursor,
                    "OrderPaidEvent",
                    {"order_id": event.order_id}
                )
            connection.commit()
        except Exception:
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
