import logging
from typing import Optional
from sqlmodel import SQLModel, Field, BigInteger, Column, Relationship
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import DBAPIError
from app.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class YoutubeMetadata(SQLModel, table=True):
    """
    A class representing YouTube video metadata to be stored in the database.
    """

    __tablename__ = "youtube_metadata"
    id: str = Field(default=None, nullable=False, primary_key=True)
    title: str
    author: str
    views: int = Field(default=None, sa_column=Column(BigInteger()))
    shazam_metadata: "ShazamMetadata" = Relationship(back_populates="youtube_metadata")

    async def save(self, session: AsyncSession):
        """
        Save the YoutubeMetadata instance to the database.

        Args:
            session (AsyncSession): The database session to use.

        Raises:
            DatabaseError: If an error occurs while saving to the database.
        """
        try:
            session.add(self)
            await session.commit()
            await session.refresh(self)
        except DBAPIError as e:
            raise DatabaseError(
                f"An error occurred while saving to the database: {str(e)}"
            )


class ShazamMetadata(SQLModel, table=True):
    """
    A class representing Shazam metadata associated with a YouTube video.
    """

    __tablename__ = "shazam_metadata"
    youtube_id: str = Field(
        default=None,
        nullable=False,
        foreign_key="youtube_metadata.id",
        primary_key=True,
    )
    title: str
    genre: str
    lyrics: Optional[str]

    youtube_metadata: YoutubeMetadata = Relationship(back_populates="shazam_metadata")

    async def save(self, session: AsyncSession):
        """
        Save the ShazamMetadata instance to the database.

        Args:
            session (AsyncSession): The database session to use.

        Raises:
            DatabaseError: If an error occurs while saving to the database.
        """
        try:
            session.add(self)
            await session.commit()
            await session.refresh(self)
        except DBAPIError as e:
            raise DatabaseError(
                f"An error occurred while saving to the database: {str(e)}"
            )
