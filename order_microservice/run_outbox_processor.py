from configs import outbox_repository, kafka_publisher, kafka_topic_map
from infrastructure.messaging.outbox_processor import OutboxProcessor


def main():
    processor = OutboxProcessor(outbox_repository, kafka_publisher, kafka_topic_map)
    processor.run()


if __name__ == "__main__":
    main()
