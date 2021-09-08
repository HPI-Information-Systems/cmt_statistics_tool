from asyncio import run

from pandas import DataFrame
from sqlalchemy import or_
from sqlalchemy.future import select
from uvloop import install

from vldb.tables import People, Revision, Submission, async_session


async def main() -> DataFrame:
    statement = (
        select(Submission.id, Submission.title, People.name, People.email)
        .join_from(Submission, Revision, onclause=Submission.revision, isouter=True)
        .join_from(Submission, People, onclause=Submission.primary_author)
        .where(
            or_(
                Submission.status == "Major revision",
                Submission.status == "Minor revision",
            ),
            Revision.submission == None,  # noqa: E711
        )
        .order_by(Submission.id)
    )
    async with async_session() as session:
        return DataFrame((await session.execute(statement)).fetchall()).rename(
            columns={
                0: "Paper ID",
                1: "Paper Title",
                2: "Primary Contact Author Name",
                3: "Primary Contact Author Email",
            }
        )


if __name__ == "__main__":
    install()
    df = run(main())
    print(df)
