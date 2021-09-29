"""
Main entrypoint to create the database.

Running this will delete all tables, create them, and insert all data.
If your DB lives elsewhere, please change the connection string in the tables module.
If your files are named differently, please change them here.
"""

from asyncio import run

from sqlalchemy.schema import CreateTable
from uvloop import install

import cmt_statistics_tool.tables as tables
from cmt_statistics_tool.insert.metareviews import insert_metareviews
from cmt_statistics_tool.insert.papers import insert_papers
from cmt_statistics_tool.insert.people import insert_people
from cmt_statistics_tool.insert.reviews import insert_reviews
from cmt_statistics_tool.insert.submission_revision_mapping import (
    insert_submission_revision_mapping,
)


async def create_tables() -> None:
    for t in tables.Base.metadata.sorted_tables:
        with open(f"cmt_statistics_tool/sql/CREATE_{t}.sql", "w") as f:
            statement = str(CreateTable(t).compile(tables.engine)).strip()
            print(statement, file=f)
    async with tables.engine.connect() as connection:
        await connection.run_sync(tables.Base.metadata.drop_all)
        await connection.run_sync(tables.Base.metadata.create_all)
        await connection.commit()


async def insert_data() -> None:
    await insert_people("data/people.txt")
    await insert_papers("data/papers.xlsx")
    await insert_reviews("data/reviews.xlsx")
    await insert_metareviews("data/metareviews.xlsx")
    await insert_submission_revision_mapping("data/mapping.xlsx")


def main() -> None:
    install()
    print("Dropping & Creating tables...", end=" ")
    run(create_tables())
    print("done! ✅")

    print("Inserting data...")
    run(insert_data())
    print("Inserting data... done! ✅")


if __name__ == "__main__":
    main()
