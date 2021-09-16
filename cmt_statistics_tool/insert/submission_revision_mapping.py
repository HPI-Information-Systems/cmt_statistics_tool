from pandas import read_excel
from sqlalchemy import bindparam, update

from cmt_statistics_tool.tables import Revision, async_session


async def insert_submission_revision_mapping(file: str) -> None:
    df = read_excel(file)[["Revision ID", "OriginalSubmission ID"]]
    statement = (
        update(Revision)
        .where(Revision.id == bindparam("rid"))
        .values(submission_id=bindparam("oid"))
    )
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                statement,
                [
                    {"rid": row["Revision ID"], "oid": row["OriginalSubmission ID"]}
                    for _, row in df.iterrows()
                ],
            )
