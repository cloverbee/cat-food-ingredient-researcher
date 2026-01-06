"""Delete dog food products from database

Revision ID: delete_dog_food
Revises: add_image_shopping_url
Create Date: 2024-12-24

This is a DATA MIGRATION that removes products containing "dog food" in the name.
WARNING: This migration is NOT fully reversible - deleted data cannot be restored.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "delete_dog_food"
down_revision: Union[str, None] = "add_image_shopping_url"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Delete all products with 'dog food' in the name (case-insensitive)."""
    
    # First, delete from the association table (foreign key constraint)
    op.execute(
        """
        DELETE FROM product_ingredient_association
        WHERE product_id IN (
            SELECT id FROM cat_food_product
            WHERE LOWER(name) LIKE '%dog food%'
        )
        """
    )
    
    # Then, delete the dog food products
    op.execute(
        """
        DELETE FROM cat_food_product
        WHERE LOWER(name) LIKE '%dog food%'
        """
    )


def downgrade() -> None:
    """
    WARNING: This downgrade cannot restore deleted data.
    You would need to re-import the dog food products from CSV/source.
    """
    # Data deletion is not reversible - the data is gone
    # To restore, you would need to re-run the ingestion process
    print("WARNING: Deleted dog food products cannot be automatically restored.")
    print("Please re-import data from your CSV files if needed.")
    pass




