"""Add style statistics details

Revision ID: 60de8beebe9c
Revises: 9749742d9bf4
Create Date: 2025-01-20 13:00:18.421047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60de8beebe9c'
down_revision: Union[str, None] = '9749742d9bf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('style_statistics', sa.Column('examples', sa.JSON(), nullable=True))
    op.add_column('style_statistics', sa.Column('page_distribution', sa.JSON(), nullable=True))
    op.add_column('style_statistics', sa.Column('y_range', sa.JSON(), nullable=True))
    op.add_column('style_statistics', sa.Column('x_range', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('style_statistics', 'x_range')
    op.drop_column('style_statistics', 'y_range')
    op.drop_column('style_statistics', 'page_distribution')
    op.drop_column('style_statistics', 'examples')
    # ### end Alembic commands ###
