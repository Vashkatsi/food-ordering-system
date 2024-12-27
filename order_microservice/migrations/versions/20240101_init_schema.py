from alembic import op

revision = "20241227_init_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE order_table
        (
            order_id    VARCHAR NOT NULL
                CONSTRAINT order_pk
                    PRIMARY KEY,
            status      VARCHAR,
            total_price NUMERIC
        );
    """)

    op.execute("""
        CREATE TABLE order_item
        (
            order_id   VARCHAR NOT NULL,
            product_id VARCHAR NOT NULL,
            quantity   INTEGER,
            unit_price NUMERIC,
            CONSTRAINT order_item_pk
                PRIMARY KEY (product_id, order_id)
        );
    """)

    op.execute("""
        CREATE TABLE outbox
        (
            id          SERIAL PRIMARY KEY,
            event_type  VARCHAR   NOT NULL,
            payload     TEXT      NOT NULL,
            occurred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            processed   BOOLEAN   NOT NULL DEFAULT FALSE,
            retry_count INT       NOT NULL DEFAULT 0,
            last_error  TEXT
        );
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS outbox;")
    op.execute("DROP TABLE IF EXISTS order_item;")
    op.execute("DROP TABLE IF EXISTS order_table;")
