from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column
from sqlalchemy import Enum as EnumColumn
from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, declarative_mixin, declared_attr, relationship
from sqlalchemy.sql.schema import ForeignKey

from vldb.tables import Base

if TYPE_CHECKING:
    from vldb.tables.metareview import RevisionMetareview, SubmissionMetareview
    from vldb.tables.paper import Revision, Submission
    from vldb.tables.review import RevisionReview, SubmissionReview
    from vldb.tables.seniormetareview import (
        RevisionSeniormetareview,
        SubmissionSeniormetareview,
    )

PeoplePaperRelation = Enum(
    "PeoplePaperRelation", ("AUTHOR", "REVIEWER", "METAREVIEWER", "SENIORMETAREVIEWER")
)


@declarative_mixin
class PeoplePaperMapping:
    __abstract__ = True
    __tablename__ = "people_paper_mapping"
    relation_type: PeoplePaperRelation = Column(
        EnumColumn(PeoplePaperRelation), primary_key=True
    )

    @declared_attr
    def people_id(cls) -> Mapped[int]:
        return Column(ForeignKey("people.id"), primary_key=True)

    @declared_attr
    def position(cls) -> Mapped[int]:
        return Column(Integer, nullable=False)


class SubmissionPeople(Base, PeoplePaperMapping):
    __tablename__ = "submission_people"
    submission_id: int = Column(ForeignKey("submission.id"), primary_key=True)


class RevisionPeople(Base, PeoplePaperMapping):
    __tablename__ = "revision_people"
    revision_id: int = Column(ForeignKey("revision.id"), primary_key=True)


class People(Base):
    __tablename__ = "people"
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False)
    affiliation: str = Column(String, nullable=False)
    country: Optional[str] = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint(name, email),)

    primary_author_submissions: List["Submission"] = relationship(
        "Submission",
        back_populates="primary_author",
        cascade="all, delete",
    )
    submissions: List["Submission"] = relationship(
        "Submission",
        secondary="submission_people",
        back_populates="people",
        cascade="all, delete",
    )
    primary_author_revisions: List["Revision"] = relationship(
        "Revision",
        back_populates="primary_author",
        cascade="all, delete",
    )
    revisions: List["Revision"] = relationship(
        "Revision",
        secondary="revision_people",
        back_populates="people",
        cascade="all, delete",
    )
    submission_reviews: List["SubmissionReview"] = relationship(
        "SubmissionReview",
        back_populates="reviewer",
        cascade="all, delete",
    )
    revision_reviews: List["RevisionReview"] = relationship(
        "RevisionReview",
        back_populates="reviewer",
        cascade="all, delete",
    )
    submission_metareviews: List["SubmissionMetareview"] = relationship(
        "SubmissionMetareview",
        back_populates="reviewer",
        cascade="all, delete",
    )
    revision_metareviews: List["RevisionMetareview"] = relationship(
        "RevisionMetareview",
        back_populates="reviewer",
        cascade="all, delete",
    )
    submission_seniormetareviews: List["SubmissionSeniormetareview"] = relationship(
        "SubmissionSeniormetareview",
        back_populates="reviewer",
        cascade="all, delete",
    )
    revision_seniormetareviews: List["RevisionSeniormetareview"] = relationship(
        "RevisionSeniormetareview",
        back_populates="reviewer",
        cascade="all, delete",
    )

    def __repr__(self) -> str:
        return f"People(name={self.name}, email={self.email})"
