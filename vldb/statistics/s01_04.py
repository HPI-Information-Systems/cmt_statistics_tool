"""Reviewers and ratings: Fraction of accepted or to be revised Papers per Paper Category"""
from asyncio import gather, run
from typing import Tuple

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from pandas import DataFrame
from sqlalchemy import func
from sqlalchemy.future import select
from uvloop import install

from vldb.statistics import get_data, test_plot_df
from vldb.tables import Revision, Submission


async def submission() -> DataFrame:
    statement = (
        select(Submission.category, func.count())
        .where(Submission.status.in_(["Accept", "Minor revision", "Major revision"]))  # type: ignore
        .group_by(Submission.category)
        .order_by(Submission.category)
    )
    df = DataFrame(await get_data(statement))
    df.rename(columns={0: "Category", 1: "Fraction"}, inplace=True)
    df["Category"].replace(
        "Experiments, Analysis & Benchmark",
        "Experiments, Analysis\n& Benchmark",
        inplace=True,
    )
    return df


def plot_submission(df: DataFrame, ax: Axes) -> None:
    df = df.sort_values("Fraction", ascending=False)
    ax.set_ylim((0, 1))
    ax.pie(
        df["Fraction"],
        labels=df["Category"] + "\n" + df["Fraction"].astype(str),
        autopct="%1.1f%%",
        # wedgeprops={"width": 1 / 2},
    )
    ax.axis("equal")
    ax.set_title("Fraction of accepted or to be revised submissions per category")


async def revision() -> DataFrame:
    statement = (
        select(Revision.category, func.count())
        .where(Revision.status == "Accept")
        .group_by(Revision.category)
        .order_by(Revision.category)
    )
    df = DataFrame(await get_data(statement))
    df.rename(columns={0: "Category", 1: "Fraction"}, inplace=True)
    df["Category"].replace(
        "Experiments, Analysis & Benchmark",
        "Experiments, Analysis\n& Benchmark",
        inplace=True,
    )
    return df


def plot_revision(df: DataFrame, ax: Axes) -> None:
    df = df.sort_values("Fraction", ascending=False)
    ax.set_ylim((0, 1))
    ax.pie(
        df["Fraction"],
        labels=df["Category"] + "\n" + df["Fraction"].astype(str),
        autopct="%1.1f%%",
        # wedgeprops={"width": 1 / 2},
    )
    ax.axis("equal")
    ax.set_title("Fraction of accepted revisions per category")


async def both() -> DataFrame:
    statement = (
        select(Submission.category, func.count())
        .where(Submission.status == "Accept")
        .group_by(Submission.category)
        .order_by(Submission.category)
    ).union_all(
        select(Revision.category, func.count())
        .where(Revision.status == "Accept")
        .group_by(Revision.category)
        .order_by(Revision.category)
    )
    df = DataFrame(await get_data(statement))
    df.rename(columns={0: "Category", 1: "Fraction"}, inplace=True)
    df = df.groupby("Category").sum().reset_index()
    df["Category"].replace(
        "Experiments, Analysis & Benchmark",
        "Experiments, Analysis\n& Benchmark",
        inplace=True,
    )
    return df


def plot_both(df: DataFrame, ax: Axes) -> None:
    df = df.sort_values("Fraction", ascending=False)
    ax.set_ylim((0, 1))
    ax.pie(
        df["Fraction"],
        labels=df["Category"] + "\n" + df["Fraction"].astype(str),
        autopct="%1.1f%%",
        # wedgeprops={"width": 1 / 2},
    )
    ax.axis("equal")
    ax.set_title("Fraction of ultimately accepted papers per category")


async def main() -> Tuple[DataFrame, DataFrame, DataFrame]:
    return await gather(submission(), revision(), both())


if __name__ == "__main__":
    install()
    s_df, r_df, b_df = run(main())
    test_plot_df(s_df, plot_submission)
    plt.savefig("plots/01_04_submission.png")
    test_plot_df(r_df, plot_revision)
    plt.savefig("plots/01_04_revision.png")
    test_plot_df(b_df, plot_both)
    plt.savefig("plots/01_04_both.png")
    print(s_df, r_df, b_df, sep="\n")
