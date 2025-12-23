"""Add image_url and shopping_url to products

Revision ID: add_image_shopping_url
Revises: 907f1ad809ec
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "add_image_shopping_url"
down_revision: Union[str, None] = "907f1ad809ec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add image_url and shopping_url columns to cat_food_product table."""
    op.execute(
        """
        ALTER TABLE cat_food_product 
        ADD COLUMN image_url VARCHAR,
        ADD COLUMN shopping_url VARCHAR
        """
    )


def downgrade() -> None:
    """Remove image_url and shopping_url columns from cat_food_product table."""
    op.execute(
        """
        ALTER TABLE cat_food_product 
        DROP COLUMN IF EXISTS image_url,
        DROP COLUMN IF EXISTS shopping_url
        """
    )

