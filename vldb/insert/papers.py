from re import compile as re_compile
from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from tqdm import tqdm

from vldb.helper import fillna_strs, get_or_add, read_original_revision
from vldb.tables import (
    People,
    Revision,
    RevisionPeople,
    Submission,
    SubmissionPeople,
    async_session,
)
from vldb.tables.people import PeoplePaperRelation as ppr

name_affiliation_pattern = re_compile(r"(?P<name>[^(]*) \((?P<affiliation>.*)\)")


def separate_name_affiliation_email(
    names_and_affiliations: str, emails: str
) -> Tuple[Tuple[str, str, str], ...]:
    result = []
    for name, email in zip(
        names_and_affiliations.strip().split(";"), emails.strip().split(";")
    ):
        if (res := name_affiliation_pattern.match(name.strip())) is not None:
            result.append(
                (
                    res.group("name").strip(),
                    res.group("affiliation").strip(),
                    email.strip().strip("*"),
                )
            )
    return tuple(result)


async def extract_and_add_people(
    session: AsyncSession, names: str, emails: str
) -> List[Tuple[int, People]]:
    return [
        (position, await get_or_add(session, name, email, affiliation))
        for position, (name, affiliation, email) in enumerate(
            separate_name_affiliation_email(names, emails)
        )
    ]


async def insert_papers(file: str) -> None:
    original, revision = read_original_revision(file)
    original = fillna_strs(
        original,
        [
            "Abstract",
            "Primary Subject Area",
            "Secondary Subject Areas",
            "Reviewers",
            "Reviewer Emails",
            "MetaReviewers",
            "MetaReviewer Emails",
            "SeniorMetaReviewers",
            "SeniorMetaReviewerEmails",
            "Q8 (Availability and Reproducibility)",
        ],
    )
    revision = fillna_strs(
        revision,
        [
            "Abstract",
            "Primary Subject Area",
            "Secondary Subject Areas",
            "Reviewers",
            "Reviewer Emails",
            "MetaReviewers",
            "MetaReviewer Emails",
            "SeniorMetaReviewers",
            "SeniorMetaReviewerEmails",
            "Q8 (Availability and Reproducibility)",
        ],
    )
    async with async_session() as session:
        for _, row in tqdm(
            original.iterrows(), desc="Submissions", total=len(original)
        ):
            async with session.begin():
                authors = await extract_and_add_people(
                    session, row["Authors"], row["Author Emails"]
                )
                reviewers = await extract_and_add_people(
                    session, row["Reviewers"], row["Reviewer Emails"]
                )
                metareviewers = await extract_and_add_people(
                    session, row["MetaReviewers"], row["MetaReviewer Emails"]
                )
                seniormetareviewers = await extract_and_add_people(
                    session, row["SeniorMetaReviewers"], row["SeniorMetaReviewerEmails"]
                )
            async with session.begin():
                submission = Submission(
                    id=row["Paper ID"],
                    title=row["Paper Title"],
                    abstract=row["Abstract"],
                    primary_author=(
                        await get_or_add(
                            session,
                            row["Primary Contact Author Name"].strip(),
                            row["Primary Contact Author Email"].strip(),
                            "",
                        )
                    ),
                    track_name=row["Track Name"],
                    primary_subject_area=row["Primary Subject Area"],
                    secondary_subject_areas=row["Secondary Subject Areas"],
                    conflicts=row["Conflicts"],
                    assigned=row["Assigned"],
                    completed=row["% Completed"],
                    bids=row["Bids"],
                    discussion=row["Discussion"],
                    status=row["Status"],
                    embargo_agreement=row[
                        "Q1 (PVLDB does not allow papers previously rejected from PVLDB to be resubmitted within 12 months of the original submission date.)"
                    ],
                    conflict_agreement=row["Q3 (Conflict)"],
                    category=row["Q4 (Special category)"],
                    authors_agreement=row["Q7 (Authors)"],
                    availability=row["Q8 (Availability and Reproducibility)"],
                )
                session.add(submission)
            async with session.begin():
                session.add_all(
                    [
                        SubmissionPeople(
                            people_id=people.id,
                            position=position,
                            relation_type=relation_type,
                            submission_id=submission.id,
                        )
                        for peoples, relation_type in (
                            (authors, ppr.AUTHOR),
                            (reviewers, ppr.REVIEWER),
                            (metareviewers, ppr.METAREVIEWER),
                            (
                                seniormetareviewers,
                                ppr.SENIORMETAREVIEWER,
                            ),
                        )
                        for position, people in set(peoples)
                    ]
                )
    async with async_session() as session:
        for _, row in tqdm(revision.iterrows(), desc="Revisions", total=len(revision)):
            async with session.begin():
                authors = await extract_and_add_people(
                    session, row["Authors"], row["Author Emails"]
                )
                reviewers = await extract_and_add_people(
                    session, row["Reviewers"], row["Reviewer Emails"]
                )
                metareviewers = await extract_and_add_people(
                    session, row["MetaReviewers"], row["MetaReviewer Emails"]
                )
                seniormetareviewers = await extract_and_add_people(
                    session, row["SeniorMetaReviewers"], row["SeniorMetaReviewerEmails"]
                )
            async with session.begin():
                revision = Revision(
                    id=row["Paper ID"],
                    title=row["Paper Title"],
                    abstract=row["Abstract"],
                    primary_author=(
                        await get_or_add(
                            session,
                            row["Primary Contact Author Name"].strip(),
                            row["Primary Contact Author Email"].strip(),
                            "",
                        )
                    ),
                    track_name=row["Track Name"],
                    primary_subject_area=row["Primary Subject Area"],
                    secondary_subject_areas=row["Secondary Subject Areas"],
                    conflicts=row["Conflicts"],
                    assigned=row["Assigned"],
                    completed=row["% Completed"],
                    bids=row["Bids"],
                    discussion=row["Discussion"],
                    status=row["Status"],
                    embargo_agreement=row[
                        "Q1 (PVLDB does not allow papers previously rejected from PVLDB to be resubmitted within 12 months of the original submission date.)"
                    ],
                    conflict_agreement=row["Q3 (Conflict)"],
                    category=row["Q4 (Special category)"],
                    authors_agreement=row["Q7 (Authors)"],
                    availability=row["Q8 (Availability and Reproducibility)"],
                )
                session.add(revision)
            async with session.begin():
                session.add_all(
                    [
                        RevisionPeople(
                            people_id=people.id,
                            position=position,
                            relation_type=relation_type,
                            revision_id=revision.id,
                        )
                        for peoples, relation_type in (
                            (authors, ppr.AUTHOR),
                            (reviewers, ppr.REVIEWER),
                            (metareviewers, ppr.METAREVIEWER),
                            (
                                seniormetareviewers,
                                ppr.SENIORMETAREVIEWER,
                            ),
                        )
                        for position, people in set(peoples)
                    ]
                )
