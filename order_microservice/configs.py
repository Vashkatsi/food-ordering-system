from typing import Annotated
from fastapi import Depends

from application.use_cases.place_order import PlaceOrderUseCase
from domain.services.order_domain_service import OrderDomainService
from infrastructure.database.order_repository import OrderRepository
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

order_repository = OrderRepository(db_config)
kafka_publisher = KafkaPublisher(kafka_config)
domain_service = OrderDomainService()


def get_place_order_use_case() -> PlaceOrderUseCase:
    return PlaceOrderUseCase(
        order_repository=order_repository,
        domain_service=domain_service,
        kafka_publisher=kafka_publisher
    )


PlaceOrderUseCaseDep = Annotated[PlaceOrderUseCase, Depends(get_place_order_use_case)]
