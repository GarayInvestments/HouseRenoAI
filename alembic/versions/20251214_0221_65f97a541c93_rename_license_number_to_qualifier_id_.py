"""rename license_number to qualifier_id_number

Revision ID: 65f97a541c93
Revises: 20251214_0100
Create Date: 2025-12-14 02:21:48.265597

Renames license_number column to qualifier_id_number to match NCLBGC portal terminology.
This applies to both the qualifiers table and licensed_businesses table.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65f97a541c93'
down_revision: Union[str, None] = '20251214_0100'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename qualifiers.license_number to qualifier_id_number
    op.alter_column('qualifiers', 'license_number', new_column_name='qualifier_id_number')
    
    # Drop old index
    op.drop_index('ix_qualifiers_license_number', table_name='qualifiers')
    
    # Create new index with updated column name
    op.create_index('ix_qualifiers_qualifier_id_number', 'qualifiers', ['qualifier_id_number'])
    
    # Rename licensed_businesses.license_number to qualifier_id_number (this is the NCLBGC business license number)
    op.alter_column('licensed_businesses', 'license_number', new_column_name='qualifier_id_number')
    
    # Drop old index
    op.drop_index('ix_licensed_businesses_license_number', table_name='licensed_businesses')
    
    # Create new index with updated column name
    op.create_index('ix_licensed_businesses_qualifier_id_number', 'licensed_businesses', ['qualifier_id_number'])
    
    # Update permits.license_number_used column name to qualifier_id_number_used for consistency
    op.alter_column('permits', 'license_number_used', new_column_name='qualifier_id_number_used')


def downgrade() -> None:
    # Revert permits column
    op.alter_column('permits', 'qualifier_id_number_used', new_column_name='license_number_used')
    
    # Revert licensed_businesses
    op.drop_index('ix_licensed_businesses_qualifier_id_number', table_name='licensed_businesses')
    op.alter_column('licensed_businesses', 'qualifier_id_number', new_column_name='license_number')
    op.create_index('ix_licensed_businesses_license_number', 'licensed_businesses', ['license_number'])
    
    # Revert qualifiers
    op.drop_index('ix_qualifiers_qualifier_id_number', table_name='qualifiers')
    op.alter_column('qualifiers', 'qualifier_id_number', new_column_name='license_number')
    op.create_index('ix_qualifiers_license_number', 'qualifiers', ['license_number'])
