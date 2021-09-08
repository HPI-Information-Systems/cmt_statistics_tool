from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

from vldb.tables.metareview import (  # noqa: E402
    RevisionMetareview,
    SubmissionMetareview,
)
from vldb.tables.paper import Revision, Submission  # noqa: E402
from vldb.tables.people import People, RevisionPeople, SubmissionPeople  # noqa: E402
from vldb.tables.review import RevisionReview, SubmissionReview  # noqa: E402
from vldb.tables.seniormetareview import (  # noqa: E402
    RevisionSeniormetareview,
    SubmissionSeniormetareview,
)

engine = create_async_engine(
    "postgresql+asyncpg://postgres:root@localhost/vldb_2021", echo=False
)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession, autoflush=False
)

__all__ = (
    "Base",
    "RevisionMetareview",
    "SubmissionMetareview",
    "Revision",
    "Submission",
    "People",
    "SubmissionPeople",
    "RevisionPeople",
    "RevisionReview",
    "SubmissionReview",
    "RevisionSeniormetareview",
    "SubmissionSeniormetareview",
    "engine",
    "async_session",
)
