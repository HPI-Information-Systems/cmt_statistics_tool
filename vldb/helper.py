from typing import List, Optional, Tuple

from pandas import DataFrame, concat, read_excel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from vldb.tables import People


def read_original_revision(path: str) -> Tuple[DataFrame, DataFrame]:
    d = read_excel(path, sheet_name=None)
    original: List[DataFrame] = []
    revision: List[DataFrame] = []
    for df in d.values():
        name = str(df.columns[0]).strip()
        df.columns = df.iloc[1]
        df.drop(df.index[:2], inplace=True)
        try:
            df.rename(
                columns={
                    "Q14 (Reproducibility. If the authors have provided supplemental material (data, code, etc.), is the information likely to be sufficient to understand and to reproduce the experiments? Otherwise, do the authors provide sufficient technical details in the paper to support reproducibility? Note that we do not expect actual reproducibility experiments, but rather a verification that the material is reasonable in scope and content.)": "Q14 (Supplemental material. If the authors have provided supplemental material (data, code, etc.,), is the information likely to be sufficient to understand and to reproduce the experiments? Note that we do not expect actual reproducibility experiments, but rather a verification that the files are in fact there and are reasonable in scope and content.)"
                },
                inplace=True,
            )
        except KeyError:
            pass
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
