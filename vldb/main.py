from asyncio import run

from sqlalchemy.schema import CreateTable
from uvloop import install

import vldb.tables as tables
from vldb.insert.metareviews import insert_metareviews
from vldb.insert.papers import insert_papers
from vldb.insert.people import insert_people
from vldb.insert.reviews import insert_reviews
from vldb.insert.submission_revision_mapping import insert_submission_revision_mapping


async def create_tables() -> None:
    for t in tables.Base.metadata.sorted_tables:
        with open(f"vldb/sql/CREATE_{t}.sql", "w") as f:
            statement = str(CreateTable(t).compile(tables.engine)).strip()
            print(statement, file=f)
    async with tables.engine.connect() as connection:
        await connection.run_sync(tables.Base.metadata.drop_all)
        await connection.run_sync(tables.Base.metadata.create_all)
        await connection.commit()


async def insert_data() -> None:
    await insert_people("data/AllPeopleVLDB.txt")
    await insert_papers("data/AllPapersThroughJuly.xlsx")
    await insert_reviews("data/PVLDBReviewsApril2020-July2021.xlsx")
    await insert_metareviews("data/PVLDBMetaReviewsApril2020-July2021.xlsx")
    await insert_submission_revision_mapping("data/RevisionToOriginalSubmission.xlsx")


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
