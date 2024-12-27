from domain.events.order_failed_event import OrderFailedEvent
from infrastructure.database.order_repository import OrderRepository
from infrastructure.database.outbox_repository import OutboxRepository


class MarkOrderFailedUseCase:
    def __init__(self, order_repository: OrderRepository, outbox_repository: OutboxRepository):
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
                order.mark_as_failed()
                self.order_repository.update_order_in_transaction(cursor, order)
                event = OrderFailedEvent(order.order_id)
                self.outbox_repository.save_event_in_transaction(
                    cursor,
                    "OrderFailedEvent",
                    {"order_id": event.order_id}
                )
            connection.commit()
        except:
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
