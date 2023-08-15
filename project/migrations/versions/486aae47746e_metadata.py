"""metadata

Revision ID: 486aae47746e
Revises: 842abcd80d3e
Create Date: 2023-08-12 17:10:51.042627

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel  # NEW


# revision identifiers, used by Alembic.
revision = "486aae47746e"
down_revision = "842abcd80d3e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "shazam_metadata",
        sa.Column(
            "youtube_id",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("genre", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("lyrics", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["youtube_id"],
            ["youtube_metadata.id"],
        ),
        sa.PrimaryKeyConstraint("youtube_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("shazam_metadata")
    # ### end Alembic commands ###
