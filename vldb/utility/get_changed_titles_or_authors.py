from asyncio import gather, run
from collections import defaultdict
from typing import Dict, Iterable, Tuple

from pandas import DataFrame, ExcelWriter
from sqlalchemy.future import select
from uvloop import install

from vldb.tables import (
    People,
    Revision,
    RevisionPeople,
    Submission,
    SubmissionPeople,
    async_session,
)
from vldb.tables.people import PeoplePaperRelation as ppr


def parse_positions(
    result: Iterable[Tuple[int, int, int, int]]
) -> Dict[Tuple[int, int], Tuple[int, ...]]:
    s = defaultdict(list)
    for oid, rid, pid, pos in result:
        s[(oid, rid)].append((pid, pos))
    return {
        key: tuple(pid for pid, _ in sorted(value, key=lambda tup: int(tup[1])))
        for key, value in s.items()
    }


async def get_submission_positions() -> Dict[Tuple[int, int], Tuple[int, ...]]:
    statement = (
        select(
            Submission.id,
            Revision.id,
            SubmissionPeople.people_id,
            SubmissionPeople.position,
        )
        .join_from(Submission, Revision)
        .join_from(Submission, SubmissionPeople)
        .where(
            Submission.revision != None,  # noqa: E711
            SubmissionPeople.relation_type == ppr.AUTHOR,
        )
        .order_by(Revision.id)
    )
    async with async_session() as session:
        d = (await session.execute(statement)).fetchall()
    return parse_positions(d)  # type: ignore


async def get_revision_positions() -> Dict[Tuple[int, int], Tuple[int, ...]]:
    statement = (
        select(
            Submission.id,
            Revision.id,
            RevisionPeople.people_id,
            RevisionPeople.position,
        )
        .join_from(Submission, Revision)
        .join_from(Revision, RevisionPeople)
        .where(RevisionPeople.relation_type == ppr.AUTHOR)
        .order_by(Revision.id)
    )
    async with async_session() as session:
        d = (await session.execute(statement)).fetchall()
    return parse_positions(d)  # type: ignore


async def get_mismatched_authors() -> DataFrame:
    o_positions, r_positions = await gather(
        get_submission_positions(), get_revision_positions()
    )
    assert o_positions.keys() == r_positions.keys()
    mismatches = {
        key: (o_position, r_position)
        for key, o_position in o_positions.items()
        if o_position != (r_position := r_positions[key])
    }
    pids = set(pid for tups in mismatches.values() for tup in tups for pid in tup)
    statement = select(People.id, People.name, People.email).where(People.id.in_(pids))
    async with async_session() as session:
        people = {
            p.id: (p.name, p.email)
            for p in (await session.execute(statement)).fetchall()
        }
    data = [
        (
            oid,
            rid,
            "\n".join("{} ({})".format(*people[id]) for id in o_pos),
            "\n".join("{} ({})".format(*people[id]) for id in r_pos),
            "\n".join("{} ({})".format(*people[id]) for id in o_pos if id not in r_pos),
            "\n".join("{} ({})".format(*people[id]) for id in r_pos if id not in o_pos),
        )
        for (oid, rid), (o_pos, r_pos) in mismatches.items()
    ]
    return (
        DataFrame(data)[[0, 1, 4, 5, 2, 3]]
        .rename(
            columns={
                0: "OriginalSubmission ID",
                1: "Revision ID",
                2: "OriginalSubmission Authors",
                3: "Revision Authors",
                4: "Removed Authors",
                5: "Added Authors",
            }
        )
        .reset_index(drop=True)
    )


async def get_mismatched_titles() -> DataFrame:
    statement = (
        select(Submission.id, Revision.id, Submission.title, Revision.title)
        .join_from(Revision, Submission)
        .order_by(Revision.id)
    )
    async with async_session() as session:
        result = DataFrame((await session.execute(statement)).fetchall())
    result = result.loc[result[2] != result[3]]
    result = result.loc[result[2] != result[3].str.strip()]
    result = result.loc[
        result[2]
        != result[3].apply(
            lambda title: (
                title[: title.rfind(" (Revision)")]
                if title.rfind(" (Revision)") >= 0
                else title
            )
        )
    ]
    result = result.loc[
        result[2]
        != result[3]
        .apply(
            lambda title: (
                title[: title.rfind(" (Revision)")]
                if title.rfind(" (Revision)") >= 0
                else title
            )
        )
        .str.strip()
    ]
    return result.rename(
        columns={
            0: "OriginalSubmission ID",
            1: "Revision ID",
            2: "OriginalSubmission Title",
            3: "Revision Title",
        }
    ).reset_index(drop=True)


async def main() -> Tuple[DataFrame, DataFrame]:
    return await gather(get_mismatched_titles(), get_mismatched_authors())


if __name__ == "__main__":
    install()
    titles, authors = run(main())
    with ExcelWriter("Mismatches.xlsx") as f:
        titles.to_excel(f, sheet_name="titles")
        authors.to_excel(f, sheet_name="authors")
