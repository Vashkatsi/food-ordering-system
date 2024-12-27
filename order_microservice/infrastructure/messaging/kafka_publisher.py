import json

from kafka import KafkaProducer


class KafkaPublisher:
    def __init__(self, kafka_config):
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_config["bootstrap_servers"],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            api_version=(2, 6, 0)
        )

    def publish(self, topic: str, message: dict):
        self.producer.send(topic, message)
        self.producer.flush()
