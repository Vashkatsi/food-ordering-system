import uuid

from domain.models.order_item import OrderItem
from domain.services.order_domain_service import OrderDomainService
from infrastructure.database.order_repository import OrderRepository
from infrastructure.messaging.kafka_publisher import KafkaPublisher


class PlaceOrderUseCase:
    def __init__(
            self, order_repository: OrderRepository,
            domain_service: OrderDomainService,
            kafka_publisher: KafkaPublisher
    ):
        self.order_repository = order_repository
        self.domain_service = domain_service
        self.kafka_publisher = kafka_publisher

    def execute(self, order_items: list[OrderItem]):
        order_id = str(uuid.uuid4())
        new_order, order_event = self.domain_service.create_order(order_id, order_items)
        self.order_repository.save_order(new_order)

        # TODO implement transactional outbox
        self.kafka_publisher.publish("order_created_topic", {
            "order_id": order_event.order_id,
            "total_price": order_event.total_price
        })

        return new_order
