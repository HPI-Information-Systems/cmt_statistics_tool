"""Paper status: Status of papers per category"""
from asyncio import gather, run
from itertools import product
from math import isnan
from typing import Tuple

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from pandas import DataFrame
from seaborn import barplot
from sqlalchemy import func
from sqlalchemy.future import select
from uvloop import install

from cmt_statistics_tool.statistics import get_data, plot_df
from cmt_statistics_tool.tables import Revision, Submission


async def submission() -> DataFrame:
    statement = (
        select(Submission.category, Submission.status, func.count())
        .group_by(Submission.category, Submission.status)
        .order_by(Submission.category, Submission.status)
    )
    df = DataFrame(await get_data(statement))
    df.rename(columns={0: "Category", 1: "Status", 2: "Count"}, inplace=True)
    total = df.groupby("Category").sum().reset_index()
    total.insert(0, "Status", "All")
    df = df.append(total)
    df["Category"].replace(
        "Experiments, Analysis & Benchmark",
        "Experiments, Analysis\n& Benchmark",
        inplace=True,
    )
    return df


def plot_submission(df: DataFrame, ax: Axes) -> None:
    order = [
        "Regular Research Paper",
        "Scalable Data Science",
        "Experiments, Analysis\n& Benchmark",
        "Vision",
    ]
    hue_order = ["All", "Accept", "Minor revision", "Major revision"]
    barplot(
        x="Category",
        y="Count",
        hue="Status",
        order=order,
        hue_order=hue_order,
        data=df,
        ax=ax,
    )
    for p, (status, category) in zip(ax.patches, product(hue_order, order)):
        height = 0 if isnan(p.get_height()) else int(p.get_height())
        ax.annotate(
            height
            if status == "All"
            else "{:d}\n({:.0%})".format(
                height,
                height
                / int(
                    df["Count"][
                        (df["Category"] == category) & (df["Status"] == "All")
                    ].iloc[0]
                ),
            ),
            xy=(
                p.get_x() + p.get_width() / 2,
                p.get_y() + height + (15 if status == "All" else 40),
            ),
            ha="center",
            va="center",
        )
    ax.set_title("Status of submissions per category")


async def revision() -> DataFrame:
    statement = (
        select(Revision.category, Revision.status, func.count())
        .group_by(Revision.category, Revision.status)
        .order_by(Revision.category, Revision.status)
    )
    df = DataFrame(await get_data(statement))
    df.rename(columns={0: "Category", 1: "Status", 2: "Count"}, inplace=True)
    total = df.groupby("Category").sum().reset_index()
    total.insert(0, "Status", "All")
    df = df.append(total)
    df["Category"].replace(
        "Experiments, Analysis & Benchmark",
        "Experiments, Analysis\n& Benchmark",
        inplace=True,
    )
    return df


def plot_revision(df: DataFrame, ax: Axes) -> None:
    order = [
        "Regular Research Paper",
        "Scalable Data Science",
        "Experiments, Analysis\n& Benchmark",
        "Vision",
    ]
    hue_order = ["All", "Accept"]
    barplot(
        x="Category",
        y="Count",
        hue="Status",
        order=order,
        hue_order=hue_order,
        data=df,
        ax=ax,
    )
    for p, (status, category) in zip(ax.patches, product(hue_order, order)):
        height = 0 if isnan(p.get_height()) else int(p.get_height())
        ax.annotate(
            height
            if status == "All"
            else "{:d}\n({:.0%})".format(
                height,
                height
                / int(
                    df["Count"][
                        (df["Category"] == category) & (df["Status"] == "All")
                    ].iloc[0]
                ),
            ),
            xy=(
                p.get_x() + p.get_width() / 2,
                p.get_y() + height + (5 if status == "All" else 10),
            ),
            ha="center",
            va="center",
        )
    ax.set_title("Status of revisions per category")


async def both() -> DataFrame:
    all, acc = await gather(
        get_data(
            select(Submission.category, func.count()).group_by(Submission.category)
        ),
        get_data(
            select(Submission.category, func.count())
            .where(Submission.status == "Accept")
            .group_by(Submission.category)
            .union_all(
                select(Revision.category, func.count())
                .where(Revision.status == "Accept")
                .group_by(Revision.category)
            )
        ),
    )
    return (
        (
            DataFrame(all)
            .set_index(0)
            .join(DataFrame(acc).groupby(0).sum(), rsuffix="_ua")
        )
        .rename(columns={"1": "All", "1_ua": "Ultimately Accepted"})
        .reset_index()
        .melt(0, var_name="Status", value_name="Count")
        .rename(columns={0: "Category"})
    )


def plot_both(df: DataFrame, ax: Axes) -> None:
    df["Category"].replace(
        "Experiments, Analysis & Benchmark",
        "Experiments, Analysis\n& Benchmark",
        inplace=True,
    )
    df["Status"].replace("All", "All (Original Submission)", inplace=True)
    order = df[df["Status"] == "All (Original Submission)"].sort_values(
        "Count", ascending=False
    )["Category"]
    hue_order = ["All (Original Submission)", "Ultimately Accepted"]
    barplot(
        x="Category",
        y="Count",
        hue="Status",
        order=order,
        hue_order=hue_order,
        data=df,
        ax=ax,
    )
    for p, (status, category) in zip(ax.patches, product(hue_order, order)):
        height = 0 if isnan(p.get_height()) else int(p.get_height())
        ax.annotate(
            height
            if status == "All (Original Submission)"
            else "{:d}\n({:.0%})".format(
                height,
                height
                / int(
                    df["Count"][
                        (df["Category"] == category)
                        & (df["Status"] == "All (Original Submission)")
                    ].iloc[0]
                ),
            ),
            xy=(
                p.get_x() + p.get_width() / 2,
                p.get_y()
                + height
                + (10 if status == "All (Original Submission)" else 30),
            ),
            ha="center",
            va="center",
        )
    ax.set_title("Status of papers per category")


async def main() -> Tuple[DataFrame, DataFrame, DataFrame]:
    return await gather(submission(), revision(), both())


if __name__ == "__main__":
    install()
    s_df, r_df, b_df = run(main())
    print(s_df, r_df, b_df, sep="\n")
    plot_df(s_df, plot_submission)
    plt.savefig("plots/02_01_submission.png")
    plot_df(r_df, plot_revision)
    plt.savefig("plots/02_01_revision.png")
    plot_df(b_df, plot_both)
    plt.savefig("plots/02_01_both.png")
