import json

from kafka import KafkaConsumer

from application.use_cases.cancel_order import CancelOrderUseCase
from application.use_cases.mark_order_failed import MarkOrderFailedUseCase
from application.use_cases.mark_order_paid import MarkOrderPaidUseCase


class PaymentEventConsumer:
    def __init__(
            self,
            kafka_config: dict,
            mark_order_paid_use_case: MarkOrderPaidUseCase,
            mark_order_failed_use_case: MarkOrderFailedUseCase,
            cancel_order_use_case: CancelOrderUseCase
    ):
        self.consumer = KafkaConsumer(
            "payment_response_topic",
            bootstrap_servers=kafka_config["bootstrap_servers"],
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            group_id="order_microservice",
            api_version=(2, 6, 0)
        )
        self.mark_order_paid_use_case = mark_order_paid_use_case
        self.mark_order_failed_use_case = mark_order_failed_use_case
        self.cancel_order_use_case = cancel_order_use_case

    def run(self):
        for message in self.consumer:
            event = message.value
            status = event.get("status")
            order_id = event.get("order_id")
            if status == "COMPLETED":
                self.mark_order_paid_use_case.execute(order_id)
            elif status == "FAILED":
                self.mark_order_failed_use_case.execute(order_id)
            elif status == "CANCELLED":
                self.cancel_order_use_case.execute(order_id)
