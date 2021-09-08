from asyncio import gather, run
from typing import Tuple, Type, Union

from pandas import DataFrame
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.sql import Subquery
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


async def get_df(substatement: Subquery) -> DataFrame:
    statement = (
        select(
            func.count().label("n_authors"),
            substatement.c.status,
            substatement.c.n_submissions,
        )
        .group_by(substatement.c.n_submissions, substatement.c.status)
        .order_by(substatement.c.n_submissions, substatement.c.status)
    )
    async with async_session() as session:
        return (
            DataFrame((await session.execute(statement)).fetchall())
            .rename(columns={1: "Status", 2: "Submissions"})
            .pivot("Submissions", "Status", 0)
            .fillna(0)
            .astype(int)
        )


async def authors(paper: Union[Type[Submission], Type[Revision]]) -> DataFrame:
    people_paper_mapping = SubmissionPeople if paper == Submission else RevisionPeople
    substatement = (
        select(People.id, paper.status, func.count().label("n_submissions"))
        .join_from(People, people_paper_mapping)
        .join_from(people_paper_mapping, paper)
        .where(people_paper_mapping.relation_type == ppr.AUTHOR)  # type: ignore
        .group_by(People.id, paper.status)
        .subquery()
    )
    return await get_df(substatement)


async def primary_authors(paper: Union[Type[Submission], Type[Revision]]) -> DataFrame:
    substatement = (
        select(
            paper.primary_author_id,
            paper.status,
            func.count().label("n_submissions"),
        )
        .group_by(paper.primary_author_id, paper.status)
        .subquery()
    )
    return await get_df(substatement)


async def main() -> Tuple[DataFrame, ...]:
    return tuple(
        await gather(
            primary_authors(Submission),
            authors(Submission),
            primary_authors(Revision),
            authors(Revision),
        )
    )


if __name__ == "__main__":
    install()
    for df in run(main()):
        print(df)
