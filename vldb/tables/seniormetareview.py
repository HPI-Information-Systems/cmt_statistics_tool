from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship

from vldb.tables import Base
from vldb.tables.review import RevisionReviewBase, SubmissionReviewBase

if TYPE_CHECKING:
    from vldb.tables.paper import Revision, Submission
    from vldb.tables.people import People


class SubmissionSeniormetareview(Base, SubmissionReviewBase):
    __tablename__ = "submission_seniormetareview"

    submission: "Submission" = relationship(
        "Submission", back_populates="seniormetareviews"
    )
    reviewer: "People" = relationship(
        "People", back_populates="submission_seniormetareviews"
    )


class RevisionSeniormetareview(Base, RevisionReviewBase):
    __tablename__ = "revision_seniormetareview"

    revision: "Revision" = relationship("Revision", back_populates="seniormetareviews")
    reviewer: "People" = relationship(
        "People", back_populates="revision_seniormetareviews"
    )
