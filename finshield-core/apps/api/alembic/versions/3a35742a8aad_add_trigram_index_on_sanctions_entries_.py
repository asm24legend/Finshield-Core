"""add trigram index on sanctions_entries name

Revision ID: 3a35742a8aad
Revises: afe372661dab
Create Date: 2026-09-02 14:30:51.565502

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a35742a8aad'
down_revision: Union[str, Sequence[str], None] = 'afe372661dab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
