import json
import time
import uuid

from infrastructure.database.outbox_repository import OutboxRepository
from infrastructure.messaging.kafka_publisher import KafkaPublisher


class OutboxProcessor:
    def __init__(self, outbox_repository: OutboxRepository, kafka_publisher: KafkaPublisher, topic_map: dict):
        self.outbox_repository = outbox_repository
        self.kafka_publisher = kafka_publisher
        self.topic_map = topic_map
        self.max_retries = 3

    def run(self):
        while True:
            events = self.outbox_repository.get_unprocessed_events(limit=10, max_retries=self.max_retries)
            if not events:
                time.sleep(5)
                continue
            for record in events:
                outbox_id = record["id"]
                event_type = record["event_type"]
                payload = json.loads(record["payload"])
                retry_count = record["retry_count"]
                event_id = payload.get("event_id")
                if not event_id:
                    event_id = str(uuid.uuid4())
                    payload["event_id"] = event_id
                topic = self.topic_map.get(event_type)
                if not topic:
                    self.outbox_repository.mark_processed(outbox_id)
                    continue
                try:
                    self.kafka_publisher.publish(topic, payload)
                    self.outbox_repository.mark_processed(outbox_id)
                except Exception as e:
                    if retry_count + 1 >= self.max_retries:
                        self.outbox_repository.mark_dead_letter(outbox_id, str(e))
                    else:
                        self.outbox_repository.increment_retry_count(outbox_id, str(e))
            time.sleep(1)
