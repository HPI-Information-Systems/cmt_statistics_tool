"""Paper status: Status of papers"""
from asyncio import gather, run
from math import isnan
from typing import Tuple, Union

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from pandas import DataFrame
from seaborn import barplot, color_palette
from sqlalchemy import func
from sqlalchemy.future import select
from uvloop import install

from vldb.statistics import get_data, test_plot_df
from vldb.tables import Revision, Submission


async def submission() -> DataFrame:
    statement = (
        select(Submission.status, func.count())
        .group_by(Submission.status)
        .order_by(Submission.status)
    )
    df = DataFrame(await get_data(statement))
    df.rename(columns={0: "Status", 1: "Count"}, inplace=True)
    return df.append(
        {"Status": "All", "Count": int(df["Count"].sum())}, ignore_index=True
    )


def plot_submission(df: DataFrame, ax: Axes) -> None:
    order = [
        "All",
        "Accept",
        "Minor revision",
        "Major revision",
        "Reject",
        "Desk Reject",
        "Withdrawn",
    ]
    barplot(
        x="Status",
        y="Count",
        order=order,
        data=df,
        color=color_palette()[0],
        ax=ax,
    )
    for p, status in zip(ax.patches, order):
        count: Union[str, int] = int(df[df["Status"] == status]["Count"].iloc[0])
        if status != "All":
            frac = count / df[df["Status"] == "All"]["Count"].iloc[0]
            count = f"{count:d}\n({frac:.1%})"
        ax.annotate(
            str(count),
            xy=(
                p.get_x() + p.get_width() / 2,
                p.get_y()
                + (0 if isnan(p.get_height()) else p.get_height())
                + (45 if status != "All" else 20),
            ),
            ha="center",
            va="center",
        )
    ax.set_title("Status of submissions")


async def revision() -> DataFrame:
    statement = (
        select(Revision.status, func.count())
        .group_by(Revision.status)
        .order_by(Revision.status)
    )
    df = DataFrame(await get_data(statement))
    df.rename(columns={0: "Status", 1: "Count"}, inplace=True)
    df = df.append(
        {"Status": "All", "Count": int(df["Count"].sum())}, ignore_index=True
    )
    return df[df["Status"] != "Awaiting Decision"]


def plot_revision(df: DataFrame, ax: Axes) -> None:
    barplot(
        x="Status",
        y="Count",
        order=["All", "Accept", "Reject"],
        data=df,
        color=color_palette()[0],
        ax=ax,
    )
    for p in ax.patches:
        height = 0 if isnan(p.get_height()) else int(p.get_height())
        ax.annotate(
            height,
            xy=(
                p.get_x() + p.get_width() / 2,
                p.get_y() + height + 5,
            ),
            ha="center",
            va="center",
        )
    ax.set_title("Status of revisions")


async def main() -> Tuple[DataFrame, DataFrame]:
    return await gather(submission(), revision())


if __name__ == "__main__":
    install()
    s_df, r_df = run(main())
    print(s_df, r_df, sep="\n")
    test_plot_df(s_df, plot_submission)
    plt.savefig("plots/02_02_submission.png")
    test_plot_df(r_df, plot_revision)
    plt.savefig("plots/02_02_revision.png")
