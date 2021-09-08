"""Other: Number of papers per country/region"""
from asyncio import gather, run
from typing import Tuple

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from pandas import DataFrame, MultiIndex
from seaborn import barplot, color_palette
from sqlalchemy import func, literal
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from uvloop import install

from vldb.statistics import get_data, test_plot_df
from vldb.tables import Revision, RevisionPeople, Submission, SubmissionPeople
from vldb.tables.people import People
from vldb.tables.people import PeoplePaperRelation as ppr


async def submission() -> DataFrame:
    statement = (
        select(People.country, Submission.status, func.count())
        .join_from(People, Submission, onclause=People.primary_author_submissions)
        .group_by(People.country, Submission.status)
        .union_all(
            select(People.country, literal("All"), func.count())
            .join_from(People, Submission, onclause=People.primary_author_submissions)
            .group_by(People.country)
        )
    )
    return DataFrame(await get_data(statement)).rename(
        columns={0: "Country/Region", 1: "Status", 2: "Count"}
    )


def plot_submission(df: DataFrame, ax: Axes) -> None:
    df = df.loc[df["Status"] == "All"].drop(columns="Status")
    df = df.loc[df["Count"] >= 2]
    barplot(
        y="Country/Region",
        x="Count",
        order=df.sort_values("Count", ascending=False)["Country/Region"],
        data=df,
        color=color_palette()[0],
        ax=ax,
    )
    ax.set_title("Number of submissions per country/region")


async def revision() -> DataFrame:
    statement = (
        select(People.country, Revision.status, func.count())
        .join_from(People, Revision, onclause=People.primary_author_revisions)
        .group_by(People.country, Revision.status)
        .union_all(
            select(People.country, literal("All"), func.count())
            .join_from(People, Revision, onclause=People.primary_author_revisions)
            .group_by(People.country)
        )
    )
    return DataFrame(await get_data(statement)).rename(
        columns={0: "Country/Region", 1: "Status", 2: "Count"}
    )


def plot_revision(df: DataFrame, ax: Axes) -> None:
    df = df.loc[df["Status"] == "All"].drop(columns="Status")
    df = df.loc[df["Count"] >= 2]
    barplot(
        y="Country/Region",
        x="Count",
        order=df.sort_values("Count", ascending=False)["Country/Region"],
        data=df,
        color=color_palette()[0],
        ax=ax,
    )
    ax.set_title("Number of revisions per country/region")


async def both() -> DataFrame:
    primary_author = aliased(People)
    primary_author_revision = aliased(People)
    statement = (
        select(
            Submission.status,
            primary_author.country,
            func.array_agg(aggregate_order_by(People.country, People.id)),
            literal("Submission"),
        )
        .join_from(Submission, SubmissionPeople)
        .join_from(SubmissionPeople, People)
        .join_from(Submission, primary_author, onclause=Submission.primary_author)
        .where(SubmissionPeople.relation_type == ppr.AUTHOR)
        .group_by(Submission.id, primary_author)
        .union_all(
            select(
                Revision.status,
                primary_author_revision.country,
                func.array_agg(aggregate_order_by(People.country, People.id)),
                literal("Revision"),
            )
            .join_from(Revision, RevisionPeople)
            .join_from(RevisionPeople, People)
            .join_from(
                Revision, primary_author_revision, onclause=Revision.primary_author
            )
            .where(RevisionPeople.relation_type == ppr.AUTHOR)
            .group_by(Revision.id, primary_author_revision)
        )
    )
    df = DataFrame(await get_data(statement))
    df["Country/Region"] = (
        (df[1].apply(lambda x: [x]) + df[2])
        .apply(
            lambda countries: (
                [country for country in countries if country is not None] + [None]
            )[0]
        )
        .fillna("None")
    )
    df.drop(columns=[1, 2], inplace=True)
    df["Count"] = 1
    df = df.groupby([3, "Country/Region", 0]).sum()
    df = df.reset_index()
    accepted_revisions = (
        df[(df[3] == "Revision") & (df[0] == "Accept")]
        .drop(columns=[0, 3])
        .set_index("Country/Region")
    )
    df = df[df[3] == "Submission"].drop(columns=[3])
    df = df.set_index(["Country/Region", 0])
    df = df.reindex(
        MultiIndex.from_product(
            (
                df.index.get_level_values("Country/Region").unique(),
                df.index.get_level_values(0).unique(),
            )
        ),
        fill_value=0,
    )
    df = df.reset_index().rename(columns={0: "Status"})
    accept = (
        df[df["Status"] == "Accept"]
        .drop(columns=["Status"])
        .set_index("Country/Region")
    )
    total = df.groupby("Country/Region").sum()
    accept = DataFrame(
        accept.join(accepted_revisions, rsuffix="_r").sum(axis=1).astype(int)
    ).rename(columns={0: "Count"})
    return (
        total.join(accept, rsuffix="_ua")
        .rename(columns={"Count": "All", "Count_ua": "Ultimately Accepted"})
        .reset_index()
        .melt(id_vars=["Country/Region"], var_name="Status", value_name="Count")
        .sort_values(["Country/Region", "Status"])
    )


def plot_both(df: DataFrame, ax: Axes) -> None:
    n = 3
    countries = (
        df[(df["Status"] == "All") & (df["Count"] >= n)]
        .sort_values(["Count", "Country/Region"], ascending=[False, True])[
            "Country/Region"
        ]
        .values
    )
    small_countries = df[(df["Status"] == "All") & (df["Count"] < n)].sort_values(
        ["Count", "Country/Region"], ascending=[False, True]
    )["Country/Region"]
    small_countries_accepted = [
        "- {:s} ({:d} accepted)".format(
            x,
            df[(df["Status"] == "Ultimately Accepted") & (df["Country/Region"] == x)][
                "Count"
            ].iloc[0],
        )
        for x in small_countries
    ]
    df = df.loc[df["Country/Region"].isin(countries)]
    barplot(
        y="Country/Region",
        x="Count",
        label="All",
        order=countries,
        data=df.loc[df["Status"] == "All"],
        color=color_palette()[0],
        ax=ax,
    )
    barplot(
        y="Country/Region",
        x="Count",
        label="Ultimately Accepted",
        order=countries,
        data=df.loc[df["Status"] == "Ultimately Accepted"],
        color=color_palette()[1],
        ax=ax,
    )
    ax.annotate(
        f"Countries/Regions with\nless than {n} papers submitted:\n"
        + "\n".join(small_countries_accepted),
        xy=(0.63, 0.55),
        xycoords="subfigure fraction",
        ha="left",
        va="center",
    )
    ax.legend(loc="lower right")
    ax.set_title(
        "Number of papers per country/region (primary contact or first non-null country/region)"
    )


async def main() -> Tuple[DataFrame, DataFrame, DataFrame]:
    return await gather(submission(), revision(), both())


if __name__ == "__main__":
    install()
    s_df, r_df, b_df = run(main())
    print(s_df, r_df, b_df, sep="\n")
    test_plot_df(s_df, plot_submission)
    plt.savefig("plots/03_02_submission.png")
    test_plot_df(r_df, plot_revision)
    plt.savefig("plots/03_02_revision.png")
    test_plot_df(b_df, plot_both)
    plt.savefig("plots/03_02_both.png")
