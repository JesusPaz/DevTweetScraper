"""Add replies, reposts, and bookmarks to tweets

Revision ID: 0b4a5ee21e82
Revises: cd57d60c9eaf
Create Date: 2025-02-02 21:23:02.264789

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b4a5ee21e82'
down_revision: Union[str, None] = 'cd57d60c9eaf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tweets', sa.Column('replies', sa.Integer(), nullable=True))
    op.add_column('tweets', sa.Column('bookmarks', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tweets', 'bookmarks')
    op.drop_column('tweets', 'replies')
    # ### end Alembic commands ###
