"""Reviewers and ratings: Expertise Level vs Rating"""
from asyncio import run

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from pandas import DataFrame
from seaborn import barplot
from sqlalchemy import func
from sqlalchemy.future import select
from uvloop import install

from vldb.statistics import get_data, test_plot_df
from vldb.tables import SubmissionReview


async def main() -> DataFrame:
    statement = (
        select(
            SubmissionReview.overall_rating, SubmissionReview.confidence, func.count()
        )
        .group_by(SubmissionReview.overall_rating, SubmissionReview.confidence)
        .order_by(SubmissionReview.overall_rating, SubmissionReview.confidence)
    )
    df = DataFrame(await get_data(statement)).rename(
        columns={0: "Status", 1: "Expertise", 2: "Count"}
    )
    df2 = df.groupby("Expertise").sum().reset_index()
    df2.insert(0, "Status", "All")
    return df.append(df2)


def plot(df: DataFrame, ax: Axes) -> None:
    ax.set_title("Expertise level and rating (original submissions)")
    barplot(
        x="Status",
        y="Count",
        hue="Expertise",
        order=["Accept", "Weak Accept", "Weak Reject", "Reject", "All"],
        hue_order=[
            "Expert in this problem",
            "Knowledgeable in this sub-area ",
            "Generally aware of the area",
            "Had to use common sense and general knowledge",
        ],
        data=df,
        ax=ax,
    )


if __name__ == "__main__":
    install()
    df = run(main())
    fig = test_plot_df(df, plot)
    plt.savefig("plots/01_01.png")
    print(df)
