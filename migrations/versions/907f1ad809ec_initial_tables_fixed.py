"""Initial tables fixed

Revision ID: 907f1ad809ec
Revises: 4f2ae0db5bdd
Create Date: 2025-11-24 14:06:10.323144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '907f1ad809ec'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    CREATE TABLE cat_food_product (
        id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        brand VARCHAR NOT NULL,
        price FLOAT,
        age_group VARCHAR,
        food_type VARCHAR,
        description TEXT,
        full_ingredient_list TEXT,
        embedding_id VARCHAR
    )
    """)
    op.execute("CREATE INDEX ix_cat_food_product_age_group ON cat_food_product (age_group)")
    op.execute("CREATE INDEX ix_cat_food_product_brand ON cat_food_product (brand)")
    op.execute("CREATE INDEX ix_cat_food_product_food_type ON cat_food_product (food_type)")
    op.execute("CREATE INDEX ix_cat_food_product_id ON cat_food_product (id)")
    op.execute("CREATE INDEX ix_cat_food_product_name ON cat_food_product (name)")

    op.execute("""
    CREATE TABLE ingredient (
        id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        description TEXT,
        nutritional_value JSONB,
        common_allergens JSONB
    )
    """)
    op.execute("CREATE INDEX ix_ingredient_id ON ingredient (id)")
    op.execute("CREATE UNIQUE INDEX ix_ingredient_name ON ingredient (name)")

    op.execute("""
    CREATE TABLE "user" (
        id UUID NOT NULL,
        email VARCHAR(320) NOT NULL,
        hashed_password VARCHAR(1024) NOT NULL,
        is_active BOOLEAN NOT NULL,
        is_superuser BOOLEAN NOT NULL,
        is_verified BOOLEAN NOT NULL,
        PRIMARY KEY (id)
    )
    """)
    op.execute('CREATE UNIQUE INDEX ix_user_email ON "user" (email)')

    op.execute("""
    CREATE TABLE product_ingredient_association (
        product_id INTEGER NOT NULL,
        ingredient_id INTEGER NOT NULL,
        PRIMARY KEY (product_id, ingredient_id),
        FOREIGN KEY (product_id) REFERENCES cat_food_product(id),
        FOREIGN KEY (ingredient_id) REFERENCES ingredient(id)
    )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE product_ingredient_association")
    op.execute('DROP TABLE "user"')
    op.execute("DROP TABLE ingredient")
    op.execute("DROP TABLE cat_food_product")
