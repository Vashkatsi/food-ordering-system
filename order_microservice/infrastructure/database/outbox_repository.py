import json
from datetime import datetime

import psycopg2
import psycopg2.extras


class OutboxRepository:
    def __init__(self, db_config):
        self.db_config = db_config

    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def save_event_in_transaction(self, cursor, event_type: str, payload: dict):
        insert_outbox = """
            INSERT INTO outbox (event_type, payload, occurred_at)
            VALUES (%s, %s, %s)
        """
        cursor.execute(
            insert_outbox,
            (event_type, json.dumps(payload), datetime.utcnow())
        )

    def save_event(self, event_type: str, payload: dict):
        connection = psycopg2.connect(**self.db_config)
        try:
            with connection.cursor() as cursor:
                insert_outbox = """
                    INSERT INTO outbox (event_type, payload, occurred_at)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_outbox, (
                    event_type,
                    json.dumps(payload),
                    datetime.utcnow()
                ))
            connection.commit()
        finally:
            connection.close()

    def get_unprocessed_events(self, limit=10, max_retries=3):
        connection = self.get_connection()
        try:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                query = """
                    SELECT id, event_type, payload, retry_count 
                    FROM outbox 
                    WHERE processed = FALSE 
                      AND retry_count < %s
                    ORDER BY id ASC
                    LIMIT %s
                """
                cursor.execute(query, (max_retries, limit))
                return cursor.fetchall()
        finally:
            connection.close()

    def mark_processed(self, outbox_id: int):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                update_sql = "UPDATE outbox SET processed = TRUE WHERE id = %s"
                cursor.execute(update_sql, (outbox_id,))
            connection.commit()
        finally:
            connection.close()

    def increment_retry_count(self, outbox_id: int, error_message: str):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                update_sql = """
                    UPDATE outbox
                    SET retry_count = retry_count + 1,
                        last_error = %s
                    WHERE id = %s
                """
                cursor.execute(update_sql, (error_message[:200], outbox_id))
            connection.commit()
        finally:
            connection.close()

    def mark_dead_letter(self, outbox_id: int, error_message: str):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                update_sql = """
                    UPDATE outbox
                    SET processed = TRUE,
                        last_error = %s
                    WHERE id = %s
                """
                cursor.execute(update_sql, (f"DEAD_LETTER: {error_message[:200]}", outbox_id))
            connection.commit()
        finally:
            connection.close()
