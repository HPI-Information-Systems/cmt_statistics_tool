from typing import List, Optional, Tuple

from pandas import DataFrame, concat, read_excel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from cmt_statistics_tool.tables import People


def read_original_revision(path: str) -> Tuple[DataFrame, DataFrame]:
    d = read_excel(path, sheet_name=None)
    original: List[DataFrame] = []
    revision: List[DataFrame] = []
    for df in d.values():
        name = str(df.columns[0]).strip()
        df.columns = df.iloc[1]
        df.drop(df.index[:2], inplace=True)
        if name.endswith("Revision"):
            revision.append(df)
        else:
            original.append(df)
    return concat(original), concat(revision)


def fillna_strs(df: DataFrame, columns: List[str], value: str = "") -> DataFrame:
    for column in columns:
        df[column] = df[column].fillna(value).astype(str)
    return df


async def get_or_add(
    session: AsyncSession,
    name: str,
    email: str,
    affiliation: str,
    country: Optional[str] = None,
) -> People:
    if (
        result := (
            await session.execute(
                select(People).filter_by(name=name, email=email).limit(1)
            )
        ).fetchone()
    ) is None:
        p = People(name=name, email=email, affiliation=affiliation, country=country)
        session.add(p)
    else:
        p = result[0]
    return p
