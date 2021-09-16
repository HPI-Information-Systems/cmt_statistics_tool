from typing import TYPE_CHECKING

from sqlalchemy import Column, Text
from sqlalchemy.orm import Mapped, declarative_mixin, declared_attr, relationship
from sqlalchemy.sql.schema import ForeignKey

from cmt_statistics_tool.tables import Base

if TYPE_CHECKING:
    from cmt_statistics_tool.tables.paper import Revision, Submission
    from cmt_statistics_tool.tables.people import People


@declarative_mixin
class Review:
    __abstract__ = True
    __tablename__ = "review"

    @declared_attr
    def reviewer_id(cls) -> Mapped[int]:
        return Column(ForeignKey("people.id"), primary_key=True, nullable=False)


@declarative_mixin
class SubmissionReviewBase(Review):
    __abstract__ = True
    __tablename__ = "submission_review_base"

    @declared_attr
    def submission_id(cls) -> Mapped[int]:
        return Column(ForeignKey("submission.id"), primary_key=True, nullable=False)


@declarative_mixin
class RevisionReviewBase(Review):
    __abstract__ = True
    __tablename__ = "revision_review_base"

    @declared_attr
    def revision_id(cls) -> Mapped[int]:
        return Column(ForeignKey("revision.id"), primary_key=True, nullable=False)


class SubmissionReview(Base, SubmissionReviewBase):
    __tablename__ = "submission_review"

    overall_rating: str = Column(Text, nullable=False)
    relevance: str = Column(Text, nullable=False)
    revision_possible: str = Column(Text, nullable=False)
    paper_flavor: str = Column(Text, nullable=False)
    summary: str = Column(Text, nullable=False)
    strengths: str = Column(Text, nullable=False)
    weaknesses: str = Column(Text, nullable=False)
    novelty: str = Column(Text, nullable=False)
    significance: str = Column(Text, nullable=False)
    technical_depth: str = Column(Text, nullable=False)
    experiments: str = Column(Text, nullable=False)
    presentation: str = Column(Text, nullable=False)
    details: str = Column(Text, nullable=False)
    reproducibility: str = Column(Text, nullable=False)
    revision_items: str = Column(Text, nullable=False)
    confidence: str = Column(Text, nullable=False)
    confidential_comments: str = Column(Text, nullable=False)
    external_reviewer: str = Column(Text, nullable=False)
    trainee_agreement: str = Column(Text, nullable=False)

    submission: "Submission" = relationship("Submission", back_populates="reviews")
    reviewer: "People" = relationship("People", back_populates="submission_reviews")


class RevisionReview(Base, RevisionReviewBase):
    __tablename__ = "revision_review"

    recommendation: str = Column(Text, nullable=False)
    revision_addressed: str = Column(Text, nullable=False)
    justification: str = Column(Text, nullable=False)
    comments_authors: str = Column(Text, nullable=False)
    confidential_comments: str = Column(Text, nullable=False)

    revision: "Revision" = relationship("Revision", back_populates="reviews")
    reviewer: "People" = relationship("People", back_populates="revision_reviews")
