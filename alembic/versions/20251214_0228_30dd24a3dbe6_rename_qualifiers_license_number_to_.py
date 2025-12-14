"""rename qualifiers license_number to qualifier_id_number

Revision ID: 30dd24a3dbe6
Revises: 20251214_0100
Create Date: 2025-12-14 02:28:59.512049

Renames license_number to qualifier_id_number ONLY in qualifiers table.
Licensed businesses keep license_number (that's correct - businesses have license numbers).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30dd24a3dbe6'
down_revision: Union[str, None] = '20251214_0100'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename qualifiers.license_number to qualifier_id_number (this is the NCLBGC Qualifier ID)
    op.alter_column('qualifiers', 'license_number', new_column_name='qualifier_id_number')
    
    # Drop old index
    op.drop_index('ix_qualifiers_license_number', table_name='qualifiers')
    
    # Create new index with updated column name
    op.create_index('ix_qualifiers_qualifier_id_number', 'qualifiers', ['qualifier_id_number'])


def downgrade() -> None:
    # Revert qualifiers
    op.drop_index('ix_qualifiers_qualifier_id_number', table_name='qualifiers')
    op.alter_column('qualifiers', 'qualifier_id_number', new_column_name='license_number')
    op.create_index('ix_qualifiers_license_number', 'qualifiers', ['license_number'])
