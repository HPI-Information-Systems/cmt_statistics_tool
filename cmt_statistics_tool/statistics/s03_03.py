"""Other: Number of accepted papers per email domain"""
from asyncio import run

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from pandas import DataFrame
from seaborn import barplot, color_palette
from sqlalchemy import func
from sqlalchemy.future import select
from uvloop import install

from cmt_statistics_tool.statistics import get_data, test_plot_df
from cmt_statistics_tool.tables import Revision, Submission
from cmt_statistics_tool.tables.people import People


async def both() -> DataFrame:
    statement = (
        select(func.lower(func.split_part(People.email, "@", 2)))
        .join_from(Submission, People, onclause=Submission.primary_author)
        .where(Submission.status == "Accept")
        .union_all(
            select(func.lower(func.split_part(People.email, "@", 2)))
            .join_from(Revision, People, onclause=Revision.primary_author)
            .where(Revision.status == "Accept")
        )
    )
    df = DataFrame(await get_data(statement))
    df["Count"] = 1
    return df.groupby(0).sum().reset_index().rename(columns={0: "Email domain"})


def plot_both(df: DataFrame, ax: Axes) -> None:
    top = 20
    df = df.sort_values(["Count", "Email domain"], ascending=[False, True])
    df = df.head(top)
    order = df["Email domain"]
    barplot(
        y="Email domain",
        x="Count",
        data=df,
        order=order,
        color=color_palette()[0],
        ax=ax,
    )
    ax.set_title(
        f"Number of accepted papers per primary contact email domain (top {top})"
    )


async def main() -> DataFrame:
    return await both()


if __name__ == "__main__":
    install()
    b_df = run(main())
    print(b_df, sep="\n")
    test_plot_df(b_df, plot_both)
    plt.savefig("plots/03_03_both.png")
