"""Other: Number of papers per distinct affiliations (email domains)"""
from asyncio import run
from math import isnan

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from pandas import DataFrame, RangeIndex
from seaborn import barplot
from sqlalchemy import func, literal
from sqlalchemy.future import select
from uvloop import install

from cmt_statistics_tool.statistics import get_data, plot_df
from cmt_statistics_tool.tables import (
    People,
    Revision,
    RevisionPeople,
    Submission,
    SubmissionPeople,
)
from cmt_statistics_tool.tables.people import PeoplePaperRelation as ppr

X = "Number of distinct affiliations (email domains)"


async def both() -> DataFrame:
    statement = (
        select(
            literal("S"),
            Submission.id,
            Submission.status,
            func.array_agg(func.lower(func.split_part(People.email, "@", 2))),
        )
        .join_from(Submission, SubmissionPeople)
        .join_from(SubmissionPeople, People)
        .where(SubmissionPeople.relation_type == ppr.AUTHOR)
        .group_by(Submission.id)
        .union_all(
            select(
                literal("R"),
                Revision.id,
                Revision.status,
                func.array_agg(func.lower(func.split_part(People.email, "@", 2))),
            )
            .join_from(Revision, RevisionPeople)
            .join_from(RevisionPeople, People)
            .where(RevisionPeople.relation_type == ppr.AUTHOR)
            .group_by(Revision.id)
        )
    )

    df = DataFrame(await get_data(statement))
    df[3] = df[3].apply(lambda l: len(set(l)))
    total = (
        df.loc[df[0] == "S"]
        .groupby(3)[[1]]
        .count()
        .rename(columns={1: "Number of Papers"})
    )
    accept = (
        df.loc[df[2] == "Accept"]
        .groupby(3)[[1]]
        .count()
        .rename(columns={1: "Number of Papers"})
    )
    combined = accept.join(total, how="outer", lsuffix="_ua").fillna(0).astype(int)
    combined = (
        combined.reindex(
            RangeIndex(combined.index.min(), combined.index.max() + 1), fill_value=0
        )
        .reset_index()
        .rename(
            columns={
                "index": X,
                "Number of Papers_ua": "Ultimately accepted",
                "Number of Papers": "All",
            }
        )
    )
    combined["Acceptance Rate"] = combined["Ultimately accepted"] / combined["All"]
    combined = combined.melt(
        id_vars=[X],
        var_name="Status",
        value_name="Count",
    )
    return combined


def plot_both(df: DataFrame, ax: Axes) -> None:
    order = sorted(df[X].unique())
    hue_order = ["All", "Ultimately accepted"]
    barplot(
        x=X,
        y="Count",
        hue="Status",
        data=df,
        order=order,
        hue_order=hue_order,
        ax=ax,
    )
    for i, p in enumerate(ax.patches[len(df.loc[df["Status"] == "All"]) :]):
        v = df.loc[df["Status"] == "Acceptance Rate"]["Count"].iloc[i]
        if not isnan(v):
            ax.annotate(
                f"{v:.1%}",
                xy=(
                    p.get_x() + p.get_width() / 2,
                    p.get_y() + p.get_height() + 25,
                ),
                ha="center",
                va="center",
                rotation=90,
            )
    ax.set_title("Number of papers per distinct affiliations (email domains)")


async def main() -> DataFrame:
    return await both()


if __name__ == "__main__":
    install()
    b_df = run(main())
    print(b_df, sep="\n")
    plot_df(b_df, plot_both)
    plt.savefig("plots/03_01_both.png")
