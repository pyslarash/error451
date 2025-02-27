"""empty message

Revision ID: 1f3fe30b6153
Revises: 267fd06da6e1
Create Date: 2025-02-26 21:59:18.146721

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f3fe30b6153'
down_revision: Union[str, None] = '267fd06da6e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('list', sa.Column('expiration_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('list', 'expiration_date')
    # ### end Alembic commands ###
