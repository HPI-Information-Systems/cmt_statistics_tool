"""Paper status: Status of papers per number of authors"""
from asyncio import gather, run
from itertools import product
from math import isnan
from typing import Tuple

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from pandas import DataFrame, MultiIndex, RangeIndex
from seaborn import barplot
from sqlalchemy import func, literal, text
from sqlalchemy.future import select
from uvloop import install

from vldb.statistics import get_data, test_plot_df
from vldb.tables import Revision, Submission
from vldb.tables.people import PeoplePaperRelation as ppr
from vldb.tables.people import RevisionPeople, SubmissionPeople


async def submission() -> DataFrame:
    statement = (
        select(text("n_authors"), text("status"), func.count())
        .select_from(
            select(
                Submission.id,
                Submission.status.label("status"),  # type: ignore
                func.count().label("n_authors"),
            )
            .join_from(Submission, SubmissionPeople)
            .where(SubmissionPeople.relation_type == ppr.AUTHOR)
            .group_by(Submission.id)
            .subquery()
        )
        .group_by(text("n_authors"), text("status"))
        .order_by(text("n_authors"), text("status"))
    )
    df = DataFrame(await get_data(statement))
    df = (
        df.set_index([0, 1])
        .reindex(
            MultiIndex.from_product(
                (RangeIndex(df[0].min(), df[0].max() + 1), df[1].unique())
            ),
            fill_value=0,
        )
        .reset_index()
    )
    total: DataFrame = df.groupby("level_0").sum().reset_index()
    total.insert(1, "level_1", "All")
    df = df.append(total)
    return df.rename(
        columns={"level_0": "Number of Authors", "level_1": "Status", 2: "Count"}
    )


def plot_submission(df: DataFrame, ax: Axes) -> None:
    barplot(
        x="Number of Authors",
        y="Count",
        hue="Status",
        hue_order=["All", "Accept", "Minor revision", "Major revision"],
        data=df,
        ax=ax,
    )
    ax.set_title("Status of submissions per number of authors")


async def revision() -> DataFrame:
    statement = (
        select(text("n_authors"), text("status"), func.count())
        .select_from(
            select(
                Revision.id,
                Revision.status.label("status"),  # type: ignore
                func.count().label("n_authors"),
            )
            .join_from(Revision, RevisionPeople)
            .where(RevisionPeople.relation_type == ppr.AUTHOR)
            .group_by(Revision.id)
            .subquery()
        )
        .group_by(text("n_authors"), text("status"))
        .order_by(text("n_authors"), text("status"))
    )
    df = DataFrame(await get_data(statement))
    df = (
        df.set_index([0, 1])
        .reindex(
            MultiIndex.from_product(
                (RangeIndex(df[0].min(), df[0].max() + 1), df[1].unique())
            ),
            fill_value=0,
        )
        .reset_index()
    )
    total: DataFrame = df.groupby("level_0").sum().reset_index()
    total.insert(1, "level_1", "All")
    df = df.append(total)
    return df.rename(
        columns={"level_0": "Number of Authors", "level_1": "Status", 2: "Count"}
    )


def plot_revision(df: DataFrame, ax: Axes) -> None:
    barplot(
        x="Number of Authors",
        y="Count",
        hue="Status",
        hue_order=["All", "Accept"],
        data=df,
        ax=ax,
    )
    ax.set_title("Status of revisions per number of authors")


async def both() -> DataFrame:
    statement = (
        select(text("n_authors"), text("status"), func.count(), literal("Submission"))
        .select_from(
            select(
                Submission.id,
                Submission.status.label("status"),  # type: ignore
                func.count().label("n_authors"),
            )
            .join_from(Submission, SubmissionPeople)
            .where(SubmissionPeople.relation_type == ppr.AUTHOR)
            .group_by(Submission.id)
            .subquery()
        )
        .group_by(text("n_authors"), text("status"))
    ).union_all(
        select(text("n_authors"), text("status"), func.count(), literal("Revision"))
        .select_from(
            select(
                Revision.id,
                Revision.status.label("status"),  # type: ignore
                func.count().label("n_authors"),
            )
            .join_from(Revision, RevisionPeople)
            .where(
                RevisionPeople.relation_type == ppr.AUTHOR, Revision.status == "Accept"
            )
            .group_by(Revision.id)
            .subquery()
        )
        .group_by(text("n_authors"), text("status"))
    )
    df = DataFrame(await get_data(statement))
    df = (
        df[df[3] == "Submission"]
        .groupby(0)
        .sum()
        .join(
            df[df[1] == "Accept"].groupby(0).sum(),
            how="outer",
            lsuffix="_total",
            rsuffix="_ua",
        )
        .fillna(0)
        .astype(int)
        .rename(columns={"2_total": "All", "2_ua": "Ultimately accepted"})
    )
    return (
        df.reindex(RangeIndex(df.index.min(), df.index.max() + 1), fill_value=0)
        .reset_index()
        .rename(columns={"index": "Number of Authors"})
        .melt(id_vars=["Number of Authors"], var_name="Status", value_name="Count")
    )


def plot_both(df: DataFrame, ax: Axes) -> None:
    order = sorted(df["Number of Authors"].unique())
    hue_order = ["All", "Ultimately accepted"]
    barplot(
        x="Number of Authors",
        y="Count",
        hue="Status",
        order=order,
        hue_order=hue_order,
        data=df,
        ax=ax,
    )
    for p, (status, n_authors) in zip(ax.patches, product(hue_order, order)):
        height = 0 if isnan(p.get_height()) else int(p.get_height())
        if status == "All":
            continue
        count_all = df["Count"][
            (df["Status"] == "All") & (df["Number of Authors"] == n_authors)
        ].iloc[0]
        if not count_all:
            continue
        ax.annotate(
            f"{height/count_all:.0%}",
            xy=(
                p.get_x() + p.get_width() / 2 + 0.1,
                p.get_y() + height + 15,
            ),
            ha="center",
            va="center",
            rotation=90,
        )
    ax.set_title("Status of papers per number of authors")


async def main() -> Tuple[DataFrame, DataFrame, DataFrame]:
    return await gather(submission(), revision(), both())


if __name__ == "__main__":
    install()
    s_df, r_df, b_df = run(main())

    print(s_df, r_df, b_df, sep="\n")
    test_plot_df(s_df, plot_submission)
    plt.savefig("plots/02_04_submission.png")
    test_plot_df(r_df, plot_revision)
    plt.savefig("plots/02_04_revision.png")
    test_plot_df(b_df, plot_both)
    plt.savefig("plots/02_04_both.png")
