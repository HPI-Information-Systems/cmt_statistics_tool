"""Reviewers and ratings: Number of Submissions/Revisions over time"""
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
        select(paper.track_name, func.count())
        .group_by(paper.track_name)
        .order_by(paper.track_name)
    )


async def submission() -> DataFrame:
    df = DataFrame(await get_data(statement(Submission))).rename(
        columns={0: "Track", 1: "Count"}
    )
    return format_sort_track(df, "Track")


def plot_submission(df: DataFrame, ax: Axes) -> None:
    barplot(x="Track", y="Count", data=df, color=color_palette()[0], ax=ax)
    ax.set_title("Number of submissions over time")


async def revision() -> DataFrame:
    df = DataFrame(await get_data(statement(Revision))).rename(
        columns={0: "Track", 1: "Count"}
    )
    return format_sort_track(df, "Track", True)


def plot_revision(df: DataFrame, ax: Axes) -> None:
    barplot(x="Track", y="Count", data=df, color=color_palette()[0], ax=ax)
    ax.set_title("Number of revisions over time")


def plot_both(df: DataFrame, ax: Axes) -> None:
    barplot(x="Track", y="Count", hue="Type", data=df, ax=ax)
    ax.set_title("Number of papers over time")


async def main() -> Tuple[DataFrame, DataFrame]:
    return await gather(submission(), revision())


if __name__ == "__main__":
    install()
    s_df, r_df = run(main())
    test_plot_df(s_df, plot_submission)
    plt.savefig("plots/01_03_submission.png")
    test_plot_df(r_df, plot_revision)
    plt.savefig("plots/01_03_revision.png")
    print(s_df, r_df, sep="\n")
    test_plot_df(
        s_df.set_index("Track")
        .rename(columns={"Count": "Original Submission"})
        .join(
            r_df.set_index("Track").rename(columns={"Count": "Revision"}), how="outer"
        )
        .fillna(0)
        .astype(int)
        .reset_index()
        .melt(id_vars=["Track"], var_name="Type", value_name="Count"),
        plot_both,
    )
    plt.savefig("plots/01_03_both.png")
