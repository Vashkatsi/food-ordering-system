import uuid

from domain.models.order_item import OrderItem
from domain.services.order_domain_service import OrderDomainService
from infrastructure.database.order_repository import OrderRepository
from infrastructure.database.outbox_repository import OutboxRepository


class PlaceOrderUseCase:
    def __init__(
            self,
            order_repository: OrderRepository,
            outbox_repository: OutboxRepository,
            domain_service: OrderDomainService
    ):
        self.order_repository = order_repository
        self.outbox_repository = outbox_repository
        self.domain_service = domain_service

    def execute(self, order_items: list[OrderItem]):
        order_id = str(uuid.uuid4())
        new_order, order_created_event = self.domain_service.create_order(order_id, order_items)

        connection = None
        try:
            connection = self.order_repository.get_connection()
            with connection.cursor() as cursor:
                self.order_repository.save_order_in_transaction(cursor, new_order)
                self.outbox_repository.save_event_in_transaction(
                    cursor,
                    event_type="OrderCreatedEvent",
                    payload={
                        "order_id": order_created_event.order_id,
                        "total_price": order_created_event.total_price
                    }
                )
            connection.commit()
        except Exception:
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()

        return new_order
