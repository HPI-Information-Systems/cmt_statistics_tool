"""
Insert the metareviews file into the DB.
"""
from tqdm import tqdm

from cmt_statistics_tool.helper import fillna_strs, get_or_add, read_original_revision
from cmt_statistics_tool.tables import (
    RevisionMetareview,
    SubmissionMetareview,
    async_session,
)


async def insert_metareviews(file: str) -> None:
    original, revision = read_original_revision(file)
    original = fillna_strs(original, ["Q3 (Revision Items)"])
    revision = fillna_strs(revision, [])
    async with async_session() as session:
        for _, row in tqdm(  # Insert all metareviews on submissions
            original.iterrows(), desc="MetaReviews Submissions", total=len(original)
        ):
            async with session.begin():
                submission = SubmissionMetareview(
                    reviewer=(
                        await get_or_add(
                            session,
                            row["Meta-Reviewer Name"].strip(),
                            row["Meta-Reviewer Email"].strip(),
                            "",
                        )
                    ),
                    submission_id=row["Paper ID"],
                    overall_rating=row["Q1 (Overall Rating)"],
                    summary=row["Q2 (Summary Comments)"],
                    revision_items=row["Q3 (Revision Items)"],
                )
                session.add(submission)
        for _, row in tqdm(  # Insert all metareviews on revisions
            revision.iterrows(), desc="MetaReviews Revisions", total=len(revision)
        ):
            async with session.begin():
                revision = RevisionMetareview(
                    reviewer=(
                        await get_or_add(
                            session,
                            row["Meta-Reviewer Name"].strip(),
                            row["Meta-Reviewer Email"].strip(),
                            "",
                        )
                    ),
                    revision_id=row["Paper ID"],
                    overall_rating=row["Q1 (Overall Rating)"],
                    comments=row["Q2 (Detailed Comments)"],
                )
                session.add(revision)
