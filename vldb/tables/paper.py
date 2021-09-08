from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, declarative_mixin, declared_attr, relationship
from sqlalchemy.sql.schema import ForeignKey

from vldb.tables import Base

if TYPE_CHECKING:
    from vldb.tables.metareview import RevisionMetareview, SubmissionMetareview
    from vldb.tables.people import People
    from vldb.tables.review import RevisionReview, SubmissionReview
    from vldb.tables.seniormetareview import (
        RevisionSeniormetareview,
        SubmissionSeniormetareview,
    )

SubmissionStatus = Enum(
    "SubmissionStatus",
    (
        "Accept",
        "Minor revision",
        "Major revision",
        "Reject",
        "Desk Reject",
        "Withdrawn",
    ),
)
RevisionStatus = Enum("RevisionStatus", ("Accept", "Awaiting Decision", "Reject"))


@declarative_mixin
class Paper:
    __abstract__ = True
    __tablename__ = "paper"

    id: int = Column(
        Integer, unique=True, primary_key=True, nullable=False, autoincrement=True
    )
    title: str = Column(Text, nullable=False)
    abstract: str = Column(Text, nullable=False)
    track_name: str = Column(Text, nullable=False)
    primary_subject_area: str = Column(Text, nullable=False)
    secondary_subject_areas: str = Column(Text, nullable=False)
    conflicts: int = Column(Integer, nullable=False)
    assigned: int = Column(Integer, nullable=False)
    completed: float = Column(Float, nullable=False)
    bids: int = Column(Integer, nullable=False)
    discussion: str = Column(String(100), nullable=False)
    status: str = Column(String(100), nullable=False)
    embargo_agreement: str = Column(Text, nullable=False)
    conflict_agreement: str = Column(Text, nullable=False)
    category: str = Column(Text, nullable=False)
    authors_agreement: str = Column(Text, nullable=False)
    availability: str = Column(Text, nullable=False)

    @declared_attr
    def primary_author_id(cls) -> Mapped[int]:
        return Column(ForeignKey("people.id"), nullable=False)

    def __repr__(self) -> str:
        return f"Paper(id={self.id}, title={self.title})"


class Submission(Base, Paper):
    __tablename__ = "submission"

    revision: Optional["Revision"] = relationship(
        "Revision", uselist=False, back_populates="submission"
    )
    primary_author: "People" = relationship(
        "People",
        back_populates="primary_author_submissions",
    )
    people: List["People"] = relationship(
        "People", secondary="submission_people", back_populates="submissions"
    )
    reviews: List["SubmissionReview"] = relationship(
        "SubmissionReview", back_populates="submission"
    )
    metareviews: List["SubmissionMetareview"] = relationship(
        "SubmissionMetareview", back_populates="submission"
    )
    seniormetareviews: List["SubmissionSeniormetareview"] = relationship(
        "SubmissionSeniormetareview", back_populates="submission"
    )


class Revision(Base, Paper):
    __tablename__ = "revision"

    submission_id: Optional[int] = Column(ForeignKey("submission.id"), nullable=True)

    submission: Optional["Submission"] = relationship(
        "Submission", back_populates="revision"
    )
    primary_author: "People" = relationship(
        "People",
        back_populates="primary_author_revisions",
    )
    people: List["People"] = relationship(
        "People", secondary="revision_people", back_populates="revisions"
    )
    reviews: List["RevisionReview"] = relationship(
        "RevisionReview", back_populates="revision"
    )
    metareviews: List["RevisionMetareview"] = relationship(
        "RevisionMetareview", back_populates="revision"
    )
    seniormetareviews: List["RevisionSeniormetareview"] = relationship(
        "RevisionSeniormetareview", back_populates="revision"
    )
