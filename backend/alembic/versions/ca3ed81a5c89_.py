"""empty message

Revision ID: ca3ed81a5c89
Revises: 8f711b6ead1d
Create Date: 2025-02-26 16:46:19.982746

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca3ed81a5c89'
down_revision: Union[str, None] = '8f711b6ead1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('admin', 'test')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('admin', sa.Column('test', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
