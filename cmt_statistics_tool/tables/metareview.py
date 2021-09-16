from typing import TYPE_CHECKING

from sqlalchemy import Column, Text
from sqlalchemy.orm import relationship

from cmt_statistics_tool.tables import Base
from cmt_statistics_tool.tables.review import RevisionReviewBase, SubmissionReviewBase

if TYPE_CHECKING:
    from cmt_statistics_tool.tables.paper import Revision, Submission
    from cmt_statistics_tool.tables.people import People


class SubmissionMetareview(Base, SubmissionReviewBase):
    __tablename__ = "submission_metareview"

    overall_rating: str = Column(Text, nullable=False)
    summary: str = Column(Text, nullable=False)
    revision_items: str = Column(Text, nullable=False)

    submission: "Submission" = relationship("Submission", back_populates="metareviews")
    reviewer: "People" = relationship("People", back_populates="submission_metareviews")


class RevisionMetareview(Base, RevisionReviewBase):
    __tablename__ = "revision_metareview"

    overall_rating: str = Column(Text, nullable=False)
    comments: str = Column(Text, nullable=False)

    revision: "Revision" = relationship("Revision", back_populates="metareviews")
    reviewer: "People" = relationship("People", back_populates="revision_metareviews")
