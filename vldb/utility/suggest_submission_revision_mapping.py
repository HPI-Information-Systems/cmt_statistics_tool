from asyncio import gather, run
from functools import reduce
from operator import add
from typing import List, Tuple

from pandas import DataFrame
from sqlalchemy import or_
from sqlalchemy.future import select
from uvloop import install

from vldb.tables import Revision, Submission, async_session


async def match_suggestions() -> List[Tuple[int, int, str, bool]]:
    statement = (
        select(Submission.id, Submission.title)
        .join(Revision, onclause=Submission.revision, isouter=True)
        .where(
            or_(
                Submission.status == "Major revision",
                Submission.status == "Minor revision",
            ),
            Revision.submission == None,  # noqa: E711
        )
    )
    async with async_session() as session:
        original = {
            title: id for id, title in (await session.execute(statement)).fetchall()
        }
    statement = (
        select(Revision.id, Revision.title)
        .where(Revision.submission == None)  # noqa: E711
        .order_by(Revision.id)
    )
    data = []
    async with async_session() as session:
        async for id, title in (await session.stream(statement)):
            title_without_revision = (
                title[: title.rfind(" (Revision)")]
                if title.rfind(" (Revision)") >= 0
                else title
            )
            if title in original:
                data.append((original[title], id, title))
            elif (t := title.strip()) in original:
                data.append((original[t], id, title))
            elif (t := title_without_revision) in original:
                data.append((original[t], id, title))
            elif (t := title_without_revision.strip()) in original:
                data.append((original[t], id, title))
            else:
                data.append(("", id, title))
    return [(oid, rid, rtitle, False) for oid, rid, rtitle in data]


async def get_previously_matched() -> List[Tuple[int, int, str, bool]]:
    data = []
    statement = (
        select(Submission.id, Revision.id, Revision.title)
        .join_from(Revision, Submission, Revision.submission)
        .order_by(Revision.id)
    )
    async with async_session() as session:
        async for oid, rid, rtitle in (await session.stream(statement)):
            data.append((oid, rid, rtitle))
    return [(oid, rid, rtitle, True) for oid, rid, rtitle in data]


async def main() -> DataFrame:
    data = await gather(match_suggestions(), get_previously_matched())
    return DataFrame(reduce(add, data))[[1, 0, 2, 3]].rename(
        columns={
            0: "OriginalSubmission ID",
            1: "Revision ID",
            2: "Revision Title",
            3: "IsAlreadyMapped?",
        }
    )


if __name__ == "__main__":
    install()
    df = run(main())
    print(df)
    # df.to_excel("RevisionToOriginalSubmission.xlsx")
