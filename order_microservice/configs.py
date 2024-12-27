from typing import Annotated

from fastapi import Depends

from application.use_cases.cancel_order import CancelOrderUseCase
from application.use_cases.mark_order_failed import MarkOrderFailedUseCase
from application.use_cases.mark_order_paid import MarkOrderPaidUseCase
from application.use_cases.place_order import PlaceOrderUseCase
from domain.services.order_domain_service import OrderDomainService
from infrastructure.database.order_repository import OrderRepository
from infrastructure.database.outbox_repository import OutboxRepository
from infrastructure.messaging.kafka_publisher import KafkaPublisher

db_config = {
    "dbname": "order_db",
    "user": "postgres",
    "password": "postgres",
    "host": "order_db",
    "port": 5432
}
kafka_config = {
    "bootstrap_servers": "kafka:9092"
}
kafka_topic_map = {
    "OrderCreatedEvent": "order_created_topic",
}

order_repository = OrderRepository(db_config)
outbox_repository = OutboxRepository(db_config)
kafka_publisher = KafkaPublisher(kafka_config)
domain_service = OrderDomainService()

mark_paid_use_case = MarkOrderPaidUseCase(order_repository, outbox_repository)
mark_failed_use_case = MarkOrderFailedUseCase(order_repository, outbox_repository)
cancel_order_use_case = CancelOrderUseCase(order_repository, outbox_repository)


def get_place_order_use_case() -> PlaceOrderUseCase:
    return PlaceOrderUseCase(
        order_repository=order_repository,
        domain_service=domain_service,
        outbox_repository=outbox_repository
    )


PlaceOrderUseCaseDep = Annotated[PlaceOrderUseCase, Depends(get_place_order_use_case)]
