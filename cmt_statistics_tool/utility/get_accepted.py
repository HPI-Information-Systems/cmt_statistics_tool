from asyncio import run

from pandas import DataFrame
from sqlalchemy import or_
from sqlalchemy.future import select
from uvloop import install

from cmt_statistics_tool.tables import People, Revision, Submission, async_session


async def main() -> DataFrame:
    statement = (
        select(
            Submission.id,
            Submission.title,
            People.name,
            People.email,
            Submission.track_name,
        )
        .join(People, onclause=Submission.primary_author)
        .where(or_(Submission.status == "Accept"))
        .order_by(Submission.id)
    ).union_all(
        select(
            Revision.id,
            Revision.title,
            People.name,
            People.email,
            Revision.track_name,
        )
        .join(People, onclause=Revision.primary_author)
        .where(or_(Revision.status == "Accept"))
        .order_by(Revision.id)
    )
    async with async_session() as session:
        return (
            DataFrame((await session.execute(statement)).fetchall())
            .sort_values(0)
            .rename(
                columns={
                    0: "Paper ID",
                    1: "Paper Title",
                    2: "Primary Contact Author Name",
                    3: "Primary Contact Author Email",
                    4: "Track Name",
                }
            )
            .set_index("Paper ID")
        )


if __name__ == "__main__":
    install()
    df = run(main())
    print(df)
    # df.to_excel("accepted.xlsx")
