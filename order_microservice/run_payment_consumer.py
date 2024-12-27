from configs import kafka_config, mark_paid_use_case, cancel_order_use_case, mark_failed_use_case
from infrastructure.messaging.kafka_consumer import PaymentEventConsumer


def main():
    consumer = PaymentEventConsumer(kafka_config, mark_paid_use_case, mark_failed_use_case, cancel_order_use_case)
    consumer.run()


if __name__ == "__main__":
    main()
