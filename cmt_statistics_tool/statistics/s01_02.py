"""Reviewers and ratings: Acceptance Rate over Time"""
from asyncio import gather, run
from typing import Tuple, Type, Union

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from pandas import DataFrame
from seaborn import barplot, color_palette
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.sql.selectable import Select
from uvloop import install

from cmt_statistics_tool.statistics import format_sort_track, get_data, test_plot_df
from cmt_statistics_tool.tables import Revision, Submission


def statement(paper: Union[Type[Submission], Type[Revision]]) -> Select:
    return (
        select(paper.track_name, paper.status, func.count())
        .group_by(paper.track_name, paper.status)
        .order_by(paper.track_name, paper.status)
    )


async def submission() -> DataFrame:
    df = format_sort_track(
        DataFrame(await get_data(statement(Submission))).rename(
            columns={0: "Track", 1: "Status", 2: "Count"}
        ),
        "Track",
    )
    total = df.groupby("Track").sum().rename(columns={"Count": "Total"})
    accepted = (
        df[df["Status"].isin(("Accept", "Minor revision", "Major revision"))]
        .groupby("Track")
        .sum()
        .rename(columns={"Count": "Accepted"})
    )
    df = total.join(accepted)
    df["Acceptance/Revision Rate"] = df["Accepted"] / df["Total"]
    return df[["Acceptance/Revision Rate"]].reset_index()


def plot_submission(df: DataFrame, ax: Axes) -> None:
    barplot(
        x="Track",
        y="Acceptance/Revision Rate",
        data=df,
        color=color_palette()[0],
        ax=ax,
    )
    ax.set_ylim((0, 1))
    ax.set_title(
        "Submission acceptance/revision rate over time (accept, minor revision, major revision)"
    )


async def revision() -> DataFrame:
    df = format_sort_track(
        DataFrame(await get_data(statement(Revision))).rename(
            columns={0: "Track", 1: "Status", 2: "Count"}
        ),
        "Track",
        True,
    )
    total = df.groupby("Track").sum().rename(columns={"Count": "Total"})
    accepted = (
        df[df["Status"] == "Accept"]
        .groupby("Track")
        .sum()
        .rename(columns={"Count": "Accepted"})
    )
    df = total.join(accepted)
    df["Acceptance Rate"] = df["Accepted"] / df["Total"]
    return df[["Acceptance Rate"]].reset_index()


def plot_revision(df: DataFrame, ax: Axes) -> None:
    barplot(
        x="Track",
        y="Acceptance Rate",
        data=df,
        color=color_palette()[0],
        ax=ax,
    )
    ax.set_ylim((0, 1))
    ax.set_title("Revision acceptance rate over time (minor and major revisions)")


async def main() -> Tuple[DataFrame, DataFrame]:
    return await gather(submission(), revision())


if __name__ == "__main__":
    install()
    s_df, r_df = run(main())
    print(s_df, r_df, sep="\n")
    test_plot_df(s_df, plot_submission)
    plt.savefig("plots/01_02_submission.png")
    test_plot_df(r_df, plot_revision)
    plt.savefig("plots/01_02_revision.png")
