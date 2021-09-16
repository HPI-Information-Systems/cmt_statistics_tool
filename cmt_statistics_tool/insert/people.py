"""Insert the people export INCLUDING country information.

Available columns:
First Name
Middle Initial (optional)
Last Name
E-mail
Organization
Country
Google Scholar URL
Semantic Scholar URL
DBLP URL
Domain Conflicts
"""

from pandas import Series, isna, read_csv
from tqdm import tqdm

from cmt_statistics_tool.helper import fillna_strs, get_or_add
from cmt_statistics_tool.tables import async_session


def agg_name(x: Series) -> str:
    f_name = x["First Name"].strip()
    m_name = x["Middle Initial (optional)"].strip()
    l_name = x["Last Name"].strip()
    return f"{f_name}{'' if m_name == '' else ' ' + m_name} {l_name}"


async def insert_people(file: str) -> None:
    df = read_csv(file, sep="\t").rename(columns={"# First Name": "First Name"})
    df = fillna_strs(
        df,
        [
            "First Name",
            "Middle Initial (optional)",
            "Last Name",
            "Organization",
        ],
    )

    df["Name"] = df.agg(agg_name, axis=1)
    async with async_session() as session:
        for _, row in tqdm(
            df[["Name", "E-mail", "Organization", "Country"]].iterrows(),
            desc="People",
            total=len(df),
        ):
            async with session.begin():
                await get_or_add(
                    session,
                    row["Name"],
                    row["E-mail"],
                    row["Organization"],
                    country=row["Country"] if not isna(row["Country"]) else None,
                )
